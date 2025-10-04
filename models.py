from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class TeachingStyle(str, Enum):
    DIRECT = "direct"
    SOCRATIC = "socratic"
    VISUAL = "visual"
    FLIPPED_CLASSROOM = "flipped_classroom"

class EmotionalState(str, Enum):
    FOCUSED = "focused"
    ANXIOUS = "anxious"
    CONFUSED = "confused"
    TIRED = "tired"

class NoteTakingStyle(str, Enum):
    OUTLINE = "outline"
    BULLET_POINTS = "bullet_points"
    NARRATIVE = "narrative"
    STRUCTURED = "structured"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ExplanationDepth(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    COMPREHENSIVE = "comprehensive"

class ChatMessage(BaseModel):
    role: Role
    content: str

class UserInfo(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the student")
    name: str = Field(..., description="Student's full name")
    grade_level: str = Field(..., description="Student's current grade level")
    learning_style_summary: str = Field(..., description="Summary of student's preferred learning style")
    emotional_state_summary: str = Field(..., description="Current emotional state of the student")
    mastery_level_summary: str = Field(..., description="Current mastery level description")

class ConversationContext(BaseModel):
    user_info: UserInfo
    chat_history: List[ChatMessage]
    current_message: str
    teaching_style: Optional[TeachingStyle] = None
    emotional_state: Optional[EmotionalState] = None
    mastery_level: Optional[int] = Field(None, ge=1, le=10)

class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    user_info: UserInfo
    chat_history: List[ChatMessage]

class ToolResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

class EducationalIntent(BaseModel):
    intent_type: str  # "note_making", "flashcard_generation", "concept_explanation", etc.
    confidence: float = Field(..., ge=0.0, le=1.0)
    extracted_parameters: Dict[str, Any]
    missing_parameters: List[str]
    suggested_tool: str

class OrchestratorResponse(BaseModel):
    success: bool
    tool_response: Optional[ToolResponse] = None
    educational_intent: Optional[EducationalIntent] = None
    error_message: Optional[str] = None
    conversation_context: Optional[ConversationContext] = None
