import re
import logging
from typing import Dict, List, Optional, Tuple
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from models import (
    ConversationContext, EducationalIntent, TeachingStyle, 
    EmotionalState, NoteTakingStyle, DifficultyLevel, ExplanationDepth
)

logger = logging.getLogger(__name__)

class ContextAnalyzer:
    """
    Analyzes conversation context to extract educational intent and parameters.
    Uses LangChain for intelligent parameter extraction and intent classification.
    """
    
    def __init__(self, openai_api_key: str):
        self.llm = OpenAI(openai_api_key=openai_api_key, temperature=0.1)
        self.intent_patterns = self._initialize_intent_patterns()
        self.parameter_patterns = self._initialize_parameter_patterns()
        
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting educational intents."""
        return {
            "note_making": [
                r"take notes", r"make notes", r"note taking", r"summarize",
                r"outline", r"organize", r"write down", r"document"
            ],
            "flashcard_generation": [
                r"flashcards", r"flash cards", r"memorize", r"study cards",
                r"practice", r"quiz", r"test", r"review"
            ],
            "concept_explanation": [
                r"explain", r"understand", r"what is", r"how does",
                r"tell me about", r"describe", r"clarify", r"help me understand"
            ],
            "quiz_generation": [
                r"quiz", r"test", r"questions", r"practice problems",
                r"exam", r"assessment", r"challenge"
            ]
        }
    
    def _initialize_parameter_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for extracting parameters."""
        return {
            "topic": [
                r"about (.+?)(?:\s|$)", r"topic (.+?)(?:\s|$)", 
                r"subject (.+?)(?:\s|$)", r"regarding (.+?)(?:\s|$)"
            ],
            "subject": [
                r"in (.+?)(?:\s|$)", r"for (.+?)(?:\s|$)", 
                r"about (.+?)(?:\s|$)", r"subject (.+?)(?:\s|$)"
            ],
            "difficulty": [
                r"easy", r"simple", r"basic", r"beginner",
                r"hard", r"difficult", r"advanced", r"complex",
                r"medium", r"intermediate"
            ],
            "count": [
                r"(\d+)\s*(?:questions?|cards?|notes?|items?)",
                r"(\d+)\s*(?:of|for)", r"(\d+)\s*(?:more|additional)"
            ]
        }
    
    def analyze_context(self, context: ConversationContext) -> EducationalIntent:
        """
        Analyze conversation context to determine educational intent and extract parameters.
        """
        try:
            # Extract intent type and confidence
            intent_type, confidence = self._detect_intent(context.current_message)
            
            # Extract parameters from conversation
            extracted_params = self._extract_parameters(context)
            
            # Determine suggested tool
            suggested_tool = self._map_intent_to_tool(intent_type)
            
            # Identify missing parameters
            missing_params = self._identify_missing_parameters(
                intent_type, extracted_params
            )
            
            return EducationalIntent(
                intent_type=intent_type,
                confidence=confidence,
                extracted_parameters=extracted_params,
                missing_parameters=missing_params,
                suggested_tool=suggested_tool
            )
            
        except Exception as e:
            logger.error(f"Error analyzing context: {e}")
            return EducationalIntent(
                intent_type="unknown",
                confidence=0.0,
                extracted_parameters={},
                missing_parameters=[],
                suggested_tool="none"
            )
    
    def _detect_intent(self, message: str) -> Tuple[str, float]:
        """Detect educational intent from message using pattern matching and LLM."""
        message_lower = message.lower()
        
        # Pattern-based detection
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            intent_scores[intent] = score / len(patterns)
        
        # Find best intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # Use LLM for additional validation if confidence is low
        if best_intent[1] < 0.5:
            llm_intent = self._llm_intent_detection(message)
            if llm_intent:
                return llm_intent, 0.8
        
        return best_intent[0], best_intent[1]
    
    def _llm_intent_detection(self, message: str) -> Optional[str]:
        """Use LLM to detect intent when pattern matching is inconclusive."""
        prompt = PromptTemplate(
            input_variables=["message"],
            template="""
            Analyze the following student message and determine the primary educational intent.
            Choose from: note_making, flashcard_generation, concept_explanation, quiz_generation
            
            Message: {message}
            
            Intent:
            """
        )
        
        try:
            response = self.llm(prompt.format(message=message))
            intent = response.strip().lower()
            if intent in self.intent_patterns.keys():
                return intent
        except Exception as e:
            logger.error(f"LLM intent detection failed: {e}")
        
        return None
    
    def _extract_parameters(self, context: ConversationContext) -> Dict[str, any]:
        """Extract parameters from conversation context."""
        params = {}
        message = context.current_message.lower()
        
        # Extract topic
        topic = self._extract_topic(message, context.chat_history)
        if topic:
            params["topic"] = topic
        
        # Extract subject
        subject = self._extract_subject(message, context.chat_history)
        if subject:
            params["subject"] = subject
        
        # Extract difficulty based on emotional state and mastery level
        difficulty = self._infer_difficulty(context)
        if difficulty:
            params["difficulty"] = difficulty
        
        # Extract count
        count = self._extract_count(message)
        if count:
            params["count"] = count
        
        # Extract note-taking style based on learning style
        note_style = self._infer_note_style(context)
        if note_style:
            params["note_taking_style"] = note_style
        
        # Extract explanation depth
        depth = self._infer_explanation_depth(context)
        if depth:
            params["desired_depth"] = depth
        
        return params
    
    def _extract_topic(self, message: str, chat_history: List) -> Optional[str]:
        """Extract topic from message and chat history."""
        # Try to extract from current message
        for pattern in self.parameter_patterns["topic"]:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        
        # Try to extract from chat history
        for msg in reversed(chat_history[-3:]):  # Last 3 messages
            if msg.role.value == "user":
                for pattern in self.parameter_patterns["topic"]:
                    match = re.search(pattern, msg.content.lower())
                    if match:
                        return match.group(1).strip()
        
        return None
    
    def _extract_subject(self, message: str, chat_history: List) -> Optional[str]:
        """Extract subject from message and chat history."""
        subjects = [
            "math", "mathematics", "calculus", "algebra", "geometry",
            "science", "physics", "chemistry", "biology", "environmental science",
            "english", "literature", "writing", "grammar",
            "history", "social studies", "geography",
            "computer science", "programming", "coding"
        ]
        
        message_lower = message.lower()
        for subject in subjects:
            if subject in message_lower:
                return subject.title()
        
        return None
    
    def _infer_difficulty(self, context: ConversationContext) -> Optional[str]:
        """Infer difficulty level based on emotional state and mastery level."""
        emotional_state = context.emotional_state
        mastery_level = context.mastery_level
        
        if emotional_state == EmotionalState.CONFUSED:
            return "easy"
        elif emotional_state == EmotionalState.ANXIOUS:
            return "easy"
        elif emotional_state == EmotionalState.TIRED:
            return "easy"
        elif emotional_state == EmotionalState.FOCUSED:
            if mastery_level and mastery_level >= 7:
                return "hard"
            elif mastery_level and mastery_level >= 4:
                return "medium"
            else:
                return "easy"
        
        # Default based on mastery level
        if mastery_level:
            if mastery_level <= 3:
                return "easy"
            elif mastery_level <= 6:
                return "medium"
            else:
                return "hard"
        
        return "medium"
    
    def _extract_count(self, message: str) -> Optional[int]:
        """Extract count/number from message."""
        for pattern in self.parameter_patterns["count"]:
            match = re.search(pattern, message)
            if match:
                count = int(match.group(1))
                return min(max(count, 1), 20)  # Clamp between 1-20
        
        return None
    
    def _infer_note_style(self, context: ConversationContext) -> Optional[str]:
        """Infer note-taking style based on learning style."""
        learning_style = context.user_info.learning_style_summary.lower()
        
        if "outline" in learning_style or "structured" in learning_style:
            return "outline"
        elif "bullet" in learning_style or "points" in learning_style:
            return "bullet_points"
        elif "narrative" in learning_style or "story" in learning_style:
            return "narrative"
        else:
            return "structured"
    
    def _infer_explanation_depth(self, context: ConversationContext) -> Optional[str]:
        """Infer explanation depth based on mastery level and emotional state."""
        mastery_level = context.mastery_level
        emotional_state = context.emotional_state
        
        if emotional_state == EmotionalState.CONFUSED:
            return "basic"
        elif emotional_state == EmotionalState.ANXIOUS:
            return "basic"
        
        if mastery_level:
            if mastery_level <= 3:
                return "basic"
            elif mastery_level <= 6:
                return "intermediate"
            elif mastery_level <= 8:
                return "advanced"
            else:
                return "comprehensive"
        
        return "intermediate"
    
    def _map_intent_to_tool(self, intent_type: str) -> str:
        """Map intent type to corresponding tool."""
        mapping = {
            "note_making": "note_maker",
            "flashcard_generation": "flashcard_generator",
            "concept_explanation": "concept_explainer",
            "quiz_generation": "quiz_generator"
        }
        return mapping.get(intent_type, "unknown")
    
    def _identify_missing_parameters(self, intent_type: str, params: Dict[str, any]) -> List[str]:
        """Identify missing required parameters for the intent type."""
        required_params = {
            "note_making": ["topic", "subject", "note_taking_style"],
            "flashcard_generation": ["topic", "count", "difficulty", "subject"],
            "concept_explanation": ["concept_to_explain", "current_topic", "desired_depth"],
            "quiz_generation": ["topic", "subject", "difficulty", "count"]
        }
        
        required = required_params.get(intent_type, [])
        missing = [param for param in required if param not in params]
        
        return missing
