"""
Interview-related Pydantic schemas.

This module contains all Pydantic models for interview data validation
and serialization.
"""

from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """Candidate profile information."""
    
    name: str = Field(..., description="Candidate's full name")
    email: str = Field(..., description="Candidate's email address")
    phone: Optional[str] = Field(None, description="Candidate's phone number")
    position: str = Field(..., description="Position being interviewed for")
    experience_years: int = Field(..., ge=0, description="Years of experience")
    skills: List[str] = Field(default_factory=list, description="List of technical skills")
    resume_url: Optional[str] = Field(None, description="Link to candidate's resume")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(None, description="Portfolio website URL")
    current_company: Optional[str] = Field(None, description="Current company")
    education: Optional[str] = Field(None, description="Educational background")
    preferred_interview_type: str = Field(default="technical", description="Preferred interview type")
    availability: Optional[str] = Field(None, description="Interview availability")


class Question(BaseModel):
    """Interview question model."""
    
    id: str = Field(..., description="Unique question identifier")
    text: str = Field(..., description="Question text")
    category: str = Field(..., description="Question category (technical, behavioral, etc.)")
    difficulty: str = Field(..., description="Question difficulty level")
    expected_duration: int = Field(..., ge=30, le=600, description="Expected answer duration in seconds")


class Response(BaseModel):
    """Candidate response model."""
    
    question_id: str = Field(..., description="ID of the question being answered")
    answer: str = Field(..., description="Candidate's answer")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    evaluation_score: Optional[float] = Field(None, ge=0, le=10, description="Response evaluation score")


class InterviewCreate(BaseModel):
    """Request model for creating a new interview."""
    
    candidate: CandidateProfile = Field(..., description="Candidate information")
    position: str = Field(..., description="Position being interviewed for")
    interview_type: str = Field(default="technical", description="Type of interview")
    duration_minutes: int = Field(default=30, ge=15, le=120, description="Interview duration in minutes")


class InterviewResponse(BaseModel):
    """Response model for interview session."""
    
    session_id: str = Field(..., description="Unique session identifier")
    candidate: CandidateProfile = Field(..., description="Candidate information")
    position: str = Field(..., description="Position being interviewed for")
    status: str = Field(..., description="Interview status")
    started_at: datetime = Field(..., description="Interview start time")
    ended_at: Optional[datetime] = Field(None, description="Interview end time")
    total_questions: int = Field(default=0, description="Total questions asked")
    completed_questions: int = Field(default=0, description="Completed questions")


class QuestionResponse(BaseModel):
    """Response model for interview questions."""
    
    question: Question = Field(..., description="Question details")
    session_id: str = Field(..., description="Interview session ID")
    question_number: int = Field(..., description="Question number in sequence")
    time_limit: int = Field(..., description="Time limit for answering in seconds")


class ResponseSubmit(BaseModel):
    """Request model for submitting a response."""
    
    question_id: str = Field(..., description="ID of the question being answered")
    answer: str = Field(..., description="Candidate's answer")
    time_taken: int = Field(..., ge=0, description="Time taken to answer in seconds")


class InterviewPhase(BaseModel):
    """Interview phase information."""
    
    phase_name: str = Field(..., description="Name of the interview phase")
    phase_order: int = Field(..., description="Order of the phase in interview sequence")
    description: str = Field(..., description="Description of what this phase covers")
    estimated_duration: int = Field(..., description="Estimated duration in minutes")
    question_count: int = Field(..., description="Number of questions in this phase")
    difficulty_level: str = Field(..., description="Difficulty level for this phase")


class InterviewSession(BaseModel):
    """Enhanced interview session model."""
    
    session_id: str = Field(..., description="Unique session identifier")
    candidate: CandidateProfile = Field(..., description="Candidate information")
    position: str = Field(..., description="Position being interviewed for")
    interview_type: str = Field(..., description="Type of interview")
    current_phase: str = Field(default="introduction", description="Current interview phase")
    phases: List[InterviewPhase] = Field(default_factory=list, description="Interview phases")
    total_duration: int = Field(..., description="Total interview duration in minutes")
    status: str = Field(default="in_progress", description="Interview status")
    started_at: datetime = Field(..., description="Interview start time")
    current_question_index: int = Field(default=0, description="Current question index")
    responses: List[Response] = Field(default_factory=list, description="Candidate responses")
    evaluations: List[Dict] = Field(default_factory=list, description="Response evaluations")


class InterviewReport(BaseModel):
    """Interview evaluation report."""
    
    session_id: str = Field(..., description="Interview session ID")
    candidate: CandidateProfile = Field(..., description="Candidate information")
    overall_score: float = Field(..., ge=0, le=10, description="Overall interview score")
    technical_score: Optional[float] = Field(None, ge=0, le=10, description="Technical skills score")
    behavioral_score: Optional[float] = Field(None, ge=0, le=10, description="Behavioral assessment score")
    communication_score: Optional[float] = Field(None, ge=0, le=10, description="Communication skills score")
    problem_solving_score: Optional[float] = Field(None, ge=0, le=10, description="Problem-solving skills score")
    cultural_fit_score: Optional[float] = Field(None, ge=0, le=10, description="Cultural fit assessment score")
    strengths: List[str] = Field(default_factory=list, description="Candidate strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas for improvement")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    phase_scores: Dict[str, float] = Field(default_factory=dict, description="Scores by interview phase")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation time") 