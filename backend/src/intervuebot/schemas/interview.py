"""
Interview-related Pydantic models and schemas.

This module defines all the data structures used for interview management,
including candidate profiles, questions, responses, and evaluation results.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience level enumeration."""
    JUNIOR = "junior"
    MID_LEVEL = "mid-level"
    SENIOR = "senior"
    LEAD = "lead"


class InterviewType(str, Enum):
    """Interview type enumeration."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    MIXED = "mixed"
    LEADERSHIP = "leadership"


class DifficultyLevel(str, Enum):
    """Question difficulty level."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewPhase(str, Enum):
    """Interview phase enumeration."""
    INTRODUCTION = "introduction"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    LEADERSHIP = "leadership"
    CLOSING = "closing"


class ResumeFile(BaseModel):
    """Resume file information."""
    filename: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="File URL for access")
    file_type: str = Field(..., description="Type of file (resume, cv, cover_letter)")


class UploadedFileData(BaseModel):
    """Uploaded file data from frontend."""
    name: str = Field(..., description="Original filename")
    type: str = Field(..., description="Type of file (resume, cv, cover_letter)")
    size: int = Field(..., description="File size in bytes")
    content: str = Field(..., description="File content as base64 string")


class ResumeAnalysis(BaseModel):
    """Resume analysis results."""
    extracted_skills: List[str] = Field(default_factory=list, description="Extracted skills from resume")
    experience_years: float = Field(0.0, description="Years of experience")
    education: Optional[str] = Field(None, description="Education information")
    current_company: Optional[str] = Field(None, description="Current company")
    previous_companies: List[str] = Field(default_factory=list, description="Previous companies")
    projects: List[Dict[str, Any]] = Field(default_factory=list, description="Projects mentioned")
    certifications: List[str] = Field(default_factory=list, description="Certifications")
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    technologies: List[str] = Field(default_factory=list, description="Technologies and tools")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Analysis confidence score")


class CandidateProfile(BaseModel):
    """Candidate profile information."""
    name: str = Field(..., description="Candidate's full name")
    email: EmailStr = Field(..., description="Candidate's email address")
    position: str = Field(..., description="Position being applied for")
    experience_level: ExperienceLevel = Field(..., description="Experience level")
    interview_type: InterviewType = Field(..., description="Type of interview")
    files: List[UploadedFileData] = Field(default_factory=list, description="Uploaded resume files")


class CandidateProfileWithAnalysis(CandidateProfile):
    """Candidate profile with resume analysis."""
    resume_analysis: Optional[ResumeAnalysis] = Field(None, description="Resume analysis results")


class Question(BaseModel):
    """Interview question model."""
    id: str = Field(..., description="Unique question ID")
    text: str = Field(..., description="Question text")
    category: str = Field(..., description="Question category")
    difficulty: DifficultyLevel = Field(..., description="Question difficulty")
    expected_duration: int = Field(..., description="Expected answer duration in seconds")
    context: Optional[Dict[str, Any]] = Field(None, description="Question context")
    follow_up_hints: List[str] = Field(default_factory=list, description="Follow-up hints")


class Response(BaseModel):
    """Candidate response model."""
    question_id: str = Field(..., description="Question ID being answered")
    answer: str = Field(..., description="Candidate's answer")
    time_taken: int = Field(..., description="Time taken to answer in seconds")
    evaluation_score: Optional[float] = Field(None, description="Evaluation score")
    evaluation_details: Optional[Dict[str, Any]] = Field(None, description="Detailed evaluation")


class ResponseEvaluation(BaseModel):
    """Response evaluation results."""
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall response score")
    technical_accuracy: float = Field(..., ge=0.0, le=10.0, description="Technical accuracy score")
    communication_clarity: float = Field(..., ge=0.0, le=10.0, description="Communication clarity score")
    problem_solving_approach: float = Field(..., ge=0.0, le=10.0, description="Problem-solving approach score")
    experience_relevance: float = Field(..., ge=0.0, le=10.0, description="Experience relevance score")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas for improvement")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    suggested_difficulty: DifficultyLevel = Field(..., description="Suggested next question difficulty")
    follow_up_questions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    skill_gaps: List[str] = Field(default_factory=list, description="Identified skill gaps")


