from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn
from typing import Dict, Any

from config import Config
from models import (
    ConversationContext, OrchestratorResponse, UserInfo, ChatMessage,
    TeachingStyle, EmotionalState
)
from tool_orchestrator import ToolOrchestrator
from schema_validator import SchemaValidator

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Global variables
orchestrator: ToolOrchestrator = None
validator: SchemaValidator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator, validator
    
    # Startup
    logger.info("Starting AI Tutor Orchestrator...")
    
    try:
        # Initialize components
        validator = SchemaValidator()
        config_dict = {
            "NOTE_MAKER_URL": Config.NOTE_MAKER_URL,
            "FLASHCARD_GENERATOR_URL": Config.FLASHCARD_GENERATOR_URL,
            "CONCEPT_EXPLAINER_URL": Config.CONCEPT_EXPLAINER_URL
        }
        orchestrator = ToolOrchestrator(Config.OPENAI_API_KEY, config_dict)
        
        logger.info("AI Tutor Orchestrator started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start AI Tutor Orchestrator: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down AI Tutor Orchestrator...")

# Create FastAPI app
app = FastAPI(
    title="AI Tutor Orchestrator",
    description="Intelligent middleware orchestrator for autonomous AI tutoring systems",
    version=Config.APP_VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get orchestrator
async def get_orchestrator() -> ToolOrchestrator:
    if orchestrator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orchestrator not initialized"
        )
    return orchestrator

# Dependency to get validator
async def get_validator() -> SchemaValidator:
    if validator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Validator not initialized"
        )
    return validator

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": Config.APP_NAME,
        "version": Config.APP_VERSION,
        "status": "active",
        "description": "AI Tutor Orchestrator - Intelligent middleware for educational tools"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": Config.APP_VERSION
    }

@app.get("/status")
async def get_status():
    """Get orchestrator status and workflow information."""
    try:
        orchestrator_instance = await get_orchestrator()
        workflow_status = orchestrator_instance.get_workflow_status()
        
        return {
            "status": "active",
            "workflow": workflow_status,
            "tools_available": list(workflow_status["tool_endpoints"].keys()),
            "version": Config.APP_VERSION
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )

@app.post("/orchestrate", response_model=OrchestratorResponse)
async def orchestrate_request(
    context: ConversationContext,
    orchestrator_instance: ToolOrchestrator = Depends(get_orchestrator),
    validator_instance: SchemaValidator = Depends(get_validator)
):
    """
    Main orchestration endpoint that processes conversation context
    and executes appropriate educational tools.
    """
    try:
        logger.info(f"Processing orchestration request for user: {context.user_info.user_id}")
        
        # Validate input context
        validation_result = validator_instance.validate_tool_request(
            type('ToolRequest', (), {
                'tool_name': 'unknown',  # Will be determined by orchestrator
                'parameters': context.dict(),
                'user_info': context.user_info,
                'chat_history': context.chat_history
            })()
        )
        
        if not validation_result.is_valid:
            logger.warning(f"Input validation failed: {validation_result.errors}")
            return OrchestratorResponse(
                success=False,
                error_message=f"Input validation failed: {validation_result.errors[0]['message']}"
            )
        
        # Execute orchestration workflow
        response = await orchestrator_instance.orchestrate(context)
        
        logger.info(f"Orchestration completed - Success: {response.success}")
        return response
        
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failed: {str(e)}"
        )

@app.post("/analyze-context")
async def analyze_context(
    context: ConversationContext,
    orchestrator_instance: ToolOrchestrator = Depends(get_orchestrator)
):
    """
    Analyze conversation context to determine educational intent
    without executing tools.
    """
    try:
        logger.info(f"Analyzing context for user: {context.user_info.user_id}")
        
        # Use context analyzer directly
        intent = orchestrator_instance.context_analyzer.analyze_context(context)
        
        return {
            "success": True,
            "educational_intent": intent.dict(),
            "analysis_timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Context analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context analysis failed: {str(e)}"
        )

@app.post("/extract-parameters")
async def extract_parameters(
    context: ConversationContext,
    orchestrator_instance: ToolOrchestrator = Depends(get_orchestrator)
):
    """
    Extract parameters from conversation context for a specific tool.
    """
    try:
        logger.info(f"Extracting parameters for user: {context.user_info.user_id}")
        
        # Analyze context first
        intent = orchestrator_instance.context_analyzer.analyze_context(context)
        
        # Extract parameters
        extraction_result = orchestrator_instance.parameter_extractor.extract_parameters(
            intent, context
        )
        
        return {
            "success": extraction_result.success,
            "extracted_parameters": extraction_result.extracted_parameters,
            "missing_parameters": extraction_result.missing_parameters,
            "confidence_scores": extraction_result.confidence_scores,
            "extraction_method": extraction_result.extraction_method
        }
        
    except Exception as e:
        logger.error(f"Parameter extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parameter extraction failed: {str(e)}"
        )

@app.post("/validate-request")
async def validate_request(
    request_data: Dict[str, Any],
    validator_instance: SchemaValidator = Depends(get_validator)
):
    """
    Validate a tool request against its schema.
    """
    try:
        logger.info("Validating tool request")
        
        # Create a mock ToolRequest for validation
        tool_request = type('ToolRequest', (), {
            'tool_name': request_data.get('tool_name', 'unknown'),
            'parameters': request_data.get('parameters', {}),
            'user_info': request_data.get('user_info', {}),
            'chat_history': request_data.get('chat_history', [])
        })()
        
        validation_result = validator_instance.validate_tool_request(tool_request)
        
        return {
            "success": validation_result.is_valid,
            "validation_result": validation_result.dict(),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Request validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Request validation failed: {str(e)}"
        )

@app.get("/tools")
async def list_available_tools():
    """List all available educational tools."""
    return {
        "tools": [
            {
                "name": "note_maker",
                "description": "Generate structured notes for educational topics",
                "endpoint": Config.NOTE_MAKER_URL,
                "required_parameters": ["user_info", "chat_history", "topic", "subject", "note_taking_style"],
                "optional_parameters": ["include_examples", "include_analogies"]
            },
            {
                "name": "flashcard_generator",
                "description": "Create flashcards for memorization and practice",
                "endpoint": Config.FLASHCARD_GENERATOR_URL,
                "required_parameters": ["user_info", "topic", "count", "difficulty", "subject"],
                "optional_parameters": ["include_examples"]
            },
            {
                "name": "concept_explainer",
                "description": "Explain complex concepts with adaptive depth",
                "endpoint": Config.CONCEPT_EXPLAINER_URL,
                "required_parameters": ["user_info", "chat_history", "concept_to_explain", "current_topic", "desired_depth"],
                "optional_parameters": []
            }
        ],
        "total_tools": 3
    }

@app.get("/schemas/{tool_name}")
async def get_tool_schema(tool_name: str):
    """Get schema for a specific educational tool."""
    try:
        validator_instance = await get_validator()
        schema = validator_instance.tool_schemas.get(tool_name)
        
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schema not found for tool: {tool_name}"
            )
        
        return {
            "tool_name": tool_name,
            "schema": schema,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schema retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema retrieval failed: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "details": str(exc) if Config.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level=Config.LOG_LEVEL.lower()
    )
