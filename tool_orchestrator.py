import asyncio
import httpx
import logging
from typing import Dict, List, Optional, Any, TypedDict
from langgraph.graph import StateGraph, END
from models import (
    ConversationContext, EducationalIntent, ToolRequest, ToolResponse,
    OrchestratorResponse, UserInfo
)
from context_analyzer import ContextAnalyzer
from parameter_extractor import ParameterExtractor

logger = logging.getLogger(__name__)

class OrchestratorState(TypedDict):
    """State for the LangGraph orchestration workflow."""
    conversation_context: ConversationContext
    educational_intent: Optional[EducationalIntent]
    extracted_parameters: Dict[str, Any]
    tool_request: Optional[ToolRequest]
    tool_response: Optional[ToolResponse]
    orchestrator_response: Optional[OrchestratorResponse]
    error_message: Optional[str]
    workflow_step: str

class ToolOrchestrator:
    """
    Main orchestration layer using LangGraph for managing tool workflows.
    Handles the complete flow from conversation analysis to tool execution.
    """
    
    def __init__(self, openai_api_key: str, config: Dict[str, str]):
        self.config = config
        self.context_analyzer = ContextAnalyzer(openai_api_key)
        self.parameter_extractor = ParameterExtractor(openai_api_key)
        self.tool_endpoints = {
            "note_maker": config.get("NOTE_MAKER_URL", "http://localhost:8001"),
            "flashcard_generator": config.get("FLASHCARD_GENERATOR_URL", "http://localhost:8002"),
            "concept_explainer": config.get("CONCEPT_EXPLAINER_URL", "http://localhost:8003")
        }
        
        # Build the LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for orchestration."""
        workflow = StateGraph(OrchestratorState)
        
        # Add nodes
        workflow.add_node("analyze_context", self._analyze_context_node)
        workflow.add_node("extract_parameters", self._extract_parameters_node)
        workflow.add_node("validate_request", self._validate_request_node)
        workflow.add_node("execute_tool", self._execute_tool_node)
        workflow.add_node("format_response", self._format_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Add edges
        workflow.add_edge("analyze_context", "extract_parameters")
        workflow.add_edge("extract_parameters", "validate_request")
        workflow.add_conditional_edges(
            "validate_request",
            self._should_execute_tool,
            {
                "execute": "execute_tool",
                "error": "handle_error"
            }
        )
        workflow.add_edge("execute_tool", "format_response")
        workflow.add_edge("format_response", END)
        workflow.add_edge("handle_error", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_context")
        
        return workflow.compile()
    
    async def orchestrate(self, context: ConversationContext) -> OrchestratorResponse:
        """
        Main orchestration method that runs the complete workflow.
        """
        try:
            # Initialize state
            initial_state: OrchestratorState = {
                "conversation_context": context,
                "educational_intent": None,
                "extracted_parameters": {},
                "tool_request": None,
                "tool_response": None,
                "orchestrator_response": None,
                "error_message": None,
                "workflow_step": "start"
            }
            
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            return final_state.get("orchestrator_response", OrchestratorResponse(
                success=False,
                error_message="Workflow execution failed"
            ))
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return OrchestratorResponse(
                success=False,
                error_message=f"Orchestration error: {str(e)}"
            )
    
    async def _analyze_context_node(self, state: OrchestratorState) -> OrchestratorState:
        """Analyze conversation context to determine educational intent."""
        try:
            context = state["conversation_context"]
            intent = self.context_analyzer.analyze_context(context)
            
            state["educational_intent"] = intent
            state["workflow_step"] = "context_analyzed"
            
            logger.info(f"Context analyzed: {intent.intent_type} (confidence: {intent.confidence})")
            
        except Exception as e:
            logger.error(f"Context analysis failed: {e}")
            state["error_message"] = f"Context analysis failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    async def _extract_parameters_node(self, state: OrchestratorState) -> OrchestratorState:
        """Extract parameters for the identified tool."""
        try:
            intent = state["educational_intent"]
            context = state["conversation_context"]
            
            if not intent:
                state["error_message"] = "No educational intent identified"
                state["workflow_step"] = "error"
                return state
            
            # Extract parameters
            extraction_result = self.parameter_extractor.extract_parameters(intent, context)
            
            if extraction_result.success:
                state["extracted_parameters"] = extraction_result.extracted_parameters
                state["workflow_step"] = "parameters_extracted"
                
                logger.info(f"Parameters extracted: {list(extraction_result.extracted_parameters.keys())}")
            else:
                # Try to fill missing parameters
                filled_params = self.parameter_extractor.fill_missing_parameters(
                    extraction_result.missing_parameters,
                    context,
                    intent.suggested_tool
                )
                
                state["extracted_parameters"] = {
                    **extraction_result.extracted_parameters,
                    **filled_params
                }
                state["workflow_step"] = "parameters_filled"
                
                logger.info(f"Missing parameters filled: {extraction_result.missing_parameters}")
            
        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            state["error_message"] = f"Parameter extraction failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    async def _validate_request_node(self, state: OrchestratorState) -> OrchestratorState:
        """Validate the tool request before execution."""
        try:
            intent = state["educational_intent"]
            params = state["extracted_parameters"]
            context = state["conversation_context"]
            
            if not intent or not params:
                state["error_message"] = "Missing intent or parameters"
                state["workflow_step"] = "error"
                return state
            
            # Create tool request
            tool_request = ToolRequest(
                tool_name=intent.suggested_tool,
                parameters=params,
                user_info=context.user_info,
                chat_history=context.chat_history
            )
            
            state["tool_request"] = tool_request
            state["workflow_step"] = "request_validated"
            
            logger.info(f"Tool request validated: {tool_request.tool_name}")
            
        except Exception as e:
            logger.error(f"Request validation failed: {e}")
            state["error_message"] = f"Request validation failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _should_execute_tool(self, state: OrchestratorState) -> str:
        """Determine if tool should be executed or if there's an error."""
        if state["workflow_step"] == "error":
            return "error"
        return "execute"
    
    async def _execute_tool_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute the educational tool."""
        try:
            tool_request = state["tool_request"]
            
            if not tool_request:
                state["error_message"] = "No tool request to execute"
                state["workflow_step"] = "error"
                return state
            
            # Execute the tool
            tool_response = await self._call_educational_tool(tool_request)
            
            state["tool_response"] = tool_response
            state["workflow_step"] = "tool_executed"
            
            logger.info(f"Tool executed: {tool_request.tool_name} - Success: {tool_response.success}")
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            state["tool_response"] = ToolResponse(
                success=False,
                error=f"Tool execution failed: {str(e)}",
                error_code="EXECUTION_ERROR"
            )
            state["workflow_step"] = "tool_executed"
        
        return state
    
    async def _format_response_node(self, state: OrchestratorState) -> OrchestratorState:
        """Format the final orchestrator response."""
        try:
            tool_response = state["tool_response"]
            intent = state["educational_intent"]
            context = state["conversation_context"]
            
            orchestrator_response = OrchestratorResponse(
                success=tool_response.success if tool_response else False,
                tool_response=tool_response,
                educational_intent=intent,
                conversation_context=context,
                error_message=tool_response.error if tool_response and not tool_response.success else None
            )
            
            state["orchestrator_response"] = orchestrator_response
            state["workflow_step"] = "response_formatted"
            
            logger.info(f"Response formatted - Success: {orchestrator_response.success}")
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            state["orchestrator_response"] = OrchestratorResponse(
                success=False,
                error_message=f"Response formatting failed: {str(e)}"
            )
            state["workflow_step"] = "error"
        
        return state
    
    async def _handle_error_node(self, state: OrchestratorState) -> OrchestratorState:
        """Handle errors in the workflow."""
        error_message = state.get("error_message", "Unknown error occurred")
        
        orchestrator_response = OrchestratorResponse(
            success=False,
            error_message=error_message,
            educational_intent=state.get("educational_intent"),
            conversation_context=state.get("conversation_context")
        )
        
        state["orchestrator_response"] = orchestrator_response
        state["workflow_step"] = "error_handled"
        
        logger.error(f"Error handled: {error_message}")
        
        return state
    
    async def _call_educational_tool(self, tool_request: ToolRequest) -> ToolResponse:
        """Make HTTP call to the educational tool."""
        tool_name = tool_request.tool_name
        endpoint = self.tool_endpoints.get(tool_name)
        
        if not endpoint:
            return ToolResponse(
                success=False,
                error=f"Unknown tool: {tool_name}",
                error_code="UNKNOWN_TOOL"
            )
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{endpoint}/generate",
                    json=tool_request.dict(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return ToolResponse(
                        success=True,
                        data=data
                    )
                else:
                    error_data = response.json() if response.content else {}
                    return ToolResponse(
                        success=False,
                        error=error_data.get("error", f"HTTP {response.status_code}"),
                        error_code=error_data.get("error_code", "HTTP_ERROR")
                    )
                    
        except httpx.TimeoutException:
            return ToolResponse(
                success=False,
                error="Tool request timed out",
                error_code="TIMEOUT"
            )
        except httpx.ConnectError:
            return ToolResponse(
                success=False,
                error=f"Could not connect to {tool_name} service",
                error_code="CONNECTION_ERROR"
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                error=f"Tool call failed: {str(e)}",
                error_code="CALL_ERROR"
            )
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status and statistics."""
        return {
            "workflow_nodes": [
                "analyze_context",
                "extract_parameters", 
                "validate_request",
                "execute_tool",
                "format_response",
                "handle_error"
            ],
            "tool_endpoints": self.tool_endpoints,
            "status": "active"
        }
