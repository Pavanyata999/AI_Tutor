import json
import logging
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, ValidationError, Field, validator
from enum import Enum
from models import (
    UserInfo, ChatMessage, ToolRequest, ToolResponse,
    NoteTakingStyle, DifficultyLevel, ExplanationDepth, EmotionalState
)

logger = logging.getLogger(__name__)

class ValidationErrorType(str, Enum):
    """Types of validation errors."""
    MISSING_REQUIRED = "missing_required"
    INVALID_TYPE = "invalid_type"
    INVALID_VALUE = "invalid_value"
    CONSTRAINT_VIOLATION = "constraint_violation"
    SCHEMA_MISMATCH = "schema_mismatch"

class ValidationResult(BaseModel):
    """Result of validation process."""
    is_valid: bool
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validated_data: Optional[Dict[str, Any]] = None

class SchemaValidator:
    """
    Comprehensive schema validation system for educational tools.
    Handles validation of tool requests, responses, and data schemas.
    """
    
    def __init__(self):
        self.tool_schemas = self._initialize_tool_schemas()
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_tool_schemas(self) -> Dict[str, Dict]:
        """Initialize comprehensive schemas for all educational tools."""
        return {
            "note_maker": {
                "required_fields": [
                    "user_info", "chat_history", "topic", "subject", "note_taking_style"
                ],
                "optional_fields": ["include_examples", "include_analogies"],
                "field_types": {
                    "user_info": "object",
                    "chat_history": "array",
                    "topic": "string",
                    "subject": "string",
                    "note_taking_style": "enum",
                    "include_examples": "boolean",
                    "include_analogies": "boolean"
                },
                "constraints": {
                    "topic": {"min_length": 1, "max_length": 200},
                    "subject": {"min_length": 1, "max_length": 100},
                    "note_taking_style": {"enum_values": ["outline", "bullet_points", "narrative", "structured"]},
                    "include_examples": {"type": "boolean"},
                    "include_analogies": {"type": "boolean"}
                }
            },
            "flashcard_generator": {
                "required_fields": [
                    "user_info", "topic", "count", "difficulty", "subject"
                ],
                "optional_fields": ["include_examples"],
                "field_types": {
                    "user_info": "object",
                    "topic": "string",
                    "count": "integer",
                    "difficulty": "enum",
                    "subject": "string",
                    "include_examples": "boolean"
                },
                "constraints": {
                    "topic": {"min_length": 1, "max_length": 200},
                    "count": {"min": 1, "max": 20},
                    "difficulty": {"enum_values": ["easy", "medium", "hard"]},
                    "subject": {"min_length": 1, "max_length": 100},
                    "include_examples": {"type": "boolean"}
                }
            },
            "concept_explainer": {
                "required_fields": [
                    "user_info", "chat_history", "concept_to_explain", "current_topic", "desired_depth"
                ],
                "optional_fields": [],
                "field_types": {
                    "user_info": "object",
                    "chat_history": "array",
                    "concept_to_explain": "string",
                    "current_topic": "string",
                    "desired_depth": "enum"
                },
                "constraints": {
                    "concept_to_explain": {"min_length": 1, "max_length": 200},
                    "current_topic": {"min_length": 1, "max_length": 200},
                    "desired_depth": {"enum_values": ["basic", "intermediate", "advanced", "comprehensive"]}
                }
            }
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules and constraints."""
        return {
            "user_info": {
                "required_fields": ["user_id", "name", "grade_level", "learning_style_summary", 
                                  "emotional_state_summary", "mastery_level_summary"],
                "field_constraints": {
                    "user_id": {"type": "string", "min_length": 1},
                    "name": {"type": "string", "min_length": 1, "max_length": 100},
                    "grade_level": {"type": "string", "min_length": 1},
                    "learning_style_summary": {"type": "string", "min_length": 1, "max_length": 500},
                    "emotional_state_summary": {"type": "string", "min_length": 1, "max_length": 500},
                    "mastery_level_summary": {"type": "string", "min_length": 1, "max_length": 500}
                }
            },
            "chat_history": {
                "item_constraints": {
                    "role": {"type": "string", "enum": ["user", "assistant"]},
                    "content": {"type": "string", "min_length": 1, "max_length": 2000}
                },
                "array_constraints": {"min_length": 0, "max_length": 50}
            }
        }
    
    def validate_tool_request(self, tool_request: ToolRequest) -> ValidationResult:
        """Validate a tool request against its schema."""
        try:
            tool_name = tool_request.tool_name
            schema = self.tool_schemas.get(tool_name)
            
            if not schema:
                return ValidationResult(
                    is_valid=False,
                    errors=[{
                        "type": ValidationErrorType.SCHEMA_MISMATCH,
                        "field": "tool_name",
                        "message": f"Unknown tool: {tool_name}",
                        "code": "UNKNOWN_TOOL"
                    }]
                )
            
            errors = []
            warnings = []
            validated_data = {}
            
            # Validate required fields
            for field in schema["required_fields"]:
                if field not in tool_request.parameters:
                    errors.append({
                        "type": ValidationErrorType.MISSING_REQUIRED,
                        "field": field,
                        "message": f"Required field '{field}' is missing",
                        "code": "MISSING_REQUIRED"
                    })
                else:
                    field_validation = self._validate_field(
                        field, tool_request.parameters[field], schema
                    )
                    if field_validation["is_valid"]:
                        validated_data[field] = tool_request.parameters[field]
                    else:
                        errors.extend(field_validation["errors"])
            
            # Validate optional fields
            for field in schema["optional_fields"]:
                if field in tool_request.parameters:
                    field_validation = self._validate_field(
                        field, tool_request.parameters[field], schema
                    )
                    if field_validation["is_valid"]:
                        validated_data[field] = tool_request.parameters[field]
                    else:
                        errors.extend(field_validation["errors"])
            
            # Validate user_info specifically
            if "user_info" in tool_request.parameters:
                user_info_validation = self._validate_user_info(
                    tool_request.parameters["user_info"]
                )
                if not user_info_validation["is_valid"]:
                    errors.extend(user_info_validation["errors"])
            
            # Validate chat_history specifically
            if "chat_history" in tool_request.parameters:
                chat_history_validation = self._validate_chat_history(
                    tool_request.parameters["chat_history"]
                )
                if not chat_history_validation["is_valid"]:
                    errors.extend(chat_history_validation["errors"])
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                validated_data=validated_data if len(errors) == 0 else None
            )
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[{
                    "type": ValidationErrorType.SCHEMA_MISMATCH,
                    "field": "general",
                    "message": f"Validation failed: {str(e)}",
                    "code": "VALIDATION_ERROR"
                }]
            )
    
    def _validate_field(self, field_name: str, value: Any, schema: Dict) -> Dict[str, Any]:
        """Validate a specific field against its constraints."""
        errors = []
        
        if field_name not in schema["field_types"]:
            return {"is_valid": False, "errors": [{
                "type": ValidationErrorType.SCHEMA_MISMATCH,
                "field": field_name,
                "message": f"Field '{field_name}' not defined in schema",
                "code": "UNDEFINED_FIELD"
            }]}
        
        expected_type = schema["field_types"][field_name]
        constraints = schema["constraints"].get(field_name, {})
        
        # Type validation
        if not self._validate_type(value, expected_type):
            errors.append({
                "type": ValidationErrorType.INVALID_TYPE,
                "field": field_name,
                "message": f"Field '{field_name}' must be of type {expected_type}",
                "code": "INVALID_TYPE",
                "expected_type": expected_type,
                "actual_type": type(value).__name__
            })
        
        # Constraint validation
        constraint_errors = self._validate_constraints(value, constraints)
        errors.extend(constraint_errors)
        
        return {"is_valid": len(errors) == 0, "errors": errors}
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate that value matches expected type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "enum": str  # Enums are strings with specific values
        }
        
        if expected_type == "enum":
            return isinstance(value, str)
        
        expected_python_type = type_mapping.get(expected_type)
        if not expected_python_type:
            return False
        
        return isinstance(value, expected_python_type)
    
    def _validate_constraints(self, value: Any, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate value against specific constraints."""
        errors = []
        
        if isinstance(value, str):
            if "min_length" in constraints and len(value) < constraints["min_length"]:
                errors.append({
                    "type": ValidationErrorType.CONSTRAINT_VIOLATION,
                    "field": "string_length",
                    "message": f"String too short (minimum: {constraints['min_length']})",
                    "code": "MIN_LENGTH_VIOLATION"
                })
            
            if "max_length" in constraints and len(value) > constraints["max_length"]:
                errors.append({
                    "type": ValidationErrorType.CONSTRAINT_VIOLATION,
                    "field": "string_length",
                    "message": f"String too long (maximum: {constraints['max_length']})",
                    "code": "MAX_LENGTH_VIOLATION"
                })
            
            if "enum_values" in constraints and value not in constraints["enum_values"]:
                errors.append({
                    "type": ValidationErrorType.INVALID_VALUE,
                    "field": "enum_value",
                    "message": f"Invalid enum value. Must be one of: {constraints['enum_values']}",
                    "code": "INVALID_ENUM_VALUE"
                })
        
        elif isinstance(value, int):
            if "min" in constraints and value < constraints["min"]:
                errors.append({
                    "type": ValidationErrorType.CONSTRAINT_VIOLATION,
                    "field": "integer_value",
                    "message": f"Integer too small (minimum: {constraints['min']})",
                    "code": "MIN_VALUE_VIOLATION"
                })
            
            if "max" in constraints and value > constraints["max"]:
                errors.append({
                    "type": ValidationErrorType.CONSTRAINT_VIOLATION,
                    "field": "integer_value",
                    "message": f"Integer too large (maximum: {constraints['max']})",
                    "code": "MAX_VALUE_VIOLATION"
                })
        
        elif isinstance(value, bool):
            if "type" in constraints and constraints["type"] != "boolean":
                errors.append({
                    "type": ValidationErrorType.INVALID_TYPE,
                    "field": "boolean_value",
                    "message": "Value must be boolean",
                    "code": "INVALID_BOOLEAN_TYPE"
                })
        
        return errors
    
    def _validate_user_info(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user_info object specifically."""
        errors = []
        rules = self.validation_rules["user_info"]
        
        # Check required fields
        for field in rules["required_fields"]:
            if field not in user_info:
                errors.append({
                    "type": ValidationErrorType.MISSING_REQUIRED,
                    "field": f"user_info.{field}",
                    "message": f"Required field 'user_info.{field}' is missing",
                    "code": "MISSING_USER_INFO_FIELD"
                })
            else:
                constraints = rules["field_constraints"].get(field, {})
                constraint_errors = self._validate_constraints(user_info[field], constraints)
                errors.extend(constraint_errors)
        
        return {"is_valid": len(errors) == 0, "errors": errors}
    
    def _validate_chat_history(self, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate chat_history array specifically."""
        errors = []
        rules = self.validation_rules["chat_history"]
        
        # Validate array constraints
        if len(chat_history) < rules["array_constraints"]["min_length"]:
            errors.append({
                "type": ValidationErrorType.CONSTRAINT_VIOLATION,
                "field": "chat_history.length",
                "message": f"Chat history too short (minimum: {rules['array_constraints']['min_length']})",
                "code": "MIN_ARRAY_LENGTH_VIOLATION"
            })
        
        if len(chat_history) > rules["array_constraints"]["max_length"]:
            errors.append({
                "type": ValidationErrorType.CONSTRAINT_VIOLATION,
                "field": "chat_history.length",
                "message": f"Chat history too long (maximum: {rules['array_constraints']['max_length']})",
                "code": "MAX_ARRAY_LENGTH_VIOLATION"
            })
        
        # Validate each message
        for i, message in enumerate(chat_history):
            if not isinstance(message, dict):
                errors.append({
                    "type": ValidationErrorType.INVALID_TYPE,
                    "field": f"chat_history[{i}]",
                    "message": f"Message {i} must be an object",
                    "code": "INVALID_MESSAGE_TYPE"
                })
                continue
            
            # Validate role
            if "role" not in message:
                errors.append({
                    "type": ValidationErrorType.MISSING_REQUIRED,
                    "field": f"chat_history[{i}].role",
                    "message": f"Message {i} missing required 'role' field",
                    "code": "MISSING_ROLE"
                })
            else:
                role_constraints = rules["item_constraints"]["role"]
                constraint_errors = self._validate_constraints(message["role"], role_constraints)
                errors.extend(constraint_errors)
            
            # Validate content
            if "content" not in message:
                errors.append({
                    "type": ValidationErrorType.MISSING_REQUIRED,
                    "field": f"chat_history[{i}].content",
                    "message": f"Message {i} missing required 'content' field",
                    "code": "MISSING_CONTENT"
                })
            else:
                content_constraints = rules["item_constraints"]["content"]
                constraint_errors = self._validate_constraints(message["content"], content_constraints)
                errors.extend(constraint_errors)
        
        return {"is_valid": len(errors) == 0, "errors": errors}
    
    def validate_tool_response(self, tool_response: ToolResponse) -> ValidationResult:
        """Validate a tool response."""
        errors = []
        
        # Basic response structure validation
        if not isinstance(tool_response.success, bool):
            errors.append({
                "type": ValidationErrorType.INVALID_TYPE,
                "field": "success",
                "message": "Response 'success' field must be boolean",
                "code": "INVALID_SUCCESS_TYPE"
            })
        
        if tool_response.success:
            if not tool_response.data:
                errors.append({
                    "type": ValidationErrorType.MISSING_REQUIRED,
                    "field": "data",
                    "message": "Successful response must include 'data' field",
                    "code": "MISSING_DATA"
                })
        else:
            if not tool_response.error:
                errors.append({
                    "type": ValidationErrorType.MISSING_REQUIRED,
                    "field": "error",
                    "message": "Failed response must include 'error' field",
                    "code": "MISSING_ERROR"
                })
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            validated_data=tool_response.dict() if len(errors) == 0 else None
        )
    
    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data to prevent security issues."""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized[key] = value.strip().replace('\x00', '')
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_input(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_input(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