class SubmitResponseResult(BaseModel):
    """Response submission result."""
    status: str = Field(..., description="Submission status")
    message: str = Field(..., description="Status message")
    evaluation: ResponseEvaluation = Field(..., description="Response evaluation")
    next_steps: str = Field(..., description="Next steps guidance")


class FinalizeResult(BaseModel):
    """Interview finalization result."""
    status: str = Field(..., description="Finalization status")
    message: str = Field(..., description="Status message")
    session_id: str = Field(..., description="Interview session ID")
    report_summary: Dict[str, Any] = Field(..., description="Report summary")


class InterviewSession(BaseModel):
    """Interview session model."""
    session_id: str = Field(..., description="Unique session ID")
    candidate: CandidateProfileWithAnalysis = Field(..., description="Candidate profile with analysis")
    position: str = Field(..., description="Position being applied for")
    status: str = Field(..., description="Session status")
    started_at: str = Field(..., description="Session start time")
    current_question_index: int = Field(0, description="Current question index")
    total_questions_asked: int = Field(0, description="Total questions asked")
    average_score: float = Field(0.0, description="Average response score")
    responses: List[Response] = Field(default_factory=list, description="Session responses")
    questions: List[Question] = Field(default_factory=list, description="Session questions")


class InterviewCreate(BaseModel):
    """Interview creation request."""
    candidate: CandidateProfile = Field(..., description="Candidate profile")
    duration_minutes: int = Field(..., ge=30, le=120, description="Interview duration in minutes")


class InterviewResponse(BaseModel):
    """Interview response model."""
    session_id: str = Field(..., description="Interview session ID")
    candidate: CandidateProfileWithAnalysis = Field(..., description="Candidate profile with analysis")
    position: str = Field(..., description="Position being applied for")
    status: str = Field(..., description="Interview status")
    started_at: str = Field(..., description="Interview start time")
    current_question_index: int = Field(0, description="Current question index")
    total_questions_asked: int = Field(0, description="Total questions asked")
    average_score: float = Field(0.0, description="Average response score")


class QuestionResponse(BaseModel):
    """Question response model."""
    question: Question = Field(..., description="Question details")
    session_id: str = Field(..., description="Session ID")
    question_number: int = Field(..., description="Question number")
    time_limit: int = Field(..., description="Time limit in seconds")
    context: Optional[Dict[str, Any]] = Field(None, description="Question context")


class ResponseSubmit(BaseModel):
    """Response submission model."""
    question_id: str = Field(..., description="Question ID")
    answer: str = Field(..., description="Candidate's answer")
    time_taken: int = Field(..., description="Time taken in seconds")


class InterviewReport(BaseModel):
    """Interview report model."""
    session_id: str = Field(..., description="Session ID")
    candidate: CandidateProfileWithAnalysis = Field(..., description="Candidate profile")
    position: str = Field(..., description="Position applied for")
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall interview score")
    technical_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Technical skills score")
    behavioral_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Behavioral skills score")
    communication_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Communication score")
    problem_solving_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Problem-solving score")
    cultural_fit_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Cultural fit score")
    strengths: List[str] = Field(default_factory=list, description="Candidate strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas for improvement")
    skill_gaps: List[str] = Field(default_factory=list, description="Identified skill gaps")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    total_questions: int = Field(0, description="Total questions asked")
    total_responses: int = Field(0, description="Total responses received")
    average_response_time: float = Field(0.0, description="Average response time")
    difficulty_progression: List[Dict[str, Any]] = Field(default_factory=list, description="Difficulty progression")
    hiring_recommendation: str = Field(..., description="Hiring recommendation")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence level")
    detailed_feedback: str = Field(..., description="Detailed feedback")
    generated_at: str = Field(..., description="Report generation time")
    interview_duration: float = Field(0.0, description="Interview duration in minutes") 