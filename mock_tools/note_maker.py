from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging

logger = logging.getLogger(__name__)

# Note Maker Tool Models
class NoteMakerRequest(BaseModel):
    user_info: Dict[str, Any]
    chat_history: List[Dict[str, Any]]
    topic: str
    subject: str
    note_taking_style: str
    include_examples: Optional[bool] = True
    include_analogies: Optional[bool] = False

class NoteSection(BaseModel):
    title: str
    content: str
    examples: List[str]
    analogies: List[str]

class NoteMakerResponse(BaseModel):
    success: bool
    notes: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

# Create FastAPI app for Note Maker
note_maker_app = FastAPI(title="Note Maker Tool", version="1.0.0")

note_maker_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@note_maker_app.post("/generate", response_model=NoteMakerResponse)
async def generate_notes(request: NoteMakerRequest):
    """Generate structured notes based on the request."""
    try:
        logger.info(f"Generating notes for topic: {request.topic}")
        
        # Extract user context
        user_name = request.user_info.get("name", "Student")
        grade_level = request.user_info.get("grade_level", "Unknown")
        learning_style = request.user_info.get("learning_style_summary", "")
        emotional_state = request.user_info.get("emotional_state_summary", "")
        mastery_level = request.user_info.get("mastery_level_summary", "")
        
        # Generate notes based on style
        if request.note_taking_style == "outline":
            notes = _generate_outline_notes(request.topic, request.subject, request.include_examples, request.include_analogies)
        elif request.note_taking_style == "bullet_points":
            notes = _generate_bullet_notes(request.topic, request.subject, request.include_examples, request.include_analogies)
        elif request.note_taking_style == "narrative":
            notes = _generate_narrative_notes(request.topic, request.subject, request.include_examples, request.include_analogies)
        else:  # structured
            notes = _generate_structured_notes(request.topic, request.subject, request.include_examples, request.include_analogies)
        
        # Add personalization based on user context
        notes["personalization"] = {
            "user_name": user_name,
            "grade_level": grade_level,
            "learning_style": learning_style,
            "emotional_state": emotional_state,
            "mastery_level": mastery_level
        }
        
        return NoteMakerResponse(success=True, notes=notes)
        
    except Exception as e:
        logger.error(f"Note generation failed: {e}")
        return NoteMakerResponse(
            success=False,
            error=f"Note generation failed: {str(e)}",
            error_code="GENERATION_ERROR"
        )

def _generate_outline_notes(topic: str, subject: str, include_examples: bool, include_analogies: bool) -> Dict[str, Any]:
    """Generate outline-style notes."""
    return {
        "note_type": "outline",
        "topic": topic,
        "subject": subject,
        "sections": [
            {
                "title": f"Introduction to {topic}",
                "content": f"This section covers the fundamental concepts of {topic} in {subject}.",
                "subsections": [
                    {"title": "Definition", "content": f"{topic} is defined as..."},
                    {"title": "Key Concepts", "content": f"The main concepts in {topic} include..."}
                ],
                "examples": [f"Example 1: {topic} in real-world application"] if include_examples else [],
                "analogies": [f"Think of {topic} like..."] if include_analogies else []
            },
            {
                "title": f"Advanced {topic}",
                "content": f"This section explores advanced aspects of {topic}.",
                "subsections": [
                    {"title": "Complex Applications", "content": f"Advanced applications of {topic}..."},
                    {"title": "Related Topics", "content": f"Topics related to {topic} include..."}
                ],
                "examples": [f"Advanced example: {topic} case study"] if include_examples else [],
                "analogies": [f"Advanced analogy for {topic}..."] if include_analogies else []
            }
        ],
        "key_concepts": [f"Concept 1: {topic} basics", f"Concept 2: {topic} applications"],
        "connections_to_prior_learning": [f"Builds on previous knowledge of {subject}"],
        "visual_elements": [{"type": "diagram", "description": f"Visual representation of {topic}"}]
    }

