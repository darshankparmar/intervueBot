"""
Interview sequence management.

This module defines the interview sequence, phases, and adaptive
difficulty progression based on candidate experience and position.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

from intervuebot.schemas.interview import InterviewPhase, CandidateProfile


class InterviewPhaseType(Enum):
    """Interview phase types."""
    INTRODUCTION = "introduction"
    WARM_UP = "warm_up"
    TECHNICAL_BASIC = "technical_basic"
    TECHNICAL_ADVANCED = "technical_advanced"
    BEHAVIORAL = "behavioral"
    PROBLEM_SOLVING = "problem_solving"
    SITUATIONAL = "situational"
    CULTURAL_FIT = "cultural_fit"
    CLOSING = "closing"


@dataclass
class PhaseConfig:
    """Configuration for interview phases."""
    name: str
    order: int
    description: str
    duration_minutes: int
    question_count: int
    difficulty: str
    required_for: List[str]  # interview types that require this phase


class InterviewSequenceManager:
    """
    Manages interview sequence and adaptive difficulty progression.
    
    This class defines the interview phases and adapts the sequence
    based on candidate experience, position, and interview type.
    """
    
    def __init__(self):
        """Initialize the interview sequence manager."""
        self.phase_configs = self._initialize_phase_configs()
    
    def _initialize_phase_configs(self) -> Dict[str, PhaseConfig]:
        """Initialize phase configurations."""
        return {
            InterviewPhaseType.INTRODUCTION.value: PhaseConfig(
                name="Introduction & Ice Breaker",
                order=1,
                description="Welcome candidate, explain interview process, and start with easy ice-breaker questions",
                duration_minutes=5,
                question_count=2,
                difficulty="easy",
                required_for=["technical", "behavioral", "mixed"]
            ),
            InterviewPhaseType.WARM_UP.value: PhaseConfig(
                name="Warm-up Questions",
                order=2,
                description="Simple questions to build confidence and assess basic communication",
                duration_minutes=8,
                question_count=3,
                difficulty="easy",
                required_for=["technical", "behavioral", "mixed"]
            ),
            InterviewPhaseType.TECHNICAL_BASIC.value: PhaseConfig(
                name="Basic Technical Assessment",
                order=3,
                description="Fundamental technical questions appropriate for the candidate's level",
                duration_minutes=15,
                question_count=4,
                difficulty="medium",
                required_for=["technical", "mixed"]
            ),
            InterviewPhaseType.TECHNICAL_ADVANCED.value: PhaseConfig(
                name="Advanced Technical Assessment",
                order=4,
                description="Complex technical questions to test deep knowledge and problem-solving",
                duration_minutes=20,
                question_count=3,
                difficulty="hard",
                required_for=["technical", "mixed"]
            ),
            InterviewPhaseType.BEHAVIORAL.value: PhaseConfig(
                name="Behavioral Assessment",
                order=5,
                description="Questions about past experiences, teamwork, and soft skills",
                duration_minutes=15,
                question_count=4,
                difficulty="medium",
                required_for=["behavioral", "mixed"]
            ),
            InterviewPhaseType.PROBLEM_SOLVING.value: PhaseConfig(
                name="Problem-Solving Scenarios",
                order=6,
                description="Real-world scenarios to test analytical thinking and decision-making",
                duration_minutes=12,
                question_count=2,
                difficulty="hard",
                required_for=["technical", "mixed"]
            ),
            InterviewPhaseType.SITUATIONAL.value: PhaseConfig(
                name="Situational Questions",
                order=7,
                description="Hypothetical scenarios to assess judgment and approach",
                duration_minutes=10,
                question_count=2,
                difficulty="medium",
                required_for=["behavioral", "mixed"]
            ),
            InterviewPhaseType.CULTURAL_FIT.value: PhaseConfig(
                name="Cultural Fit Assessment",
                order=8,
                description="Questions about work style, values, and team dynamics",
                duration_minutes=8,
                question_count=2,
                difficulty="medium",
                required_for=["behavioral", "mixed"]
            ),
            InterviewPhaseType.CLOSING.value: PhaseConfig(
                name="Closing & Next Steps",
                order=9,
                description="Wrap up interview, answer candidate questions, and explain next steps",
                duration_minutes=5,
                question_count=1,
                difficulty="easy",
                required_for=["technical", "behavioral", "mixed"]
            )
        }
    
    def generate_interview_sequence(
        self,
        candidate: CandidateProfile,
        position: str,
        interview_type: str,
        total_duration: int = 60
    ) -> List[InterviewPhase]:
        """
        Generate interview sequence based on candidate profile and requirements.
        
        Args:
            candidate: Candidate profile information
            position: Job position
            interview_type: Type of interview (technical, behavioral, mixed)
            total_duration: Total interview duration in minutes
            
        Returns:
            List[InterviewPhase]: Ordered list of interview phases
        """
        # Determine which phases to include based on interview type
        required_phases = []
        for phase_key, config in self.phase_configs.items():
            if interview_type in config.required_for:
                required_phases.append((phase_key, config))
        
        # Sort by order
        required_phases.sort(key=lambda x: x[1].order)
        
        # Adjust difficulty and duration based on experience level
        adjusted_phases = []
        for phase_key, config in required_phases:
            adjusted_config = self._adjust_phase_for_candidate(
                config, candidate, position, interview_type
            )
            adjusted_phases.append(adjusted_config)
        
        # Ensure total duration fits within allocated time
        adjusted_phases = self._adjust_duration(adjusted_phases, total_duration)
        
        return adjusted_phases
    
    def _adjust_phase_for_candidate(
        self,
        config: PhaseConfig,
        candidate: CandidateProfile,
        position: str,
        interview_type: str
    ) -> InterviewPhase:
        """
        Adjust phase configuration based on candidate profile.
        
        Args:
            config: Original phase configuration
            candidate: Candidate profile
            position: Job position
            interview_type: Interview type
            
        Returns:
            InterviewPhase: Adjusted phase configuration
        """
        # Adjust difficulty based on experience
        difficulty = self._determine_difficulty(config.difficulty, candidate.experience_years)
        
        # Adjust question count based on experience and position
        question_count = self._adjust_question_count(
            config.question_count, candidate.experience_years, position
        )
        
        # Adjust duration based on question count and complexity
        duration = self._adjust_duration_for_phase(
            config.duration_minutes, question_count, difficulty
        )
        
        return InterviewPhase(
            phase_name=config.name,
            phase_order=config.order,
            description=config.description,
            estimated_duration=duration,
            question_count=question_count,
            difficulty_level=difficulty
        )
    
    def _determine_difficulty(self, base_difficulty: str, experience_years: int) -> str:
        """Determine adjusted difficulty based on experience."""
        if experience_years <= 1:
            # Junior level - reduce difficulty
            if base_difficulty == "hard":
                return "medium"
            elif base_difficulty == "medium":
                return "easy"
            return "easy"
        elif experience_years >= 5:
            # Senior level - increase difficulty
            if base_difficulty == "easy":
                return "medium"
            elif base_difficulty == "medium":
                return "hard"
            return "hard"
        else:
            # Mid-level - keep base difficulty
            return base_difficulty
    
    def _adjust_question_count(
        self, base_count: int, experience_years: int, position: str
    ) -> int:
        """Adjust question count based on experience and position."""
        # Senior positions get more questions
        if "senior" in position.lower() or "lead" in position.lower():
            base_count = min(base_count + 1, 6)
        
        # Junior positions get fewer questions
        if experience_years <= 1:
            base_count = max(base_count - 1, 1)
        
        return base_count
    
    def _adjust_duration_for_phase(
        self, base_duration: int, question_count: int, difficulty: str
    ) -> int:
        """Adjust duration based on question count and difficulty."""
        # Adjust for question count
        duration = base_duration * (question_count / 3)  # Normalize to 3 questions
        
        # Adjust for difficulty
        if difficulty == "hard":
            duration *= 1.3
        elif difficulty == "easy":
            duration *= 0.8
        
        return max(int(duration), 3)  # Minimum 3 minutes
    
    def _adjust_duration(
        self, phases: List[InterviewPhase], total_duration: int
    ) -> List[InterviewPhase]:
        """Adjust phase durations to fit within total duration."""
        total_estimated = sum(phase.estimated_duration for phase in phases)
        
        if total_estimated <= total_duration:
            return phases
        
        # Reduce duration proportionally
        ratio = total_duration / total_estimated
        adjusted_phases = []
        
        for phase in phases:
            adjusted_duration = max(int(phase.estimated_duration * ratio), 3)
            adjusted_phase = InterviewPhase(
                phase_name=phase.phase_name,
                phase_order=phase.phase_order,
                description=phase.description,
                estimated_duration=adjusted_duration,
                question_count=phase.question_count,
                difficulty_level=phase.difficulty_level
            )
            adjusted_phases.append(adjusted_phase)
        
        return adjusted_phases
    
    def get_next_phase(self, current_phase: str, phases: List[InterviewPhase]) -> Optional[InterviewPhase]:
        """Get the next phase in the sequence."""
        current_order = None
        for phase in phases:
            if phase.phase_name == current_phase:
                current_order = phase.phase_order
                break
        
        if current_order is None:
            return None
        
        for phase in phases:
            if phase.phase_order == current_order + 1:
                return phase
        
        return None
    
    def get_phase_by_name(self, phase_name: str, phases: List[InterviewPhase]) -> Optional[InterviewPhase]:
        """Get phase by name."""
        for phase in phases:
            if phase.phase_name == phase_name:
                return phase
        return None


# Global instance
interview_sequence_manager = InterviewSequenceManager() 