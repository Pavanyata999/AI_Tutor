#!/usr/bin/env python3
"""
Detailed Example Script
=======================

This script shows detailed output from the AI Tutor Orchestrator
to demonstrate the complete functionality.
"""

import asyncio
import json
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from demo import SimplifiedOrchestrator, MockConversationContext, MockUserInfo, MockChatMessage

async def show_detailed_example():
    """Show a detailed example of the orchestrator in action."""
    print("🎓 AI Tutor Orchestrator - Detailed Example")
    print("=" * 60)
    
    # Create a realistic scenario
    context = MockConversationContext(
        user_info=MockUserInfo(
            user_id="student_alice_001",
            name="Alice Johnson",
            grade_level="11",
            learning_style_summary="Visual learner, prefers structured notes with diagrams and examples",
            emotional_state_summary="Focused and motivated to improve test scores",
            mastery_level_summary="Level 7 - Proficient with good understanding"
        ),
        chat_history=[
            MockChatMessage("user", "I'm studying for my AP Biology exam"),
            MockChatMessage("assistant", "That's great! AP Biology covers many important topics. What specific area would you like help with?"),
            MockChatMessage("user", "I'm having trouble with cellular respiration"),
            MockChatMessage("assistant", "Cellular respiration is a complex process. Would you like me to explain the concepts or help you practice with questions?")
        ],
        current_message="Can you create flashcards for cellular respiration? I need about 12 cards to memorize the key steps and molecules.",
        teaching_style="visual",
        emotional_state="focused",
        mastery_level=7
    )
    
    print("👤 Student Profile:")
    print(f"   Name: {context.user_info.name}")
    print(f"   Grade: {context.user_info.grade_level}")
    print(f"   Learning Style: {context.user_info.learning_style_summary}")
    print(f"   Emotional State: {context.user_info.emotional_state_summary}")
    print(f"   Mastery Level: {context.user_info.mastery_level_summary}")
    
    print(f"\n💬 Current Message: '{context.current_message}'")
    
    print(f"\n🔄 Processing Request...")
    
    # Run orchestrator
    orchestrator = SimplifiedOrchestrator()
    response = await orchestrator.orchestrate(context)
    
    print(f"\n🧠 Context Analysis Results:")
    intent = response.educational_intent
    print(f"   Detected Intent: {intent.intent_type}")
    print(f"   Confidence Score: {intent.confidence:.2f}")
    print(f"   Suggested Tool: {intent.suggested_tool}")
    
    print(f"\n📋 Extracted Parameters:")
    for key, value in intent.extracted_parameters.items():
        print(f"   {key}: {value}")
    
    if intent.missing_parameters:
        print(f"\n⚠️  Missing Parameters (filled with defaults):")
        for param in intent.missing_parameters:
            print(f"   {param}")
    
    print(f"\n🔧 Tool Execution Results:")
    tool_response = response.tool_response
    print(f"   Success: {tool_response.success}")
    
    if tool_response.success and tool_response.data:
        print(f"\n📦 Generated Content:")
        
        if "flashcards" in tool_response.data:
            flashcards = tool_response.data["flashcards"]
            print(f"   Generated {len(flashcards)} flashcards")
            
            print(f"\n📚 Sample Flashcards:")
            for i, card in enumerate(flashcards[:3], 1):  # Show first 3 cards
                print(f"   Card {i}:")
                print(f"     Front: {card['front']}")
                print(f"     Back: {card['back'][:100]}...")
                print(f"     Difficulty: {card['difficulty']}")
                print(f"     Examples: {len(card.get('examples', []))} examples")
                print()
        
        if "metadata" in tool_response.data:
            metadata = tool_response.data["metadata"]
            print(f"   Metadata:")
            print(f"     User: {metadata.get('user_name', 'N/A')}")
            print(f"     Generated: {metadata.get('generation_timestamp', 'N/A')}")
    
    print(f"\n✅ Overall Success: {response.success}")
    
    if response.success:
        print(f"\n🎉 SUCCESS! The AI Tutor Orchestrator successfully:")
        print(f"   • Analyzed the student's request")
        print(f"   • Detected the educational intent")
        print(f"   • Extracted relevant parameters")
        print(f"   • Selected the appropriate tool")
        print(f"   • Generated personalized educational content")
        print(f"   • Adapted content based on student profile")
    else:
        print(f"\n❌ FAILED: {response.error_message}")

async def show_personalization_example():
    """Show how personalization affects the output."""
    print(f"\n\n🎯 Personalization Example")
    print("=" * 60)
    
    # Same request, different student profiles
    base_message = "I need help understanding photosynthesis"
    
    profiles = [
        {
            "name": "Confused Beginner",
            "emotional_state": "confused",
            "mastery_level": 3,
            "learning_style": "Prefers simple explanations with lots of examples"
        },
        {
            "name": "Advanced Student", 
            "emotional_state": "focused",
            "mastery_level": 9,
            "learning_style": "Analytical learner, enjoys complex problems"
        }
    ]
    
    orchestrator = SimplifiedOrchestrator()
    
    for profile in profiles:
        print(f"\n👤 {profile['name']}:")
        
        context = MockConversationContext(
            user_info=MockUserInfo(
                user_id=f"student_{profile['name'].lower().replace(' ', '_')}",
                name=profile['name'],
                grade_level="10",
                learning_style_summary=profile['learning_style'],
                emotional_state_summary=f"{profile['emotional_state']} and engaged",
                mastery_level_summary=f"Level {profile['mastery_level']} - {'Foundation' if profile['mastery_level'] <= 3 else 'Advanced' if profile['mastery_level'] >= 7 else 'Intermediate'}"
            ),
            chat_history=[
                MockChatMessage("user", "I need help with biology"),
                MockChatMessage("assistant", "I'd be happy to help!")
            ],
            current_message=base_message,
            emotional_state=profile['emotional_state'],
            mastery_level=profile['mastery_level']
        )
        
        response = await orchestrator.orchestrate(context)
        
        if response.success and response.tool_response.data:
            intent = response.educational_intent
            print(f"   Intent: {intent.intent_type}")
            print(f"   Difficulty: {intent.extracted_parameters.get('difficulty', 'N/A')}")
            print(f"   Depth: {intent.extracted_parameters.get('desired_depth', 'N/A')}")
            
            if "explanation" in response.tool_response.data:
                explanation = response.tool_response.data["explanation"]
                print(f"   Explanation Level: {explanation.get('depth_level', 'N/A')}")
                print(f"   Key Points: {len(explanation.get('key_points', []))} points")

if __name__ == "__main__":
    asyncio.run(show_detailed_example())
    asyncio.run(show_personalization_example())
