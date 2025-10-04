import json
import logging
from typing import Dict, List, Optional, Any
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from pydantic import BaseModel, Field
from models import ConversationContext, EducationalIntent, UserInfo

logger = logging.getLogger(__name__)

class ParameterExtractionResult(BaseModel):
    """Result of parameter extraction process."""
    success: bool
    extracted_parameters: Dict[str, Any]
    missing_parameters: List[str]
    confidence_scores: Dict[str, float]
    extraction_method: str

class ParameterExtractor:
    """
    Advanced parameter extraction system using LangChain and LLM capabilities.
    Handles intelligent inference and validation of tool parameters.
    """
    
    def __init__(self, openai_api_key: str):
        self.llm = OpenAI(openai_api_key=openai_api_key, temperature=0.1)
        self.tool_schemas = self._initialize_tool_schemas()
        
    def _initialize_tool_schemas(self) -> Dict[str, Dict]:
        """Initialize schemas for different educational tools."""
        return {
            "note_maker": {
                "required": ["user_info", "chat_history", "topic", "subject", "note_taking_style"],
                "optional": ["include_examples", "include_analogies"],
                "parameter_descriptions": {
                    "topic": "The main topic for note generation",
                    "subject": "Academic subject area",
                    "note_taking_style": "Preferred format: outline, bullet_points, narrative, structured",
                    "include_examples": "Boolean flag to include practical examples",
                    "include_analogies": "Boolean flag to include explanatory analogies"
                }
            },
            "flashcard_generator": {
                "required": ["user_info", "topic", "count", "difficulty", "subject"],
                "optional": ["include_examples"],
                "parameter_descriptions": {
                    "topic": "Topic for flashcard generation",
                    "count": "Number of flashcards (1-20)",
                    "difficulty": "Difficulty level: easy, medium, hard",
                    "subject": "Academic discipline",
                    "include_examples": "Boolean flag to include examples"
                }
            },
            "concept_explainer": {
                "required": ["user_info", "chat_history", "concept_to_explain", "current_topic", "desired_depth"],
                "optional": [],
                "parameter_descriptions": {
                    "concept_to_explain": "Specific concept to explain",
                    "current_topic": "Broader subject context",
                    "desired_depth": "Detail level: basic, intermediate, advanced, comprehensive"
                }
            }
        }
    
    def extract_parameters(
        self, 
        intent: EducationalIntent, 
        context: ConversationContext
    ) -> ParameterExtractionResult:
        """
        Extract and validate parameters for the identified tool.
        """
        try:
            tool_name = intent.suggested_tool
            if tool_name not in self.tool_schemas:
                return ParameterExtractionResult(
                    success=False,
                    extracted_parameters={},
                    missing_parameters=[],
                    confidence_scores={},
                    extraction_method="error"
                )
            
            # Extract parameters using multiple methods
            extracted_params = self._extract_with_multiple_methods(
                intent, context, tool_name
            )
            
            # Validate extracted parameters
            validated_params, missing_params = self._validate_parameters(
                extracted_params, tool_name
            )
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(
                validated_params, context
            )
            
            return ParameterExtractionResult(
                success=len(missing_params) == 0,
                extracted_parameters=validated_params,
                missing_parameters=missing_params,
                confidence_scores=confidence_scores,
                extraction_method="hybrid"
            )
            
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
            return ParameterExtractionResult(
                success=False,
                extracted_parameters={},
                missing_parameters=[],
                confidence_scores={},
                extraction_method="error"
            )
    
    def _extract_with_multiple_methods(
        self, 
        intent: EducationalIntent, 
        context: ConversationContext,
        tool_name: str
    ) -> Dict[str, Any]:
        """Extract parameters using multiple extraction methods."""
        params = {}
        
        # Method 1: Use existing extracted parameters from context analyzer
        params.update(intent.extracted_parameters)
        
        # Method 2: LLM-based extraction for missing parameters
        llm_params = self._llm_parameter_extraction(context, tool_name)
        params.update(llm_params)
        
        # Method 3: Context-based inference
        inferred_params = self._infer_from_context(context, tool_name)
        params.update(inferred_params)
        
        # Method 4: Default value assignment
        default_params = self._assign_default_values(tool_name, context)
        for key, value in default_params.items():
            if key not in params:
                params[key] = value
        
        return params
    
    def _llm_parameter_extraction(
        self, 
        context: ConversationContext, 
        tool_name: str
    ) -> Dict[str, Any]:
        """Use LLM to extract parameters from conversation context."""
        schema = self.tool_schemas[tool_name]
        
        prompt = PromptTemplate(
            input_variables=["conversation", "tool_schema"],
            template="""
            Extract parameters for the {tool_name} tool from the following conversation.
            
            Conversation:
            {conversation}
            
            Tool Schema:
            {tool_schema}
            
            Extract only the parameters that are clearly mentioned or can be reasonably inferred.
            Return as JSON format.
            """
        )
        
        conversation_text = self._format_conversation(context)
        schema_text = json.dumps(schema, indent=2)
        
        try:
            response = self.llm(prompt.format(
                conversation=conversation_text,
                tool_schema=schema_text
            ))
            
            # Parse LLM response
            extracted = json.loads(response.strip())
            return extracted
            
        except Exception as e:
            logger.error(f"LLM parameter extraction failed: {e}")
            return {}
    
    def _infer_from_context(
        self, 
        context: ConversationContext, 
        tool_name: str
    ) -> Dict[str, Any]:
        """Infer parameters from user context and preferences."""
        params = {}
        
        # Always include user_info and chat_history
        params["user_info"] = context.user_info.dict()
        params["chat_history"] = [msg.dict() for msg in context.chat_history]
        
        # Infer parameters based on user profile
        if tool_name == "note_maker":
            params.update(self._infer_note_maker_params(context))
        elif tool_name == "flashcard_generator":
            params.update(self._infer_flashcard_params(context))
        elif tool_name == "concept_explainer":
            params.update(self._infer_concept_explainer_params(context))
        
        return params
    
    def _infer_note_maker_params(self, context: ConversationContext) -> Dict[str, Any]:
        """Infer parameters specific to note maker tool."""
        params = {}
        
        # Infer note-taking style from learning style
        learning_style = context.user_info.learning_style_summary.lower()
        if "outline" in learning_style:
            params["note_taking_style"] = "outline"
        elif "bullet" in learning_style:
            params["note_taking_style"] = "bullet_points"
        elif "narrative" in learning_style:
            params["note_taking_style"] = "narrative"
        else:
            params["note_taking_style"] = "structured"
        
        # Infer inclusion flags based on teaching style
        if context.teaching_style == "visual":
            params["include_examples"] = True
            params["include_analogies"] = True
        elif context.teaching_style == "direct":
            params["include_examples"] = True
            params["include_analogies"] = False
        else:
            params["include_examples"] = True
            params["include_analogies"] = False
        
        return params
    
    def _infer_flashcard_params(self, context: ConversationContext) -> Dict[str, Any]:
        """Infer parameters specific to flashcard generator tool."""
        params = {}
        
        # Infer count based on mastery level
        if context.mastery_level:
            if context.mastery_level <= 3:
                params["count"] = 5
            elif context.mastery_level <= 6:
                params["count"] = 10
            else:
                params["count"] = 15
        else:
            params["count"] = 10
        
        # Infer difficulty based on emotional state and mastery level
        if context.emotional_state == "confused" or context.emotional_state == "anxious":
            params["difficulty"] = "easy"
        elif context.emotional_state == "focused" and context.mastery_level and context.mastery_level >= 7:
            params["difficulty"] = "hard"
        else:
            params["difficulty"] = "medium"
        
        # Infer inclusion flags
        params["include_examples"] = True
        
        return params
    
    def _infer_concept_explainer_params(self, context: ConversationContext) -> Dict[str, Any]:
        """Infer parameters specific to concept explainer tool."""
        params = {}
        
        # Infer explanation depth
        if context.emotional_state == "confused" or context.emotional_state == "anxious":
            params["desired_depth"] = "basic"
        elif context.mastery_level:
            if context.mastery_level <= 3:
                params["desired_depth"] = "basic"
            elif context.mastery_level <= 6:
                params["desired_depth"] = "intermediate"
            elif context.mastery_level <= 8:
                params["desired_depth"] = "advanced"
            else:
                params["desired_depth"] = "comprehensive"
        else:
            params["desired_depth"] = "intermediate"
        
        return params
    
    def _assign_default_values(
        self, 
        tool_name: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Assign default values for missing parameters."""
        defaults = {
            "note_maker": {
                "include_examples": True,
                "include_analogies": False
            },
            "flashcard_generator": {
                "count": 10,
                "include_examples": True
            },
            "concept_explainer": {}
        }
        
        return defaults.get(tool_name, {})
    
    def _validate_parameters(
        self, 
        params: Dict[str, Any], 
        tool_name: str
    ) -> tuple[Dict[str, Any], List[str]]:
        """Validate parameters against tool schema."""
        schema = self.tool_schemas[tool_name]
        validated_params = {}
        missing_params = []
        
        # Check required parameters
        for param in schema["required"]:
            if param in params and params[param] is not None:
                validated_params[param] = params[param]
            else:
                missing_params.append(param)
        
        # Add optional parameters if present
        for param in schema["optional"]:
            if param in params:
                validated_params[param] = params[param]
        
        return validated_params, missing_params
    
    def _calculate_confidence_scores(
        self, 
        params: Dict[str, Any], 
        context: ConversationContext
    ) -> Dict[str, float]:
        """Calculate confidence scores for extracted parameters."""
        scores = {}
        
        for param, value in params.items():
            if param == "user_info" or param == "chat_history":
                scores[param] = 1.0  # Always available
            elif param in ["topic", "subject"]:
                # Higher confidence if explicitly mentioned
                scores[param] = 0.9 if value else 0.3
            elif param in ["difficulty", "note_taking_style", "desired_depth"]:
                # Medium confidence for inferred values
                scores[param] = 0.7
            elif param in ["count", "include_examples", "include_analogies"]:
                # Lower confidence for default values
                scores[param] = 0.5
            else:
                scores[param] = 0.6
        
        return scores
    
    def _format_conversation(self, context: ConversationContext) -> str:
        """Format conversation for LLM processing."""
        conversation_parts = []
        
        # Add chat history
        for msg in context.chat_history:
            conversation_parts.append(f"{msg.role.value}: {msg.content}")
        
        # Add current message
        conversation_parts.append(f"user: {context.current_message}")
        
        return "\n".join(conversation_parts)
    
    def fill_missing_parameters(
        self, 
        missing_params: List[str], 
        context: ConversationContext,
        tool_name: str
    ) -> Dict[str, Any]:
        """Fill missing parameters by asking targeted questions or using defaults."""
        filled_params = {}
        
        for param in missing_params:
            if param in ["topic", "subject"]:
                # These are critical parameters that should be asked
                filled_params[param] = self._ask_for_parameter(param, context)
            else:
                # Use intelligent defaults
                filled_params[param] = self._get_intelligent_default(param, context, tool_name)
        
        return filled_params
    
    def _ask_for_parameter(self, param: str, context: ConversationContext) -> str:
        """Generate a question to ask for missing parameter."""
        questions = {
            "topic": f"What specific topic would you like to focus on, {context.user_info.name}?",
            "subject": f"What subject area is this related to, {context.user_info.name}?"
        }
        
        return questions.get(param, f"Please specify {param}")
    
    def _get_intelligent_default(
        self, 
        param: str, 
        context: ConversationContext, 
        tool_name: str
    ) -> Any:
        """Get intelligent default value for parameter."""
        defaults = {
            "note_taking_style": "structured",
            "difficulty": "medium",
            "count": 10,
            "desired_depth": "intermediate",
            "include_examples": True,
            "include_analogies": False
        }
        
        return defaults.get(param, None)
