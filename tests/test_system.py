import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

from models import (
    UserInfo, ChatMessage, ConversationContext, EducationalIntent,
    TeachingStyle, EmotionalState, NoteTakingStyle, DifficultyLevel, ExplanationDepth
)
from context_analyzer import ContextAnalyzer
from parameter_extractor import ParameterExtractor
from tool_orchestrator import ToolOrchestrator
from schema_validator import SchemaValidator
from state_manager import StateManager

# Test fixtures
@pytest.fixture
def sample_user_info():
    return UserInfo(
        user_id="test_user_123",
        name="Test Student",
        grade_level="10",
        learning_style_summary="Visual learner, prefers diagrams and examples",
        emotional_state_summary="Focused and motivated to learn",
        mastery_level_summary="Level 6 - Good understanding, ready for application"
    )

@pytest.fixture
def sample_chat_history():
    return [
        ChatMessage(role="user", content="I need help with calculus derivatives"),
        ChatMessage(role="assistant", content="I'd be happy to help you with calculus derivatives!"),
        ChatMessage(role="user", content="Can you explain the chain rule?")
    ]

@pytest.fixture
def sample_conversation_context(sample_user_info, sample_chat_history):
    return ConversationContext(
        user_info=sample_user_info,
        chat_history=sample_chat_history,
        current_message="I'm struggling with calculus derivatives and need some practice problems",
        teaching_style=TeachingStyle.VISUAL,
        emotional_state=EmotionalState.FOCUSED,
        mastery_level=6
    )

@pytest.fixture
def mock_openai_api_key():
    return "test_openai_key"

# Context Analyzer Tests
class TestContextAnalyzer:
    
    @pytest.fixture
    def context_analyzer(self, mock_openai_api_key):
        with patch('context_analyzer.OpenAI'):
            return ContextAnalyzer(mock_openai_api_key)
    
    def test_intent_patterns_initialization(self, context_analyzer):
        """Test that intent patterns are properly initialized."""
        assert "note_making" in context_analyzer.intent_patterns
        assert "flashcard_generation" in context_analyzer.intent_patterns
        assert "concept_explanation" in context_analyzer.intent_patterns
        assert "quiz_generation" in context_analyzer.intent_patterns
    
    def test_parameter_patterns_initialization(self, context_analyzer):
        """Test that parameter patterns are properly initialized."""
        assert "topic" in context_analyzer.parameter_patterns
        assert "subject" in context_analyzer.parameter_patterns
        assert "difficulty" in context_analyzer.parameter_patterns
        assert "count" in context_analyzer.parameter_patterns
    
    def test_detect_intent_note_making(self, context_analyzer):
        """Test intent detection for note making."""
        message = "I need to take notes on photosynthesis"
        intent_type, confidence = context_analyzer._detect_intent(message)
        assert intent_type == "note_making"
        assert confidence > 0
    
    def test_detect_intent_flashcard_generation(self, context_analyzer):
        """Test intent detection for flashcard generation."""
        message = "Can you create flashcards for me to memorize vocabulary?"
        intent_type, confidence = context_analyzer._detect_intent(message)
        assert intent_type == "flashcard_generation"
        assert confidence > 0
    
    def test_detect_intent_concept_explanation(self, context_analyzer):
        """Test intent detection for concept explanation."""
        message = "Can you explain how photosynthesis works?"
        intent_type, confidence = context_analyzer._detect_intent(message)
        assert intent_type == "concept_explanation"
        assert confidence > 0
    
    def test_extract_topic_from_message(self, context_analyzer, sample_chat_history):
        """Test topic extraction from message."""
        message = "I want to learn about water cycle"
        topic = context_analyzer._extract_topic(message, sample_chat_history)
        assert topic is not None
        assert "water cycle" in topic.lower()
    
    def test_extract_subject_from_message(self, context_analyzer, sample_chat_history):
        """Test subject extraction from message."""
        message = "I need help with calculus"
        subject = context_analyzer._extract_subject(message, sample_chat_history)
        assert subject is not None
        assert "calculus" in subject.lower()
    
    def test_infer_difficulty_confused_state(self, context_analyzer, sample_conversation_context):
        """Test difficulty inference for confused emotional state."""
        context = sample_conversation_context
        context.emotional_state = EmotionalState.CONFUSED
        difficulty = context_analyzer._infer_difficulty(context)
        assert difficulty == "easy"
    
    def test_infer_difficulty_focused_state(self, context_analyzer, sample_conversation_context):
        """Test difficulty inference for focused emotional state."""
        context = sample_conversation_context
        context.emotional_state = EmotionalState.FOCUSED
        context.mastery_level = 8
        difficulty = context_analyzer._infer_difficulty(context)
        assert difficulty == "hard"
    
    def test_infer_note_style_visual_learner(self, context_analyzer, sample_conversation_context):
        """Test note style inference for visual learner."""
        context = sample_conversation_context
        context.user_info.learning_style_summary = "Visual learner, prefers diagrams"
        note_style = context_analyzer._infer_note_style(context)
        assert note_style in ["outline", "bullet_points", "narrative", "structured"]
    
    def test_map_intent_to_tool(self, context_analyzer):
        """Test mapping of intent to tool."""
        assert context_analyzer._map_intent_to_tool("note_making") == "note_maker"
        assert context_analyzer._map_intent_to_tool("flashcard_generation") == "flashcard_generator"
        assert context_analyzer._map_intent_to_tool("concept_explanation") == "concept_explainer"
        assert context_analyzer._map_intent_to_tool("unknown") == "unknown"
    
    def test_identify_missing_parameters(self, context_analyzer):
        """Test identification of missing parameters."""
        params = {"topic": "test", "subject": "math"}
        missing = context_analyzer._identify_missing_parameters("note_making", params)
        assert "note_taking_style" in missing

