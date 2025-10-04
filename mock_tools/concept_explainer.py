from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging

logger = logging.getLogger(__name__)

# Concept Explainer Tool Models
class ConceptExplainerRequest(BaseModel):
    user_info: Dict[str, Any]
    chat_history: List[Dict[str, Any]]
    concept_to_explain: str
    current_topic: str
    desired_depth: str

class ConceptExplanation(BaseModel):
    concept: str
    explanation: str
    depth_level: str
    examples: List[str]
    analogies: List[str]
    related_concepts: List[str]

class ConceptExplainerResponse(BaseModel):
    success: bool
    explanation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

# Create FastAPI app for Concept Explainer
concept_explainer_app = FastAPI(title="Concept Explainer Tool", version="1.0.0")

concept_explainer_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@concept_explainer_app.post("/generate", response_model=ConceptExplainerResponse)
async def explain_concept(request: ConceptExplainerRequest):
    """Generate concept explanation based on the request."""
    try:
        logger.info(f"Explaining concept: {request.concept_to_explain}")
        
        # Extract user context
        user_name = request.user_info.get("name", "Student")
        grade_level = request.user_info.get("grade_level", "Unknown")
        learning_style = request.user_info.get("learning_style_summary", "")
        emotional_state = request.user_info.get("emotional_state_summary", "")
        mastery_level = request.user_info.get("mastery_level_summary", "")
        
        # Generate explanation based on depth
        explanation = _generate_explanation_by_depth(
            request.concept_to_explain,
            request.current_topic,
            request.desired_depth,
            learning_style,
            emotional_state
        )
        
        # Add personalization metadata
        explanation["personalization"] = {
            "user_name": user_name,
            "grade_level": grade_level,
            "learning_style": learning_style,
            "emotional_state": emotional_state,
            "mastery_level": mastery_level,
            "explanation_timestamp": "2024-01-01T00:00:00Z"
        }
        
        return ConceptExplainerResponse(success=True, explanation=explanation)
        
    except Exception as e:
        logger.error(f"Concept explanation failed: {e}")
        return ConceptExplainerResponse(
            success=False,
            error=f"Concept explanation failed: {str(e)}",
            error_code="EXPLANATION_ERROR"
        )

def _generate_explanation_by_depth(
    concept: str,
    topic: str,
    depth: str,
    learning_style: str,
    emotional_state: str
) -> Dict[str, Any]:
    """Generate explanation based on desired depth level."""
    
    if depth == "basic":
        return _generate_basic_explanation(concept, topic, learning_style, emotional_state)
    elif depth == "intermediate":
        return _generate_intermediate_explanation(concept, topic, learning_style, emotional_state)
    elif depth == "advanced":
        return _generate_advanced_explanation(concept, topic, learning_style, emotional_state)
    else:  # comprehensive
        return _generate_comprehensive_explanation(concept, topic, learning_style, emotional_state)

def _generate_basic_explanation(concept: str, topic: str, learning_style: str, emotional_state: str) -> Dict[str, Any]:
    """Generate basic-level explanation."""
    return {
        "concept": concept,
        "topic": topic,
        "depth_level": "basic",
        "explanation": f"""
        {concept} is a fundamental concept in {topic}. At its core, {concept} represents 
        the basic building block that helps us understand how {topic} works.
        
        Think of {concept} as the foundation upon which more complex ideas are built. 
        It's like the first piece of a puzzle that helps you see the bigger picture.
        """,
        "key_points": [
            f"{concept} is essential for understanding {topic}",
            f"{concept} provides the foundation for advanced concepts",
            f"{concept} is used in many practical applications"
        ],
        "examples": [
            f"Simple example: {concept} in everyday life",
            f"Basic application: How {concept} works in practice"
        ],
        "analogies": [
            f"Think of {concept} like the foundation of a house",
            f"{concept} is similar to the alphabet in language learning"
        ],
        "related_concepts": [
            f"Basic concepts related to {concept}",
            f"Simple applications of {concept}"
        ],
        "learning_tips": [
            f"Start with understanding what {concept} means",
            f"Practice with simple examples of {concept}",
            f"Build confidence with basic {concept} applications"
        ],
        "difficulty_adaptation": "simplified" if emotional_state in ["confused", "anxious"] else "standard"
    }

def _generate_intermediate_explanation(concept: str, topic: str, learning_style: str, emotional_state: str) -> Dict[str, Any]:
    """Generate intermediate-level explanation."""
    return {
        "concept": concept,
        "topic": topic,
        "depth_level": "intermediate",
        "explanation": f"""
        {concept} represents a sophisticated mechanism within {topic} that involves 
        multiple interconnected processes. Understanding {concept} requires 
        comprehension of its underlying principles, mechanisms, and applications.
        
        The complexity of {concept} emerges from its interaction with various 
        factors and its role in the broader context of {topic}. This concept 
        serves as a bridge between basic understanding and advanced applications.
        """,
        "key_points": [
            f"{concept} involves multiple interconnected processes",
            f"{concept} serves as a bridge between basic and advanced concepts",
            f"{concept} has practical applications in various contexts",
            f"Understanding {concept} requires analytical thinking"
        ],
        "examples": [
            f"Real-world example: {concept} in professional practice",
            f"Case study: {concept} implementation",
            f"Application: {concept} in different contexts"
        ],
        "analogies": [
            f"{concept} is like a complex machine with multiple parts",
            f"Think of {concept} as a recipe with many ingredients"
        ],
        "related_concepts": [
            f"Advanced concepts building on {concept}",
            f"Practical applications of {concept}",
            f"Theoretical frameworks involving {concept}"
        ],
        "learning_tips": [
            f"Break down {concept} into its components",
            f"Practice with intermediate-level examples",
            f"Connect {concept} to real-world applications"
        ],
        "difficulty_adaptation": "guided" if emotional_state in ["confused", "anxious"] else "standard"
    }

