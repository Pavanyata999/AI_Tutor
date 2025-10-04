import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from models import UserInfo, ChatMessage, ConversationContext, TeachingStyle, EmotionalState

logger = logging.getLogger(__name__)

@dataclass
class StudentProfile:
    """Comprehensive student profile for personalization."""
    user_id: str
    name: str
    grade_level: str
    learning_style_summary: str
    emotional_state_summary: str
    mastery_level_summary: str
    teaching_style: Optional[TeachingStyle] = None
    emotional_state: Optional[EmotionalState] = None
    mastery_level: Optional[int] = None
    preferences: Dict[str, Any] = None
    learning_history: List[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.learning_history is None:
            self.learning_history = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class ConversationSession:
    """Represents a conversation session with state management."""
    session_id: str
    user_id: str
    chat_history: List[ChatMessage]
    current_context: Optional[ConversationContext] = None
    session_start: datetime = None
    last_activity: datetime = None
    tool_interactions: List[Dict[str, Any]] = None
    learning_objectives: List[str] = None
    progress_tracking: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.session_start is None:
            self.session_start = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.tool_interactions is None:
            self.tool_interactions = []
        if self.learning_objectives is None:
            self.learning_objectives = []
        if self.progress_tracking is None:
            self.progress_tracking = {}

class StateManager:
    """
    Manages conversation state and student context across sessions.
    Handles personalization, learning progress, and context persistence.
    """
    
    def __init__(self):
        self.student_profiles: Dict[str, StudentProfile] = {}
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.session_timeout = timedelta(hours=2)  # 2-hour session timeout
        
    def create_student_profile(self, user_info: UserInfo) -> StudentProfile:
        """Create a new student profile."""
        profile = StudentProfile(
            user_id=user_info.user_id,
            name=user_info.name,
            grade_level=user_info.grade_level,
            learning_style_summary=user_info.learning_style_summary,
            emotional_state_summary=user_info.emotional_state_summary,
            mastery_level_summary=user_info.mastery_level_summary
        )
        
        # Infer additional attributes
        profile.teaching_style = self._infer_teaching_style(user_info)
        profile.emotional_state = self._infer_emotional_state(user_info)
        profile.mastery_level = self._infer_mastery_level(user_info)
        
        self.student_profiles[user_info.user_id] = profile
        
        logger.info(f"Created student profile for {user_info.user_id}")
        return profile
    
    def get_student_profile(self, user_id: str) -> Optional[StudentProfile]:
        """Get student profile by user ID."""
        return self.student_profiles.get(user_id)
    
    def update_student_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update student profile with new information."""
        profile = self.student_profiles.get(user_id)
        if not profile:
            return False
        
        # Update profile fields
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.now()
        
        logger.info(f"Updated student profile for {user_id}")
        return True
    
    def create_session(self, user_id: str, session_id: str) -> ConversationSession:
        """Create a new conversation session."""
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            chat_history=[]
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get conversation session by session ID."""
        session = self.active_sessions.get(session_id)
        
        # Check if session has expired
        if session and datetime.now() - session.last_activity > self.session_timeout:
            logger.info(f"Session {session_id} expired, removing")
            del self.active_sessions[session_id]
            return None
        
        return session
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session with new information."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        # Update session fields
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.last_activity = datetime.now()
        
        logger.info(f"Updated session {session_id}")
        return True
    
    def add_message_to_session(self, session_id: str, message: ChatMessage) -> bool:
        """Add a message to the session's chat history."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        session.chat_history.append(message)
        session.last_activity = datetime.now()
        
        # Limit chat history size
        if len(session.chat_history) > 50:
            session.chat_history = session.chat_history[-50:]
        
        logger.info(f"Added message to session {session_id}")
        return True
    
    def add_tool_interaction(self, session_id: str, tool_name: str, 
                           request: Dict[str, Any], response: Dict[str, Any]) -> bool:
        """Record a tool interaction in the session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "request": request,
            "response": response
        }
        
        session.tool_interactions.append(interaction)
        session.last_activity = datetime.now()
        
        logger.info(f"Recorded tool interaction for session {session_id}")
        return True
    
    def get_conversation_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get current conversation context for a session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        profile = self.student_profiles.get(session.user_id)
        if not profile:
            return None
        
        # Create conversation context
        context = ConversationContext(
            user_info=UserInfo(
                user_id=profile.user_id,
                name=profile.name,
                grade_level=profile.grade_level,
                learning_style_summary=profile.learning_style_summary,
                emotional_state_summary=profile.emotional_state_summary,
                mastery_level_summary=profile.mastery_level_summary
            ),
            chat_history=session.chat_history,
            current_message="",  # Will be set when processing
            teaching_style=profile.teaching_style,
            emotional_state=profile.emotional_state,
            mastery_level=profile.mastery_level
        )
        
        return context
    
    def update_learning_progress(self, user_id: str, topic: str, 
                               progress_data: Dict[str, Any]) -> bool:
        """Update learning progress for a student."""
        profile = self.student_profiles.get(user_id)
        if not profile:
            return False
        
        # Add to learning history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "progress_data": progress_data
        }
        
        profile.learning_history.append(history_entry)
        
        # Update mastery level if significant progress
        if progress_data.get("mastery_increase", 0) > 0:
            current_level = profile.mastery_level or 1
            new_level = min(current_level + progress_data["mastery_increase"], 10)
            profile.mastery_level = new_level
            profile.mastery_level_summary = f"Level {new_level} - {'Foundation' if new_level <= 3 else 'Developing' if new_level <= 6 else 'Advanced' if new_level <= 9 else 'Master'}"
        
        profile.updated_at = datetime.now()
        
        logger.info(f"Updated learning progress for {user_id} on {topic}")
        return True
    
    def get_learning_recommendations(self, user_id: str) -> List[str]:
        """Get personalized learning recommendations based on history."""
        profile = self.student_profiles.get(user_id)
        if not profile:
            return []
        
        recommendations = []
        
        # Analyze learning history
        recent_topics = [entry["topic"] for entry in profile.learning_history[-10:]]
        
        # Recommend based on mastery level
        if profile.mastery_level and profile.mastery_level <= 3:
            recommendations.extend([
                "Focus on foundational concepts",
                "Practice with basic examples",
                "Build confidence with simple exercises"
            ])
        elif profile.mastery_level and profile.mastery_level <= 6:
            recommendations.extend([
                "Practice intermediate applications",
                "Connect concepts to real-world examples",
                "Try more challenging problems"
            ])
        else:
            recommendations.extend([
                "Explore advanced concepts",
                "Engage with complex problems",
                "Consider teaching others"
            ])
        
        # Recommend based on emotional state
        if profile.emotional_state == EmotionalState.CONFUSED:
            recommendations.append("Take breaks and review basic concepts")
        elif profile.emotional_state == EmotionalState.ANXIOUS:
            recommendations.append("Practice with supportive, low-pressure exercises")
        elif profile.emotional_state == EmotionalState.FOCUSED:
            recommendations.append("Challenge yourself with advanced topics")
        
        return recommendations
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
    
    def _infer_teaching_style(self, user_info: UserInfo) -> TeachingStyle:
        """Infer teaching style from user info."""
        learning_style = user_info.learning_style_summary.lower()
        
        if "visual" in learning_style or "image" in learning_style:
            return TeachingStyle.VISUAL
        elif "question" in learning_style or "discussion" in learning_style:
            return TeachingStyle.SOCRATIC
        elif "application" in learning_style or "practice" in learning_style:
            return TeachingStyle.FLIPPED_CLASSROOM
        else:
            return TeachingStyle.DIRECT
    
    def _infer_emotional_state(self, user_info: UserInfo) -> EmotionalState:
        """Infer emotional state from user info."""
        emotional_summary = user_info.emotional_state_summary.lower()
        
        if "focused" in emotional_summary or "motivated" in emotional_summary:
            return EmotionalState.FOCUSED
        elif "anxious" in emotional_summary or "worried" in emotional_summary:
            return EmotionalState.ANXIOUS
        elif "confused" in emotional_summary or "lost" in emotional_summary:
            return EmotionalState.CONFUSED
        elif "tired" in emotional_summary or "exhausted" in emotional_summary:
            return EmotionalState.TIRED
        else:
            return EmotionalState.FOCUSED  # Default
    
    def _infer_mastery_level(self, user_info: UserInfo) -> int:
        """Infer mastery level from user info."""
        mastery_summary = user_info.mastery_level_summary.lower()
        
        if "level 1" in mastery_summary or "foundation" in mastery_summary:
            return 1
        elif "level 2" in mastery_summary:
            return 2
        elif "level 3" in mastery_summary:
            return 3
        elif "level 4" in mastery_summary or "building" in mastery_summary:
            return 4
        elif "level 5" in mastery_summary:
            return 5
        elif "level 6" in mastery_summary or "good" in mastery_summary:
            return 6
        elif "level 7" in mastery_summary or "proficient" in mastery_summary:
            return 7
        elif "level 8" in mastery_summary:
            return 8
        elif "level 9" in mastery_summary or "advanced" in mastery_summary:
            return 9
        elif "level 10" in mastery_summary or "master" in mastery_summary:
            return 10
        else:
            return 5  # Default intermediate level
    
    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for analysis or backup."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        profile = self.student_profiles.get(session.user_id)
        
        return {
            "session": asdict(session),
            "profile": asdict(profile) if profile else None,
            "export_timestamp": datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "total_students": len(self.student_profiles),
            "active_sessions": len(self.active_sessions),
            "total_interactions": sum(
                len(session.tool_interactions) 
                for session in self.active_sessions.values()
            ),
            "average_session_duration": self._calculate_average_session_duration(),
            "most_active_students": self._get_most_active_students()
        }
    
    def _calculate_average_session_duration(self) -> float:
        """Calculate average session duration in minutes."""
        if not self.active_sessions:
            return 0.0
        
        total_duration = sum(
            (datetime.now() - session.session_start).total_seconds() / 60
            for session in self.active_sessions.values()
        )
        
        return total_duration / len(self.active_sessions)
    
    def _get_most_active_students(self) -> List[Dict[str, Any]]:
        """Get list of most active students."""
        student_activity = {}
        
        for session in self.active_sessions.values():
            user_id = session.user_id
            if user_id not in student_activity:
                student_activity[user_id] = {
                    "user_id": user_id,
                    "session_count": 0,
                    "interaction_count": 0
                }
            
            student_activity[user_id]["session_count"] += 1
            student_activity[user_id]["interaction_count"] += len(session.tool_interactions)
        
        # Sort by interaction count and return top 5
        sorted_students = sorted(
            student_activity.values(),
            key=lambda x: x["interaction_count"],
            reverse=True
        )
        
        return sorted_students[:5]