# Parameter Extractor Tests
class TestParameterExtractor:
    
    @pytest.fixture
    def parameter_extractor(self, mock_openai_api_key):
        with patch('parameter_extractor.OpenAI'):
            return ParameterExtractor(mock_openai_api_key)
    
    def test_tool_schemas_initialization(self, parameter_extractor):
        """Test that tool schemas are properly initialized."""
        assert "note_maker" in parameter_extractor.tool_schemas
        assert "flashcard_generator" in parameter_extractor.tool_schemas
        assert "concept_explainer" in parameter_extractor.tool_schemas
    
    def test_extract_parameters_success(self, parameter_extractor, sample_conversation_context):
        """Test successful parameter extraction."""
        intent = EducationalIntent(
            intent_type="note_making",
            confidence=0.8,
            extracted_parameters={"topic": "photosynthesis", "subject": "biology"},
            missing_parameters=[],
            suggested_tool="note_maker"
        )
        
        result = parameter_extractor.extract_parameters(intent, sample_conversation_context)
        assert result.success is True
        assert "user_info" in result.extracted_parameters
        assert "chat_history" in result.extracted_parameters
    
    def test_infer_note_maker_params(self, parameter_extractor, sample_conversation_context):
        """Test parameter inference for note maker."""
        params = parameter_extractor._infer_note_maker_params(sample_conversation_context)
        assert "note_taking_style" in params
        assert "include_examples" in params
        assert "include_analogies" in params
    
    def test_infer_flashcard_params(self, parameter_extractor, sample_conversation_context):
        """Test parameter inference for flashcard generator."""
        params = parameter_extractor._infer_flashcard_params(sample_conversation_context)
        assert "count" in params
        assert "difficulty" in params
        assert "include_examples" in params
    
    def test_infer_concept_explainer_params(self, parameter_extractor, sample_conversation_context):
        """Test parameter inference for concept explainer."""
        params = parameter_extractor._infer_concept_explainer_params(sample_conversation_context)
        assert "desired_depth" in params
    
    def test_assign_default_values(self, parameter_extractor, sample_conversation_context):
        """Test assignment of default values."""
        defaults = parameter_extractor._assign_default_values("note_maker", sample_conversation_context)
        assert "include_examples" in defaults
        assert "include_analogies" in defaults
    
    def test_validate_parameters(self, parameter_extractor):
        """Test parameter validation."""
        params = {
            "user_info": {"user_id": "test"},
            "chat_history": [],
            "topic": "test",
            "subject": "math",
            "note_taking_style": "outline"
        }
        
        validated, missing = parameter_extractor._validate_parameters(params, "note_maker")
        assert len(missing) == 0
        assert "user_info" in validated
        assert "topic" in validated

