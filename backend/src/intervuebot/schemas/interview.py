"""
Interview-related Pydantic schemas for adaptive interview system.

This module contains all Pydantic models for the new adaptive interview
flow with resume analysis and dynamic question generation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class ExperienceLevel(str, Enum):
    """Experience level enumeration."""
    JUNIOR = "junior"  # 0-2 years
    MID_LEVEL = "mid-level"  # 2-5 years
    SENIOR = "senior"  # 5+ years
    LEAD = "lead"  # 7+ years with leadership


class InterviewType(str, Enum):
    """Interview type enumeration."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    MIXED = "mixed"
    LEADERSHIP = "leadership"


class DifficultyLevel(str, Enum):
    """Difficulty level enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ResumeFile(BaseModel):
    """Resume file information."""
    filename: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="Uploaded file URL")
    file_type: str = Field(..., description="File type (resume, cv, cover_letter)")


class ResumeAnalysis(BaseModel):
    """Resume analysis results."""
    extracted_skills: List[str] = Field(default_factory=list, description="Skills extracted from resume")
    experience_years: float = Field(..., description="Years of experience extracted")
    education: Optional[str] = Field(None, description="Educational background")
    current_company: Optional[str] = Field(None, description="Current company")
    previous_companies: List[str] = Field(default_factory=list, description="Previous companies")
    projects: List[Dict[str, Any]] = Field(default_factory=list, description="Projects mentioned")
    certifications: List[str] = Field(default_factory=list, description="Certifications")
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    technologies: List[str] = Field(default_factory=list, description="Technologies and tools")
    confidence_score: float = Field(..., ge=0, le=1, description="Analysis confidence score")


class CandidateProfile(BaseModel):
    """Simplified candidate profile with only essential information."""
    
    # Basic information
    name: str = Field(..., description="Candidate's full name")
    email: str = Field(..., description="Candidate's email address")
    
    # Position and experience
    position: str = Field(..., description="Position being interviewed for")
    experience_level: ExperienceLevel = Field(..., description="Experience level")
    interview_type: InterviewType = Field(..., description="Type of interview")
    
    # Resume files
    files: List[ResumeFile] = Field(..., description="Uploaded files (resume, CV, cover letter)")
    
    # Resume analysis (populated by AI)
    resume_analysis: Optional[ResumeAnalysis] = Field(None, description="Resume analysis results")


class InterviewCreate(BaseModel):
    """Request model for creating a new adaptive interview."""
    
    candidate: CandidateProfile = Field(..., description="Candidate information with files")
    duration_minutes: int = Field(default=60, ge=30, le=120, description="Interview duration in minutes")


class Question(BaseModel):
    """Enhanced interview question model."""
    
    id: str = Field(..., description="Unique question identifier")
    text: str = Field(..., description="Question text")
    category: str = Field(..., description="Question category (technical, behavioral, etc.)")
    difficulty: DifficultyLevel = Field(..., description="Question difficulty level")
    expected_duration: int = Field(..., ge=30, le=600, description="Expected answer duration in seconds")
    context: Optional[Dict[str, Any]] = Field(None, description="Question context and metadata")
    follow_up_hints: List[str] = Field(default_factory=list, description="Suggested follow-up questions")


class Response(BaseModel):
    """Enhanced candidate response model."""
    
    question_id: str = Field(..., description="ID of the question being answered")
    answer: str = Field(..., description="Candidate's answer")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    time_taken: int = Field(..., ge=0, description="Time taken to answer in seconds")
    evaluation_score: Optional[float] = Field(None, ge=0, le=10, description="Response evaluation score")
    evaluation_details: Optional[Dict[str, Any]] = Field(None, description="Detailed evaluation breakdown")


class ResponseSubmit(BaseModel):
    """Request model for submitting a response."""
    
    question_id: str = Field(..., description="ID of the question being answered")
    answer: str = Field(..., description="Candidate's answer")
    time_taken: int = Field(..., ge=0, description="Time taken to answer in seconds")


class InterviewSession(BaseModel):
    """Enhanced interview session model."""
    
    session_id: str = Field(..., description="Unique session identifier")
    candidate: CandidateProfile = Field(..., description="Candidate information")
    position: str = Field(..., description="Position being interviewed for")
    interview_type: InterviewType = Field(..., description="Type of interview")
    
    # Session state
    current_phase: str = Field(default="introduction", description="Current interview phase")
    current_difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="Current difficulty level")
    current_question_index: int = Field(default=0, description="Current question index")
    
    # Progress tracking
    total_questions_asked: int = Field(default=0, description="Total questions asked")
    total_responses_received: int = Field(default=0, description="Total responses received")
    average_score: float = Field(default=0.0, ge=0, le=10, description="Average response score")
    
    # Session data
    questions: List[Question] = Field(default_factory=list, description="All questions asked")
    responses: List[Response] = Field(default_factory=list, description="All responses received")
    evaluations: List[Dict[str, Any]] = Field(default_factory=list, description="Response evaluations")
    
    # Session metadata
    status: str = Field(default="in_progress", description="Interview status")
    started_at: datetime = Field(..., description="Interview start time")
    ended_at: Optional[datetime] = Field(None, description="Interview end time")
    duration_minutes: int = Field(..., description="Interview duration in minutes")


class InterviewResponse(BaseModel):
    """Response model for interview session."""
    
    session_id: str = Field(..., description="Unique session identifier")
    candidate: CandidateProfile = Field(..., description="Candidate information")
    position: str = Field(..., description="Position being interviewed for")
    status: str = Field(..., description="Interview status")
    started_at: datetime = Field(..., description="Interview start time")
    current_question_index: int = Field(default=0, description="Current question index")
    total_questions_asked: int = Field(default=0, description="Total questions asked")
    average_score: float = Field(default=0.0, description="Average response score")


class QuestionResponse(BaseModel):
    """Response model for interview questions."""
    
    question: Question = Field(..., description="Question details")
    session_id: str = Field(..., description="Interview session ID")
    question_number: int = Field(..., description="Question number in sequence")
    time_limit: int = Field(..., description="Time limit for answering in seconds")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the question")


class ResponseEvaluation(BaseModel):
    """Detailed response evaluation."""
    
    question_id: str = Field(..., description="Question ID")
    response_text: str = Field(..., description="Original response text")
    
    # Scoring breakdown
    technical_accuracy: float = Field(..., ge=0, le=10, description="Technical accuracy score")
    communication_clarity: float = Field(..., ge=0, le=10, description="Communication clarity score")
    problem_solving_approach: float = Field(..., ge=0, le=10, description="Problem-solving approach score")
    experience_relevance: float = Field(..., ge=0, le=10, description="Experience relevance score")
    overall_score: float = Field(..., ge=0, le=10, description="Overall response score")
    
    # Detailed feedback
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas for improvement")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for better answers")
    
    # Adaptive recommendations
    suggested_difficulty: DifficultyLevel = Field(..., description="Suggested next difficulty level")
    follow_up_questions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    skill_gaps: List[str] = Field(default_factory=list, description="Identified skill gaps")


class InterviewReport(BaseModel):
    """Comprehensive interview evaluation report."""
    
    session_id: str = Field(..., description="Interview session ID")
    candidate: CandidateProfile = Field(..., description="Candidate information")
    position: str = Field(..., description="Position being interviewed for")
    
    # Overall assessment
    overall_score: float = Field(..., ge=0, le=10, description="Overall interview score")
    technical_score: Optional[float] = Field(None, ge=0, le=10, description="Technical skills score")
    behavioral_score: Optional[float] = Field(None, ge=0, le=10, description="Behavioral assessment score")
    communication_score: Optional[float] = Field(None, ge=0, le=10, description="Communication skills score")
    problem_solving_score: Optional[float] = Field(None, ge=0, le=10, description="Problem-solving skills score")
    cultural_fit_score: Optional[float] = Field(None, ge=0, le=10, description="Cultural fit assessment score")
    
    # Detailed analysis
    strengths: List[str] = Field(default_factory=list, description="Candidate strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas for improvement")
    skill_gaps: List[str] = Field(default_factory=list, description="Identified skill gaps")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    
    # Interview statistics
    total_questions: int = Field(..., description="Total questions asked")
    total_responses: int = Field(..., description="Total responses received")
    average_response_time: float = Field(..., description="Average response time in seconds")
    difficulty_progression: List[Dict[str, Any]] = Field(default_factory=list, description="Difficulty progression")
    
    # Final assessment
    hiring_recommendation: str = Field(..., description="Hiring recommendation (hire, consider, reject)")
    confidence_level: float = Field(..., ge=0, le=1, description="Assessment confidence level")
    detailed_feedback: str = Field(..., description="Detailed feedback and assessment")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation time")
    interview_duration: float = Field(..., description="Total interview duration in minutes") 