def _generate_bullet_notes(topic: str, subject: str, include_examples: bool, include_analogies: bool) -> Dict[str, Any]:
    """Generate bullet-point style notes."""
    return {
        "note_type": "bullet_points",
        "topic": topic,
        "subject": subject,
        "main_points": [
            f"• {topic} is a fundamental concept in {subject}",
            f"• Key characteristics of {topic}:",
            f"  - Characteristic 1",
            f"  - Characteristic 2",
            f"  - Characteristic 3",
            f"• Applications of {topic}:",
            f"  - Application 1",
            f"  - Application 2",
            f"• Important considerations for {topic}"
        ],
        "examples": [
            f"Example: {topic} in practice",
            f"Case study: {topic} application"
        ] if include_examples else [],
        "analogies": [
            f"Analogy: {topic} is like...",
            f"Comparison: {topic} vs similar concepts"
        ] if include_analogies else [],
        "key_concepts": [f"Key concept 1: {topic}", f"Key concept 2: {topic} applications"],
        "summary": f"Summary: {topic} is essential for understanding {subject}"
    }

def _generate_narrative_notes(topic: str, subject: str, include_examples: bool, include_analogies: bool) -> Dict[str, Any]:
    """Generate narrative-style notes."""
    return {
        "note_type": "narrative",
        "topic": topic,
        "subject": subject,
        "narrative_content": f"""
        The study of {topic} in {subject} represents a fascinating journey through fundamental principles and practical applications. 
        This concept has evolved over time and continues to shape our understanding of {subject}.
        
        Beginning with the basics, {topic} serves as a cornerstone for more advanced studies. The foundational elements 
        provide students with the necessary building blocks to explore complex applications and real-world scenarios.
        
        As we delve deeper into {topic}, we discover its multifaceted nature and the various ways it influences 
        our daily lives and professional practices. The interconnectedness of concepts becomes apparent, 
        revealing the intricate web of knowledge that defines {subject}.
        """,
        "examples": [
            f"Real-world example: {topic} in action",
            f"Historical example: Evolution of {topic}"
        ] if include_examples else [],
        "analogies": [
            f"Metaphor: {topic} as a foundation",
            f"Story: The journey of understanding {topic}"
        ] if include_analogies else [],
        "key_concepts": [f"Narrative concept 1: {topic}", f"Narrative concept 2: {topic} evolution"],
        "conclusion": f"In conclusion, {topic} represents a vital component of {subject} education."
    }

def _generate_structured_notes(topic: str, subject: str, include_examples: bool, include_analogies: bool) -> Dict[str, Any]:
    """Generate structured notes with clear organization."""
    return {
        "note_type": "structured",
        "topic": topic,
        "subject": subject,
        "structure": {
            "introduction": {
                "overview": f"Overview of {topic} in {subject}",
                "objectives": [f"Understand {topic}", f"Apply {topic} concepts", f"Analyze {topic} applications"],
                "prerequisites": [f"Basic knowledge of {subject}"]
            },
            "main_content": {
                "core_concepts": [
                    {"concept": f"Core concept 1: {topic}", "description": f"Description of core concept 1"},
                    {"concept": f"Core concept 2: {topic}", "description": f"Description of core concept 2"}
                ],
                "detailed_explanations": [
                    f"Detailed explanation of {topic} principles",
                    f"Step-by-step breakdown of {topic} processes"
                ]
            },
            "applications": {
                "practical_uses": [f"Practical use 1 of {topic}", f"Practical use 2 of {topic}"],
                "case_studies": [f"Case study: {topic} implementation"] if include_examples else []
            },
            "conclusion": {
                "key_takeaways": [f"Key takeaway 1: {topic}", f"Key takeaway 2: {topic}"],
                "next_steps": [f"Further study of {topic}", f"Practice with {topic}"]
            }
        },
        "examples": [
            f"Structured example: {topic} demonstration",
            f"Application example: {topic} in practice"
        ] if include_examples else [],
        "analogies": [
            f"Structural analogy: {topic} framework",
            f"System analogy: {topic} components"
        ] if include_analogies else [],
        "visual_elements": [
            {"type": "flowchart", "description": f"{topic} process flow"},
            {"type": "diagram", "description": f"{topic} structure diagram"}
        ]
    }

@note_maker_app.get("/")
async def root():
    return {"tool": "Note Maker", "version": "1.0.0", "status": "active"}

@note_maker_app.get("/health")
async def health():
    return {"status": "healthy", "tool": "note_maker"}

if __name__ == "__main__":
    uvicorn.run(note_maker_app, host="0.0.0.0", port=8001)
