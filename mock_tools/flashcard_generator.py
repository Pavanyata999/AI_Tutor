from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging

logger = logging.getLogger(__name__)

# Flashcard Generator Tool Models
class FlashcardGeneratorRequest(BaseModel):
    user_info: Dict[str, Any]
    topic: str
    count: int
    difficulty: str
    subject: str
    include_examples: Optional[bool] = True

class Flashcard(BaseModel):
    front: str
    back: str
    difficulty: str
    topic: str
    examples: Optional[List[str]] = []

class FlashcardGeneratorResponse(BaseModel):
    success: bool
    flashcards: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

# Create FastAPI app for Flashcard Generator
flashcard_app = FastAPI(title="Flashcard Generator Tool", version="1.0.0")

flashcard_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@flashcard_app.post("/generate", response_model=FlashcardGeneratorResponse)
async def generate_flashcards(request: FlashcardGeneratorRequest):
    """Generate flashcards based on the request."""
    try:
        logger.info(f"Generating {request.count} flashcards for topic: {request.topic}")
        
        # Validate count
        if request.count < 1 or request.count > 20:
            return FlashcardGeneratorResponse(
                success=False,
                error="Count must be between 1 and 20",
                error_code="INVALID_COUNT"
            )
        
        # Extract user context
        user_name = request.user_info.get("name", "Student")
        grade_level = request.user_info.get("grade_level", "Unknown")
        learning_style = request.user_info.get("learning_style_summary", "")
        emotional_state = request.user_info.get("emotional_state_summary", "")
        mastery_level = request.user_info.get("mastery_level_summary", "")
        
        # Generate flashcards based on difficulty
        flashcards = _generate_flashcards_by_difficulty(
            request.topic, 
            request.subject, 
            request.count, 
            request.difficulty,
            request.include_examples
        )
        
        # Add personalization metadata
        metadata = {
            "user_name": user_name,
            "grade_level": grade_level,
            "learning_style": learning_style,
            "emotional_state": emotional_state,
            "mastery_level": mastery_level,
            "generation_timestamp": "2024-01-01T00:00:00Z"
        }
        
        return FlashcardGeneratorResponse(
            success=True, 
            flashcards=flashcards,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Flashcard generation failed: {e}")
        return FlashcardGeneratorResponse(
            success=False,
            error=f"Flashcard generation failed: {str(e)}",
            error_code="GENERATION_ERROR"
        )

def _generate_flashcards_by_difficulty(
    topic: str, 
    subject: str, 
    count: int, 
    difficulty: str,
    include_examples: bool
) -> List[Dict[str, Any]]:
    """Generate flashcards based on difficulty level."""
    flashcards = []
    
    if difficulty == "easy":
        flashcards = _generate_easy_flashcards(topic, subject, count, include_examples)
    elif difficulty == "medium":
        flashcards = _generate_medium_flashcards(topic, subject, count, include_examples)
    else:  # hard
        flashcards = _generate_hard_flashcards(topic, subject, count, include_examples)
    
    return flashcards

def _generate_easy_flashcards(topic: str, subject: str, count: int, include_examples: bool) -> List[Dict[str, Any]]:
    """Generate easy-level flashcards."""
    flashcards = []
    
    for i in range(count):
        card_num = i + 1
        flashcards.append({
            "id": f"easy_{topic}_{card_num}",
            "front": f"What is {topic}?",
            "back": f"{topic} is a fundamental concept in {subject} that represents...",
            "difficulty": "easy",
            "topic": topic,
            "subject": subject,
            "examples": [
                f"Example: {topic} in everyday life",
                f"Simple case: {topic} application"
            ] if include_examples else [],
            "hints": [f"Think about basic {topic} concepts"],
            "tags": ["basic", "foundation", topic.lower()]
        })
    
    return flashcards

def _generate_medium_flashcards(topic: str, subject: str, count: int, include_examples: bool) -> List[Dict[str, Any]]:
    """Generate medium-level flashcards."""
    flashcards = []
    
    for i in range(count):
        card_num = i + 1
        flashcards.append({
            "id": f"medium_{topic}_{card_num}",
            "front": f"How does {topic} work in {subject}?",
            "back": f"{topic} operates through several mechanisms including process A, process B, and process C. The key principle is...",
            "difficulty": "medium",
            "topic": topic,
            "subject": subject,
            "examples": [
                f"Real-world example: {topic} implementation",
                f"Case study: {topic} in practice",
                f"Application: {topic} usage"
            ] if include_examples else [],
            "hints": [f"Consider the processes involved in {topic}"],
            "tags": ["intermediate", "application", topic.lower()]
        })
    
    return flashcards

def _generate_hard_flashcards(topic: str, subject: str, count: int, include_examples: bool) -> List[Dict[str, Any]]:
    """Generate hard-level flashcards."""
    flashcards = []
    
    for i in range(count):
        card_num = i + 1
        flashcards.append({
            "id": f"hard_{topic}_{card_num}",
            "front": f"Analyze the complex relationship between {topic} and advanced {subject} concepts",
            "back": f"The sophisticated interplay between {topic} and advanced {subject} involves multiple layers of complexity. Key factors include theoretical frameworks, practical applications, and emergent properties that require deep understanding of...",
            "difficulty": "hard",
            "topic": topic,
            "subject": subject,
            "examples": [
                f"Advanced case: Complex {topic} scenario",
                f"Research example: {topic} in academic context",
                f"Professional application: {topic} in industry"
            ] if include_examples else [],
            "hints": [f"Consider multiple perspectives on {topic}"],
            "tags": ["advanced", "complex", "analysis", topic.lower()]
        })
    
    return flashcards

@flashcard_app.get("/")
async def root():
    return {"tool": "Flashcard Generator", "version": "1.0.0", "status": "active"}

@flashcard_app.get("/health")
async def health():
    return {"status": "healthy", "tool": "flashcard_generator"}

if __name__ == "__main__":
    uvicorn.run(flashcard_app, host="0.0.0.0", port=8002)
