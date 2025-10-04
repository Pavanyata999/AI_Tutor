#!/usr/bin/env python3
"""
Simple Test Script for AI Tutor Orchestrator
============================================

This script demonstrates the core functionality of the AI Tutor Orchestrator
with a few test cases.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from demo import SimplifiedOrchestrator, MockConversationContext, MockUserInfo, MockChatMessage

async def test_scenario(name: str, message: str, expected_intent: str):
    """Test a single scenario."""
    print(f"\n🧪 Testing: {name}")
    print(f"📝 Message: '{message}'")
    print(f"🎯 Expected Intent: {expected_intent}")
    
    # Create context
    context = MockConversationContext(
        user_info=MockUserInfo(
            user_id="test_user",
            name="Test Student",
            grade_level="10",
            learning_style_summary="Visual learner, prefers examples",
            emotional_state_summary="Focused and motivated",
            mastery_level_summary="Level 6 - Good understanding"
        ),
        chat_history=[
            MockChatMessage("user", "Hello, I need help"),
            MockChatMessage("assistant", "I'd be happy to help!")
        ],
        current_message=message,
        teaching_style="visual",
        emotional_state="focused",
        mastery_level=6
    )
    
    # Run orchestrator
    orchestrator = SimplifiedOrchestrator()
    response = await orchestrator.orchestrate(context)
    
    # Check results
    actual_intent = response.educational_intent.intent_type
    confidence = response.educational_intent.confidence
    success = response.success
    
    print(f"✅ Detected Intent: {actual_intent}")
    print(f"📊 Confidence: {confidence:.2f}")
    print(f"🔧 Tool: {response.educational_intent.suggested_tool}")
    print(f"🎯 Success: {success}")
    
    if actual_intent == expected_intent:
        print("✅ Intent detection CORRECT")
    else:
        print(f"❌ Intent detection INCORRECT (expected {expected_intent})")
    
    if success:
        print("✅ Tool execution SUCCESSFUL")
        if response.tool_response and response.tool_response.data:
            data_keys = list(response.tool_response.data.keys())
            print(f"📦 Generated data: {data_keys}")
    else:
        print("❌ Tool execution FAILED")
        if response.tool_response and response.tool_response.error:
            print(f"❌ Error: {response.tool_response.error}")
    
    return actual_intent == expected_intent and success

async def main():
    """Run all test scenarios."""
    print("🚀 AI Tutor Orchestrator - Test Suite")
    print("=" * 50)
    
    test_cases = [
        ("Note Making", "Can you help me take notes on photosynthesis?", "note_making"),
        ("Flashcard Generation", "I need flashcards to memorize Spanish vocabulary", "flashcard_generation"),
        ("Concept Explanation", "Can you explain derivatives in simple terms?", "concept_explanation"),
        ("Quiz Generation", "I need practice problems for calculus", "quiz_generation"),
        ("Mixed Request", "I'm struggling with biology and need help understanding cells", "concept_explanation"),
    ]
    
    results = []
    
    for name, message, expected_intent in test_cases:
        result = await test_scenario(name, message, expected_intent)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {passed/total:.1%}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The AI Tutor Orchestrator is working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the implementation.")
    
    print("\n🔍 Key Features Demonstrated:")
    print("  • Intent detection from natural language")
    print("  • Parameter extraction from conversation context")
    print("  • Tool selection and execution")
    print("  • Personalization based on user profile")
    print("  • Error handling and validation")
    print("  • Response formatting and data generation")

if __name__ == "__main__":
    asyncio.run(main())