def _generate_advanced_explanation(concept: str, topic: str, learning_style: str, emotional_state: str) -> Dict[str, Any]:
    """Generate advanced-level explanation."""
    return {
        "concept": concept,
        "topic": topic,
        "depth_level": "advanced",
        "explanation": f"""
        {concept} represents a complex, multi-dimensional phenomenon within {topic} 
        that encompasses theoretical frameworks, practical applications, and emergent 
        properties. The advanced understanding of {concept} requires synthesis of 
        multiple perspectives, critical analysis, and appreciation of nuanced interactions.
        
        At this level, {concept} reveals its sophisticated nature through intricate 
        relationships with other concepts, dynamic processes, and contextual variations. 
        Mastery of {concept} enables deep insights into {topic} and facilitates 
        innovative applications and theoretical contributions.
        """,
        "key_points": [
            f"{concept} involves complex theoretical frameworks",
            f"{concept} exhibits emergent properties and dynamic behaviors",
            f"{concept} requires synthesis of multiple perspectives",
            f"Advanced {concept} enables innovative applications",
            f"{concept} connects to broader theoretical contexts"
        ],
        "examples": [
            f"Advanced case study: Complex {concept} scenario",
            f"Research application: {concept} in academic context",
            f"Professional implementation: {concept} in industry",
            f"Innovative use: {concept} in emerging fields"
        ],
        "analogies": [
            f"{concept} is like a symphony with multiple instruments",
            f"Think of {concept} as an ecosystem with complex interactions"
        ],
        "related_concepts": [
            f"Cutting-edge research involving {concept}",
            f"Advanced theoretical frameworks for {concept}",
            f"Emerging applications of {concept}",
            f"Interdisciplinary connections of {concept}"
        ],
        "learning_tips": [
            f"Analyze {concept} from multiple theoretical perspectives",
            f"Engage with advanced research on {concept}",
            f"Practice critical analysis of {concept} applications",
            f"Explore innovative uses of {concept}"
        ],
        "difficulty_adaptation": "challenging" if emotional_state == "focused" else "standard"
    }

def _generate_comprehensive_explanation(concept: str, topic: str, learning_style: str, emotional_state: str) -> Dict[str, Any]:
    """Generate comprehensive explanation covering all aspects."""
    return {
        "concept": concept,
        "topic": topic,
        "depth_level": "comprehensive",
        "explanation": f"""
        {concept} represents a comprehensive, multi-faceted phenomenon that spans 
        the entire spectrum of {topic} understanding. This complete exploration 
        encompasses foundational principles, intermediate applications, advanced 
        theoretical frameworks, and cutting-edge innovations.
        
        The comprehensive understanding of {concept} integrates historical development, 
        current state-of-the-art, and future directions. It connects theoretical 
        foundations with practical applications, basic principles with advanced 
        complexities, and individual concepts with broader systemic understanding.
        """,
        "foundational_aspects": [
            f"Basic definition and principles of {concept}",
            f"Historical development of {concept}",
            f"Core mechanisms underlying {concept}"
        ],
        "intermediate_aspects": [
            f"Practical applications of {concept}",
            f"Common variations and implementations of {concept}",
            f"Integration of {concept} with related concepts"
        ],
        "advanced_aspects": [
            f"Complex theoretical frameworks for {concept}",
            f"Emergent properties and behaviors of {concept}",
            f"Advanced analytical methods for {concept}"
        ],
        "cutting_edge_aspects": [
            f"Latest research developments in {concept}",
            f"Innovative applications of {concept}",
            f"Future directions for {concept} research"
        ],
        "examples": [
            f"Historical example: Early development of {concept}",
            f"Contemporary example: Current applications of {concept}",
            f"Future example: Emerging uses of {concept}",
            f"Cross-disciplinary example: {concept} in other fields"
        ],
        "analogies": [
            f"{concept} is like a complete ecosystem",
            f"Think of {concept} as a comprehensive library",
            f"{concept} resembles a complex city with many districts"
        ],
        "related_concepts": [
            f"All foundational concepts related to {concept}",
            f"Intermediate concepts building on {concept}",
            f"Advanced concepts extending {concept}",
            f"Cutting-edge concepts emerging from {concept}"
        ],
        "learning_tips": [
            f"Start with foundational understanding of {concept}",
            f"Progress through intermediate applications of {concept}",
            f"Engage with advanced theoretical aspects of {concept}",
            f"Explore cutting-edge developments in {concept}",
            f"Synthesize all levels of {concept} understanding"
        ],
        "difficulty_adaptation": "comprehensive" if emotional_state == "focused" else "adaptive"
    }

@concept_explainer_app.get("/")
async def root():
    return {"tool": "Concept Explainer", "version": "1.0.0", "status": "active"}

@concept_explainer_app.get("/health")
async def health():
    return {"status": "healthy", "tool": "concept_explainer"}

if __name__ == "__main__":
    uvicorn.run(concept_explainer_app, host="0.0.0.0", port=8003)
