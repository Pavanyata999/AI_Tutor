#!/usr/bin/env python3
"""
Simplified AI Tutor Orchestrator Demo
=====================================

This is a simplified version that demonstrates the core functionality
without requiring complex dependencies like LangChain and LangGraph.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data models
class MockUserInfo:
    def __init__(self, user_id: str, name: str, grade_level: str, 
                 learning_style_summary: str, emotional_state_summary: str, 
                 mastery_level_summary: str):
        self.user_id = user_id
        self.name = name
        self.grade_level = grade_level
        self.learning_style_summary = learning_style_summary
        self.emotional_state_summary = emotional_state_summary
        self.mastery_level_summary = mastery_level_summary
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "grade_level": self.grade_level,
            "learning_style_summary": self.learning_style_summary,
            "emotional_state_summary": self.emotional_state_summary,
            "mastery_level_summary": self.mastery_level_summary
        }

class MockChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_dict(self):
        return {"role": self.role, "content": self.content}

class MockConversationContext:
    def __init__(self, user_info: MockUserInfo, chat_history: List[MockChatMessage], 
                 current_message: str, teaching_style: str = "direct", 
                 emotional_state: str = "focused", mastery_level: int = 5):
        self.user_info = user_info
        self.chat_history = chat_history
        self.current_message = current_message
        self.teaching_style = teaching_style
        self.emotional_state = emotional_state
        self.mastery_level = mastery_level

class MockEducationalIntent:
    def __init__(self, intent_type: str, confidence: float, extracted_parameters: Dict[str, Any], 
                 missing_parameters: List[str], suggested_tool: str):
        self.intent_type = intent_type
        self.confidence = confidence
        self.extracted_parameters = extracted_parameters
        self.missing_parameters = missing_parameters
        self.suggested_tool = suggested_tool
    
    def to_dict(self):
        return {
            "intent_type": self.intent_type,
            "confidence": self.confidence,
            "extracted_parameters": self.extracted_parameters,
            "missing_parameters": self.missing_parameters,
            "suggested_tool": self.suggested_tool
        }

class MockToolResponse:
    def __init__(self, success: bool, data: Optional[Dict[str, Any]] = None, 
                 error: Optional[str] = None, error_code: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.error_code = error_code
    
    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "error_code": self.error_code
        }

class MockOrchestratorResponse:
    def __init__(self, success: bool, tool_response: Optional[MockToolResponse] = None,
                 educational_intent: Optional[MockEducationalIntent] = None,
                 error_message: Optional[str] = None, conversation_context: Optional[MockConversationContext] = None):
        self.success = success
        self.tool_response = tool_response
        self.educational_intent = educational_intent
        self.error_message = error_message
        self.conversation_context = conversation_context
    
    def to_dict(self):
        return {
            "success": self.success,
            "tool_response": self.tool_response.to_dict() if self.tool_response else None,
            "educational_intent": self.educational_intent.to_dict() if self.educational_intent else None,
            "error_message": self.error_message,
            "conversation_context": {
                "user_info": self.conversation_context.user_info.to_dict() if self.conversation_context else None,
                "current_message": self.conversation_context.current_message if self.conversation_context else None
            }
        }

class SimplifiedContextAnalyzer:
    """Simplified context analyzer using pattern matching."""
    
    def __init__(self):
        self.intent_patterns = {
            "note_making": [
                r"take notes", r"make notes", r"note taking", r"summarize",
                r"outline", r"organize", r"write down", r"document",
                r"help me take", r"notes on", r"structured notes"
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
    
    def analyze_context(self, context: MockConversationContext) -> MockEducationalIntent:
        """Analyze conversation context to determine educational intent."""
        message_lower = context.current_message.lower()
        
        # Pattern-based intent detection
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            intent_scores[intent] = score / len(patterns)
        
        # Find best intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_type, confidence = best_intent
        
        # Extract parameters
        extracted_params = self._extract_parameters(context)
        
        # Map intent to tool
        tool_mapping = {
            "note_making": "note_maker",
            "flashcard_generation": "flashcard_generator", 
            "concept_explanation": "concept_explainer",
            "quiz_generation": "quiz_generator"
        }
        suggested_tool = tool_mapping.get(intent_type, "unknown")
        
        # Identify missing parameters
        missing_params = self._identify_missing_parameters(intent_type, extracted_params)
        
        return MockEducationalIntent(
            intent_type=intent_type,
            confidence=confidence,
            extracted_parameters=extracted_params,
            missing_parameters=missing_params,
            suggested_tool=suggested_tool
        )
    
    def _extract_parameters(self, context: MockConversationContext) -> Dict[str, Any]:
        """Extract parameters from conversation context."""
        params = {}
        message = context.current_message.lower()
        
        # Extract topic
        topic_patterns = [
            r"about (.+?)(?:\s|$)", r"topic (.+?)(?:\s|$)", 
            r"subject (.+?)(?:\s|$)", r"regarding (.+?)(?:\s|$)",
            r"on (.+?)(?:\s|$)", r"for (.+?)(?:\s|$)"
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, message)
            if match:
                params["topic"] = match.group(1).strip()
                break
        
        # Extract subject
        subjects = [
            "math", "mathematics", "calculus", "algebra", "geometry",
            "science", "physics", "chemistry", "biology", "environmental science",
            "english", "literature", "writing", "grammar",
            "history", "social studies", "geography",
            "computer science", "programming", "coding"
        ]
        
        for subject in subjects:
            if subject in message:
                params["subject"] = subject.title()
                break
        
        # Infer difficulty based on emotional state
        if context.emotional_state == "confused":
            params["difficulty"] = "easy"
        elif context.emotional_state == "anxious":
            params["difficulty"] = "easy"
        elif context.emotional_state == "focused" and context.mastery_level >= 7:
            params["difficulty"] = "hard"
        else:
            params["difficulty"] = "medium"
        
        # Extract count
        count_patterns = [
            r"(\d+)\s*(?:questions?|cards?|notes?|items?)",
            r"(\d+)\s*(?:of|for)", r"(\d+)\s*(?:more|additional)"
        ]
        
        for pattern in count_patterns:
            match = re.search(pattern, message)
            if match:
                count = int(match.group(1))
                params["count"] = min(max(count, 1), 20)  # Clamp between 1-20
                break
        
        # Infer note-taking style
        learning_style = context.user_info.learning_style_summary.lower()
        if "outline" in learning_style:
            params["note_taking_style"] = "outline"
        elif "bullet" in learning_style:
            params["note_taking_style"] = "bullet_points"
        elif "narrative" in learning_style:
            params["note_taking_style"] = "narrative"
        else:
            params["note_taking_style"] = "structured"
        
        # Infer explanation depth
        if context.emotional_state == "confused":
            params["desired_depth"] = "basic"
        elif context.mastery_level <= 3:
            params["desired_depth"] = "basic"
        elif context.mastery_level <= 6:
            params["desired_depth"] = "intermediate"
        elif context.mastery_level <= 8:
            params["desired_depth"] = "advanced"
        else:
            params["desired_depth"] = "comprehensive"
        
        return params
    
    def _identify_missing_parameters(self, intent_type: str, params: Dict[str, Any]) -> List[str]:
        """Identify missing required parameters."""
        required_params = {
            "note_making": ["topic", "subject", "note_taking_style"],
            "flashcard_generation": ["topic", "count", "difficulty", "subject"],
            "concept_explanation": ["concept_to_explain", "current_topic", "desired_depth"],
            "quiz_generation": ["topic", "subject", "difficulty", "count"]
        }
        
        required = required_params.get(intent_type, [])
        missing = [param for param in required if param not in params]
        
        return missing

class MockEducationalTools:
    """Mock educational tools that simulate the real tools."""
    
    @staticmethod
    async def note_maker(params: Dict[str, Any], user_info: MockUserInfo) -> MockToolResponse:
        """Mock note maker tool."""
        topic = params.get("topic", "General Topic")
        subject = params.get("subject", "General Subject")
        style = params.get("note_taking_style", "structured")
        
        notes = {
            "note_type": style,
            "topic": topic,
            "subject": subject,
            "sections": [
                {
                    "title": f"Introduction to {topic}",
                    "content": f"This section covers the fundamental concepts of {topic} in {subject}.",
                    "examples": [f"Example: {topic} in real-world application"],
                    "analogies": [f"Think of {topic} like..."]
                }
            ],
            "key_concepts": [f"Key concept 1: {topic}", f"Key concept 2: {topic} applications"],
            "personalization": {
                "user_name": user_info.name,
                "grade_level": user_info.grade_level,
                "learning_style": user_info.learning_style_summary
            }
        }
        
        return MockToolResponse(success=True, data={"notes": notes})
    
    @staticmethod
    async def flashcard_generator(params: Dict[str, Any], user_info: MockUserInfo) -> MockToolResponse:
        """Mock flashcard generator tool."""
        topic = params.get("topic", "General Topic")
        count = params.get("count", 10)
        difficulty = params.get("difficulty", "medium")
        subject = params.get("subject", "General Subject")
        
        flashcards = []
        for i in range(count):
            flashcards.append({
                "id": f"{difficulty}_{topic}_{i+1}",
                "front": f"What is {topic}?",
                "back": f"{topic} is a concept in {subject} that represents...",
                "difficulty": difficulty,
                "topic": topic,
                "examples": [f"Example: {topic} in practice"],
                "hints": [f"Think about {topic} concepts"]
            })
        
        return MockToolResponse(success=True, data={
            "flashcards": flashcards,
            "metadata": {
                "user_name": user_info.name,
                "generation_timestamp": datetime.now().isoformat()
            }
        })
    
    @staticmethod
    async def concept_explainer(params: Dict[str, Any], user_info: MockUserInfo) -> MockToolResponse:
        """Mock concept explainer tool."""
        concept = params.get("concept_to_explain", params.get("topic", "General Concept"))
        topic = params.get("current_topic", params.get("subject", "General Topic"))
        depth = params.get("desired_depth", "intermediate")
        
        explanation = {
            "concept": concept,
            "topic": topic,
            "depth_level": depth,
            "explanation": f"""
            {concept} is a fundamental concept in {topic}. At the {depth} level, 
            {concept} represents the core principles that help us understand 
            how {topic} works in practice.
            
            The key aspects of {concept} include its theoretical foundations,
            practical applications, and real-world examples that demonstrate
            its importance in {topic}.
            """,
            "key_points": [
                f"{concept} is essential for understanding {topic}",
                f"{concept} has practical applications in various contexts",
                f"Understanding {concept} requires analytical thinking"
            ],
            "examples": [
                f"Real-world example: {concept} in practice",
                f"Case study: {concept} implementation"
            ],
            "personalization": {
                "user_name": user_info.name,
                "grade_level": user_info.grade_level,
                "learning_style": user_info.learning_style_summary
            }
        }
        
        return MockToolResponse(success=True, data={"explanation": explanation})

class SimplifiedOrchestrator:
    """Simplified orchestrator that demonstrates the core workflow."""
    
    def __init__(self):
        self.context_analyzer = SimplifiedContextAnalyzer()
        self.tools = MockEducationalTools()
    
    async def orchestrate(self, context: MockConversationContext) -> MockOrchestratorResponse:
        """Main orchestration method."""
        try:
            logger.info(f"Processing orchestration request for user: {context.user_info.user_id}")
            
            # Step 1: Analyze context
            intent = self.context_analyzer.analyze_context(context)
            logger.info(f"Detected intent: {intent.intent_type} (confidence: {intent.confidence:.2f})")
            
            # Step 2: Fill missing parameters with defaults
            params = intent.extracted_parameters.copy()
            for missing_param in intent.missing_parameters:
                params[missing_param] = self._get_default_value(missing_param, context)
            
            logger.info(f"Final parameters: {list(params.keys())}")
            
            # Step 3: Execute tool
            tool_response = await self._execute_tool(intent.suggested_tool, params, context.user_info)
            
            logger.info(f"Tool execution completed - Success: {tool_response.success}")
            
            return MockOrchestratorResponse(
                success=tool_response.success,
                tool_response=tool_response,
                educational_intent=intent,
                conversation_context=context,
                error_message=tool_response.error if not tool_response.success else None
            )
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return MockOrchestratorResponse(
                success=False,
                error_message=f"Orchestration error: {str(e)}"
            )
    
    def _get_default_value(self, param: str, context: MockConversationContext) -> Any:
        """Get default value for missing parameter."""
        defaults = {
            "topic": "General Topic",
            "subject": "General Subject",
            "count": 10,
            "difficulty": "medium",
            "note_taking_style": "structured",
            "desired_depth": "intermediate",
            "concept_to_explain": context.current_message.split()[0] if context.current_message else "Concept",
            "current_topic": "General Topic"
        }
        return defaults.get(param, "Default Value")
    
    async def _execute_tool(self, tool_name: str, params: Dict[str, Any], user_info: MockUserInfo) -> MockToolResponse:
        """Execute the appropriate educational tool."""
        try:
            if tool_name == "note_maker":
                return await self.tools.note_maker(params, user_info)
            elif tool_name == "flashcard_generator":
                return await self.tools.flashcard_generator(params, user_info)
            elif tool_name == "concept_explainer":
                return await self.tools.concept_explainer(params, user_info)
            else:
                return MockToolResponse(
                    success=False,
                    error=f"Unknown tool: {tool_name}",
                    error_code="UNKNOWN_TOOL"
                )
        except Exception as e:
            return MockToolResponse(
                success=False,
                error=f"Tool execution failed: {str(e)}",
                error_code="EXECUTION_ERROR"
            )

async def run_demo_scenarios():
    """Run demo scenarios to showcase the system."""
    orchestrator = SimplifiedOrchestrator()
    
    scenarios = [
        {
            "name": "Note Making Request",
            "context": MockConversationContext(
                user_info=MockUserInfo(
                    user_id="student_001",
                    name="Alice Johnson",
                    grade_level="9",
                    learning_style_summary="Visual learner, prefers structured notes with diagrams",
                    emotional_state_summary="Focused and engaged in learning",
                    mastery_level_summary="Level 5 - Building foundational knowledge"
                ),
                chat_history=[
                    MockChatMessage("user", "I'm studying biology and need help"),
                    MockChatMessage("assistant", "I'd be happy to help you with biology!")
                ],
                current_message="Can you help me take notes on photosynthesis? I need structured notes with examples.",
                teaching_style="visual",
                emotional_state="focused",
                mastery_level=5
            )
        },
        {
            "name": "Flashcard Generation Request",
            "context": MockConversationContext(
                user_info=MockUserInfo(
                    user_id="student_002",
                    name="Bob Smith",
                    grade_level="11",
                    learning_style_summary="Kinesthetic learner, learns best through practice and repetition",
                    emotional_state_summary="Motivated to improve test scores",
                    mastery_level_summary="Level 7 - Proficient with good understanding"
                ),
                chat_history=[
                    MockChatMessage("user", "I have a vocabulary test coming up"),
                    MockChatMessage("assistant", "I can help you prepare for your vocabulary test!")
                ],
                current_message="I need flashcards to memorize Spanish vocabulary. Can you create 15 flashcards for me?",
                teaching_style="direct",
                emotional_state="focused",
                mastery_level=7
            )
        },
        {
            "name": "Concept Explanation Request",
            "context": MockConversationContext(
                user_info=MockUserInfo(
                    user_id="student_003",
                    name="Charlie Brown",
                    grade_level="12",
                    learning_style_summary="Auditory learner, prefers step-by-step explanations",
                    emotional_state_summary="Confused about advanced concepts",
                    mastery_level_summary="Level 4 - Building foundational knowledge"
                ),
                chat_history=[
                    MockChatMessage("user", "I'm struggling with calculus"),
                    MockChatMessage("assistant", "Calculus can be challenging. What specific concept are you having trouble with?")
                ],
                current_message="Can you explain derivatives in simple terms? I'm really confused about how they work.",
                teaching_style="socratic",
                emotional_state="confused",
                mastery_level=4
            )
        }
    ]
    
    print("AI Tutor Orchestrator - Demo Scenarios")
    print("=" * 50)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario['name']}")
        print("-" * 40)
        
        response = await orchestrator.orchestrate(scenario['context'])
        
        print(f"✓ Success: {response.success}")
        print(f"✓ Intent: {response.educational_intent.intent_type}")
        print(f"✓ Confidence: {response.educational_intent.confidence:.2f}")
        print(f"✓ Tool: {response.educational_intent.suggested_tool}")
        print(f"✓ Parameters: {list(response.educational_intent.extracted_parameters.keys())}")
        
        if response.tool_response and response.tool_response.success:
            print(f"✓ Tool Response: Success")
            if response.tool_response.data:
                data_keys = list(response.tool_response.data.keys())
                print(f"✓ Data Keys: {data_keys}")
        else:
            print(f"✗ Tool Response: Failed")
            if response.tool_response and response.tool_response.error:
                print(f"✗ Error: {response.tool_response.error}")
        
        print()

async def interactive_demo():
    """Run interactive demo."""
    orchestrator = SimplifiedOrchestrator()
    
    print("AI Tutor Orchestrator - Interactive Demo")
    print("=" * 40)
    print("Enter student messages to see how the system responds.")
    print("Type 'quit' to exit.")
    print()
    
    while True:
        user_message = input("Student: ").strip()
        
        if user_message.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_message:
            continue
        
        # Create context
        context = MockConversationContext(
            user_info=MockUserInfo(
                user_id="interactive_user",
                name="Interactive Student",
                grade_level="10",
                learning_style_summary="Mixed learning style",
                emotional_state_summary="Curious and engaged",
                mastery_level_summary="Level 5 - Intermediate understanding"
            ),
            chat_history=[
                MockChatMessage("user", "Hello, I need help with my studies"),
                MockChatMessage("assistant", "I'd be happy to help you with your studies!")
            ],
            current_message=user_message,
            teaching_style="direct",
            emotional_state="focused",
            mastery_level=5
        )
        
        response = await orchestrator.orchestrate(context)
        
        print(f"\nSystem Response:")
        print(f"Intent: {response.educational_intent.intent_type}")
        print(f"Confidence: {response.educational_intent.confidence:.2f}")
        print(f"Tool: {response.educational_intent.suggested_tool}")
        print(f"Success: {response.success}")
        
        if response.tool_response and response.tool_response.success:
            print("✓ Tool executed successfully")
        else:
            print("✗ Tool execution failed")
        
        print()

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_demo())
    else:
        asyncio.run(run_demo_scenarios())

if __name__ == "__main__":
    main()
