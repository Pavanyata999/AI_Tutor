#!/usr/bin/env python3
"""
Demo Scenarios Script
=====================

This script provides various demo scenarios to showcase the AI Tutor Orchestrator
capabilities. It demonstrates different educational intents and tool interactions.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoScenarios:
    """Demo scenarios for the AI Tutor Orchestrator."""
    
    def __init__(self, orchestrator_url: str = "http://localhost:8000"):
        self.orchestrator_url = orchestrator_url
        self.scenarios = self._initialize_scenarios()
    
    def _initialize_scenarios(self) -> List[Dict[str, Any]]:
        """Initialize demo scenarios."""
        return [
            {
                "name": "Note Making Request",
                "description": "Student wants to take notes on photosynthesis",
                "context": {
                    "user_info": {
                        "user_id": "student_001",
                        "name": "Alice Johnson",
                        "grade_level": "9",
                        "learning_style_summary": "Visual learner, prefers structured notes with diagrams",
                        "emotional_state_summary": "Focused and engaged in learning",
                        "mastery_level_summary": "Level 5 - Building foundational knowledge"
                    },
                    "chat_history": [
                        {"role": "user", "content": "I'm studying biology and need help"},
                        {"role": "assistant", "content": "I'd be happy to help you with biology!"}
                    ],
                    "current_message": "Can you help me take notes on photosynthesis? I need structured notes with examples.",
                    "teaching_style": "visual",
                    "emotional_state": "focused",
                    "mastery_level": 5
                },
                "expected_intent": "note_making",
                "expected_tool": "note_maker"
            },
            {
                "name": "Flashcard Generation Request",
                "description": "Student wants flashcards for vocabulary practice",
                "context": {
                    "user_info": {
                        "user_id": "student_002",
                        "name": "Bob Smith",
                        "grade_level": "11",
                        "learning_style_summary": "Kinesthetic learner, learns best through practice and repetition",
                        "emotional_state_summary": "Motivated to improve test scores",
                        "mastery_level_summary": "Level 7 - Proficient with good understanding"
                    },
                    "chat_history": [
                        {"role": "user", "content": "I have a vocabulary test coming up"},
                        {"role": "assistant", "content": "I can help you prepare for your vocabulary test!"}
                    ],
                    "current_message": "I need flashcards to memorize Spanish vocabulary. Can you create 15 flashcards for me?",
                    "teaching_style": "direct",
                    "emotional_state": "focused",
                    "mastery_level": 7
                },
                "expected_intent": "flashcard_generation",
                "expected_tool": "flashcard_generator"
            },
            {
                "name": "Concept Explanation Request",
                "description": "Student needs explanation of complex concept",
                "context": {
                    "user_info": {
                        "user_id": "student_003",
                        "name": "Charlie Brown",
                        "grade_level": "12",
                        "learning_style_summary": "Auditory learner, prefers step-by-step explanations",
                        "emotional_state_summary": "Confused about advanced concepts",
                        "mastery_level_summary": "Level 4 - Building foundational knowledge"
                    },
                    "chat_history": [
                        {"role": "user", "content": "I'm struggling with calculus"},
                        {"role": "assistant", "content": "Calculus can be challenging. What specific concept are you having trouble with?"}
                    ],
                    "current_message": "Can you explain derivatives in simple terms? I'm really confused about how they work.",
                    "teaching_style": "socratic",
                    "emotional_state": "confused",
                    "mastery_level": 4
                },
                "expected_intent": "concept_explanation",
                "expected_tool": "concept_explainer"
            },
            {
                "name": "Anxious Student Request",
                "description": "Anxious student needs simplified approach",
                "context": {
                    "user_info": {
                        "user_id": "student_004",
                        "name": "Diana Prince",
                        "grade_level": "8",
                        "learning_style_summary": "Prefers simple, clear explanations with lots of examples",
                        "emotional_state_summary": "Anxious about upcoming exam",
                        "mastery_level_summary": "Level 3 - Foundation building with scaffolding"
                    },
                    "chat_history": [
                        {"role": "user", "content": "I'm worried about my math test tomorrow"},
                        {"role": "assistant", "content": "It's natural to feel nervous before a test. Let's work through this together."}
                    ],
                    "current_message": "I need help with fractions but I'm really stressed. Can you make it simple?",
                    "teaching_style": "direct",
                    "emotional_state": "anxious",
                    "mastery_level": 3
                },
                "expected_intent": "concept_explanation",
                "expected_tool": "concept_explainer"
            },
            {
                "name": "Advanced Student Request",
                "description": "Advanced student wants challenging content",
                "context": {
                    "user_info": {
                        "user_id": "student_005",
                        "name": "Eve Wilson",
                        "grade_level": "12",
                        "learning_style_summary": "Analytical learner, enjoys complex problems and deep understanding",
                        "emotional_state_summary": "Focused and ready for challenges",
                        "mastery_level_summary": "Level 9 - Advanced application and nuanced understanding"
                    },
                    "chat_history": [
                        {"role": "user", "content": "I'm preparing for advanced placement exams"},
                        {"role": "assistant", "content": "AP exams require deep understanding. What subject are you focusing on?"}
                    ],
                    "current_message": "I need comprehensive notes on quantum mechanics for my AP Physics exam. Include advanced applications and theoretical frameworks.",
                    "teaching_style": "flipped_classroom",
                    "emotional_state": "focused",
                    "mastery_level": 9
                },
                "expected_intent": "note_making",
                "expected_tool": "note_maker"
            }
        ]
    
    async def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single demo scenario."""
        logger.info(f"Running scenario: {scenario['name']}")
        logger.info(f"Description: {scenario['description']}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start_time = time.time()
                
                response = await client.post(
                    f"{self.orchestrator_url}/orchestrate",
                    json=scenario["context"]
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Analyze results
                    success = result.get("success", False)
                    intent = result.get("educational_intent", {})
                    tool_response = result.get("tool_response", {})
                    
                    scenario_result = {
                        "scenario_name": scenario["name"],
                        "success": success,
                        "response_time": response_time,
                        "detected_intent": intent.get("intent_type", "unknown"),
                        "expected_intent": scenario["expected_intent"],
                        "intent_match": intent.get("intent_type") == scenario["expected_intent"],
                        "confidence": intent.get("confidence", 0.0),
                        "suggested_tool": intent.get("suggested_tool", "unknown"),
                        "expected_tool": scenario["expected_tool"],
                        "tool_match": intent.get("suggested_tool") == scenario["expected_tool"],
                        "tool_success": tool_response.get("success", False),
                        "extracted_parameters": intent.get("extracted_parameters", {}),
                        "missing_parameters": intent.get("missing_parameters", []),
                        "error_message": result.get("error_message")
                    }
                    
                    logger.info(f"✓ Scenario completed successfully")
                    logger.info(f"  Intent: {scenario_result['detected_intent']} (confidence: {scenario_result['confidence']:.2f})")
                    logger.info(f"  Tool: {scenario_result['suggested_tool']}")
                    logger.info(f"  Response time: {response_time:.2f}s")
                    
                    return scenario_result
                
                else:
                    logger.error(f"✗ Scenario failed with status {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    
                    return {
                        "scenario_name": scenario["name"],
                        "success": False,
                        "response_time": response_time,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
        
        except Exception as e:
            logger.error(f"✗ Scenario failed with exception: {e}")
            return {
                "scenario_name": scenario["name"],
                "success": False,
                "error": str(e)
            }
    
    async def run_all_scenarios(self) -> List[Dict[str, Any]]:
        """Run all demo scenarios."""
        logger.info("Starting AI Tutor Orchestrator Demo Scenarios")
        logger.info("=" * 60)
        
        results = []
        
        for i, scenario in enumerate(self.scenarios, 1):
            logger.info(f"\nScenario {i}/{len(self.scenarios)}")
            logger.info("-" * 40)
            
            result = await self.run_scenario(scenario)
            results.append(result)
            
            # Small delay between scenarios
            await asyncio.sleep(1)
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the results of all scenarios."""
        total_scenarios = len(results)
        successful_scenarios = sum(1 for r in results if r.get("success", False))
        
        intent_matches = sum(1 for r in results if r.get("intent_match", False))
        tool_matches = sum(1 for r in results if r.get("tool_match", False))
        tool_successes = sum(1 for r in results if r.get("tool_success", False))
        
        avg_response_time = sum(r.get("response_time", 0) for r in results) / total_scenarios
        avg_confidence = sum(r.get("confidence", 0) for r in results) / total_scenarios
        
        analysis = {
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "success_rate": successful_scenarios / total_scenarios,
            "intent_accuracy": intent_matches / total_scenarios,
            "tool_accuracy": tool_matches / total_scenarios,
            "tool_success_rate": tool_successes / total_scenarios,
            "average_response_time": avg_response_time,
            "average_confidence": avg_confidence,
            "scenario_results": results
        }
        
        return analysis
    
    def print_summary(self, analysis: Dict[str, Any]):
        """Print a summary of the demo results."""
        logger.info("\n" + "=" * 60)
        logger.info("DEMO SCENARIOS SUMMARY")
        logger.info("=" * 60)
        
        logger.info(f"Total Scenarios: {analysis['total_scenarios']}")
        logger.info(f"Successful Scenarios: {analysis['successful_scenarios']}")
        logger.info(f"Success Rate: {analysis['success_rate']:.1%}")
        logger.info(f"Intent Accuracy: {analysis['intent_accuracy']:.1%}")
        logger.info(f"Tool Accuracy: {analysis['tool_accuracy']:.1%}")
        logger.info(f"Tool Success Rate: {analysis['tool_success_rate']:.1%}")
        logger.info(f"Average Response Time: {analysis['average_response_time']:.2f}s")
        logger.info(f"Average Confidence: {analysis['average_confidence']:.2f}")
        
        logger.info("\nDetailed Results:")
        logger.info("-" * 40)
        
        for result in analysis["scenario_results"]:
            status = "✓" if result.get("success", False) else "✗"
            intent_status = "✓" if result.get("intent_match", False) else "✗"
            tool_status = "✓" if result.get("tool_match", False) else "✗"
            
            logger.info(f"{status} {result['scenario_name']}")
            logger.info(f"  Intent: {result.get('detected_intent', 'unknown')} {intent_status}")
            logger.info(f"  Tool: {result.get('suggested_tool', 'unknown')} {tool_status}")
            logger.info(f"  Time: {result.get('response_time', 0):.2f}s")
            
            if result.get("error"):
                logger.info(f"  Error: {result['error']}")
    
    async def run_interactive_demo(self):
        """Run an interactive demo where user can input custom scenarios."""
        logger.info("Interactive Demo Mode")
        logger.info("=" * 30)
        
        while True:
            print("\nEnter a student message (or 'quit' to exit):")
            user_message = input("> ").strip()
            
            if user_message.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_message:
                continue
            
            # Create a simple context
            context = {
                "user_info": {
                    "user_id": "interactive_user",
                    "name": "Interactive Student",
                    "grade_level": "10",
                    "learning_style_summary": "Mixed learning style",
                    "emotional_state_summary": "Curious and engaged",
                    "mastery_level_summary": "Level 5 - Intermediate understanding"
                },
                "chat_history": [
                    {"role": "user", "content": "Hello, I need help with my studies"},
                    {"role": "assistant", "content": "I'd be happy to help you with your studies!"}
                ],
                "current_message": user_message,
                "teaching_style": "direct",
                "emotional_state": "focused",
                "mastery_level": 5
            }
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.orchestrator_url}/orchestrate",
                        json=context
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        intent = result.get("educational_intent", {})
                        
                        print(f"\nDetected Intent: {intent.get('intent_type', 'unknown')}")
                        print(f"Confidence: {intent.get('confidence', 0):.2f}")
                        print(f"Suggested Tool: {intent.get('suggested_tool', 'unknown')}")
                        print(f"Success: {result.get('success', False)}")
                        
                        if intent.get("extracted_parameters"):
                            print("Extracted Parameters:")
                            for key, value in intent["extracted_parameters"].items():
                                print(f"  {key}: {value}")
                    
                    else:
                        print(f"Error: HTTP {response.status_code}")
                        print(response.text)
            
            except Exception as e:
                print(f"Error: {e}")

async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Tutor Orchestrator Demo Scenarios")
    parser.add_argument("--url", default="http://localhost:8000", help="Orchestrator URL")
    parser.add_argument("--interactive", action="store_true", help="Run interactive demo")
    parser.add_argument("--scenario", type=int, help="Run specific scenario number")
    
    args = parser.parse_args()
    
    demo = DemoScenarios(args.url)
    
    if args.interactive:
        await demo.run_interactive_demo()
    elif args.scenario:
        if 1 <= args.scenario <= len(demo.scenarios):
            scenario = demo.scenarios[args.scenario - 1]
            result = await demo.run_scenario(scenario)
            print(json.dumps(result, indent=2))
        else:
            print(f"Invalid scenario number. Choose 1-{len(demo.scenarios)}")
    else:
        results = await demo.run_all_scenarios()
        analysis = demo.analyze_results(results)
        demo.print_summary(analysis)

if __name__ == "__main__":
    asyncio.run(main())