# Schema Validator Tests
class TestSchemaValidator:
    
    @pytest.fixture
    def schema_validator(self):
        return SchemaValidator()
    
    def test_tool_schemas_initialization(self, schema_validator):
        """Test that tool schemas are properly initialized."""
        assert "note_maker" in schema_validator.tool_schemas
        assert "flashcard_generator" in schema_validator.tool_schemas
        assert "concept_explainer" in schema_validator.tool_schemas
    
    def test_validate_tool_request_success(self, schema_validator, sample_user_info, sample_chat_history):
        """Test successful tool request validation."""
        from models import ToolRequest
        
        tool_request = ToolRequest(
            tool_name="note_maker",
            parameters={
                "user_info": sample_user_info.dict(),
                "chat_history": [msg.dict() for msg in sample_chat_history],
                "topic": "photosynthesis",
                "subject": "biology",
                "note_taking_style": "outline"
            },
            user_info=sample_user_info,
            chat_history=sample_chat_history
        )
        
        result = schema_validator.validate_tool_request(tool_request)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_tool_request_missing_required(self, schema_validator, sample_user_info, sample_chat_history):
        """Test validation with missing required parameters."""
        from models import ToolRequest
        
        tool_request = ToolRequest(
            tool_name="note_maker",
            parameters={
                "user_info": sample_user_info.dict(),
                "chat_history": [msg.dict() for msg in sample_chat_history],
                "topic": "photosynthesis"
                # Missing subject and note_taking_style
            },
            user_info=sample_user_info,
            chat_history=sample_chat_history
        )
        
        result = schema_validator.validate_tool_request(tool_request)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validate_tool_request_invalid_tool(self, schema_validator, sample_user_info, sample_chat_history):
        """Test validation with invalid tool name."""
        from models import ToolRequest
        
        tool_request = ToolRequest(
            tool_name="invalid_tool",
            parameters={},
            user_info=sample_user_info,
            chat_history=sample_chat_history
        )
        
        result = schema_validator.validate_tool_request(tool_request)
        assert result.is_valid is False
        assert "Unknown tool" in result.errors[0]["message"]
    
    def test_validate_user_info(self, schema_validator):
        """Test user info validation."""
        user_info = {
            "user_id": "test",
            "name": "Test Student",
            "grade_level": "10",
            "learning_style_summary": "Visual learner",
            "emotional_state_summary": "Focused",
            "mastery_level_summary": "Level 6"
        }
        
        result = schema_validator._validate_user_info(user_info)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_chat_history(self, schema_validator):
        """Test chat history validation."""
        chat_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        result = schema_validator._validate_chat_history(chat_history)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    def test_sanitize_input(self, schema_validator):
        """Test input sanitization."""
        data = {
            "text": "  Test text with\x00null character  ",
            "nested": {
                "value": "Another\x00value"
            },
            "list": ["Item1", "Item2\x00"]
        }
        
        sanitized = schema_validator.sanitize_input(data)
        assert "\x00" not in sanitized["text"]
        assert "\x00" not in sanitized["nested"]["value"]
        assert "\x00" not in sanitized["list"][1]

# State Manager Tests
class TestStateManager:
    
    @pytest.fixture
    def state_manager(self):
        return StateManager()
    
    def test_create_student_profile(self, state_manager, sample_user_info):
        """Test student profile creation."""
        profile = state_manager.create_student_profile(sample_user_info)
        
        assert profile.user_id == sample_user_info.user_id
        assert profile.name == sample_user_info.name
        assert profile.teaching_style is not None
        assert profile.emotional_state is not None
        assert profile.mastery_level is not None
    
    def test_get_student_profile(self, state_manager, sample_user_info):
        """Test student profile retrieval."""
        state_manager.create_student_profile(sample_user_info)
        profile = state_manager.get_student_profile(sample_user_info.user_id)
        
        assert profile is not None
        assert profile.user_id == sample_user_info.user_id
    
    def test_update_student_profile(self, state_manager, sample_user_info):
        """Test student profile updates."""
        state_manager.create_student_profile(sample_user_info)
        
        updates = {"mastery_level": 8}
        success = state_manager.update_student_profile(sample_user_info.user_id, updates)
        
        assert success is True
        profile = state_manager.get_student_profile(sample_user_info.user_id)
        assert profile.mastery_level == 8
    
    def test_create_session(self, state_manager, sample_user_info):
        """Test session creation."""
        state_manager.create_student_profile(sample_user_info)
        session = state_manager.create_session(sample_user_info.user_id, "session_123")
        
        assert session.session_id == "session_123"
        assert session.user_id == sample_user_info.user_id
        assert len(session.chat_history) == 0
    
    def test_add_message_to_session(self, state_manager, sample_user_info):
        """Test adding messages to session."""
        state_manager.create_student_profile(sample_user_info)
        session = state_manager.create_session(sample_user_info.user_id, "session_123")
        
        message = ChatMessage(role="user", content="Hello")
        success = state_manager.add_message_to_session("session_123", message)
        
        assert success is True
        retrieved_session = state_manager.get_session("session_123")
        assert len(retrieved_session.chat_history) == 1
    
    def test_add_tool_interaction(self, state_manager, sample_user_info):
        """Test adding tool interactions to session."""
        state_manager.create_student_profile(sample_user_info)
        session = state_manager.create_session(sample_user_info.user_id, "session_123")
        
        request = {"tool": "note_maker", "params": {}}
        response = {"success": True, "data": {}}
        
        success = state_manager.add_tool_interaction("session_123", "note_maker", request, response)
        
        assert success is True
        retrieved_session = state_manager.get_session("session_123")
        assert len(retrieved_session.tool_interactions) == 1
    
    def test_get_conversation_context(self, state_manager, sample_user_info, sample_chat_history):
        """Test conversation context retrieval."""
        state_manager.create_student_profile(sample_user_info)
        session = state_manager.create_session(sample_user_info.user_id, "session_123")
        
        # Add messages to session
        for message in sample_chat_history:
            state_manager.add_message_to_session("session_123", message)
        
        context = state_manager.get_conversation_context("session_123")
        
        assert context is not None
        assert context.user_info.user_id == sample_user_info.user_id
        assert len(context.chat_history) == len(sample_chat_history)
    
    def test_update_learning_progress(self, state_manager, sample_user_info):
        """Test learning progress updates."""
        state_manager.create_student_profile(sample_user_info)
        
        progress_data = {"mastery_increase": 1, "topic": "calculus"}
        success = state_manager.update_learning_progress(sample_user_info.user_id, "calculus", progress_data)
        
        assert success is True
        profile = state_manager.get_student_profile(sample_user_info.user_id)
        assert len(profile.learning_history) == 1
    
    def test_get_learning_recommendations(self, state_manager, sample_user_info):
        """Test learning recommendations."""
        state_manager.create_student_profile(sample_user_info)
        
        recommendations = state_manager.get_learning_recommendations(sample_user_info.user_id)
        
        assert len(recommendations) > 0
        assert isinstance(recommendations, list)
    
    def test_get_statistics(self, state_manager, sample_user_info):
        """Test system statistics."""
        state_manager.create_student_profile(sample_user_info)
        state_manager.create_session(sample_user_info.user_id, "session_123")
        
        stats = state_manager.get_statistics()
        
        assert "total_students" in stats
        assert "active_sessions" in stats
        assert "total_interactions" in stats
        assert stats["total_students"] == 1
        assert stats["active_sessions"] == 1

# Integration Tests
class TestIntegration:
    
    @pytest.fixture
    def mock_config(self):
        return {
            "NOTE_MAKER_URL": "http://localhost:8001",
            "FLASHCARD_GENERATOR_URL": "http://localhost:8002",
            "CONCEPT_EXPLAINER_URL": "http://localhost:8003"
        }
    
    @pytest.mark.asyncio
    async def test_orchestration_workflow(self, mock_openai_api_key, mock_config, sample_conversation_context):
        """Test complete orchestration workflow."""
        with patch('tool_orchestrator.OpenAI'), \
             patch('tool_orchestrator.httpx.AsyncClient') as mock_client:
            
            # Mock HTTP response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True, "data": {"notes": "test notes"}}
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            orchestrator = ToolOrchestrator(mock_openai_api_key, mock_config)
            response = await orchestrator.orchestrate(sample_conversation_context)
            
            assert response is not None
            assert hasattr(response, 'success')
    
    def test_end_to_end_parameter_extraction(self, mock_openai_api_key, sample_conversation_context):
        """Test end-to-end parameter extraction."""
        with patch('context_analyzer.OpenAI'), \
             patch('parameter_extractor.OpenAI'):
            
            context_analyzer = ContextAnalyzer(mock_openai_api_key)
            parameter_extractor = ParameterExtractor(mock_openai_api_key)
            
            # Analyze context
            intent = context_analyzer.analyze_context(sample_conversation_context)
            
            # Extract parameters
            result = parameter_extractor.extract_parameters(intent, sample_conversation_context)
            
            assert result is not None
            assert hasattr(result, 'success')
            assert hasattr(result, 'extracted_parameters')

# Performance Tests
class TestPerformance:
    
    @pytest.fixture
    def large_chat_history(self):
        """Create a large chat history for performance testing."""
        return [
            ChatMessage(role="user", content=f"Message {i}")
            for i in range(100)
        ]
    
    def test_large_chat_history_processing(self, mock_openai_api_key, sample_user_info, large_chat_history):
        """Test processing of large chat history."""
        with patch('context_analyzer.OpenAI'):
            context_analyzer = ContextAnalyzer(mock_openai_api_key)
            
            context = ConversationContext(
                user_info=sample_user_info,
                chat_history=large_chat_history,
                current_message="Test message",
                teaching_style=TeachingStyle.DIRECT,
                emotional_state=EmotionalState.FOCUSED,
                mastery_level=5
            )
            
            # Should handle large chat history without issues
            intent = context_analyzer.analyze_context(context)
            assert intent is not None
    
    def test_concurrent_session_management(self, sample_user_info):
        """Test concurrent session management."""
        state_manager = StateManager()
        
        # Create multiple sessions concurrently
        sessions = []
        for i in range(10):
            session = state_manager.create_session(sample_user_info.user_id, f"session_{i}")
            sessions.append(session)
        
        # Verify all sessions were created
        assert len(state_manager.active_sessions) == 10
        
        # Test concurrent access
        for session in sessions:
            retrieved = state_manager.get_session(session.session_id)
            assert retrieved is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
