"""
Adaptive Interview endpoints.

This module provides endpoints for managing adaptive interview sessions
with resume analysis and dynamic question generation.
"""

import uuid
import logging
from typing import Dict, List, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException

from intervuebot.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    QuestionResponse,
    ResponseSubmit,
    CandidateProfile,
    CandidateProfileWithAnalysis,
    InterviewSession,
    Response,
    InterviewReport,
    DifficultyLevel
)
from intervuebot.agents.adaptive_interview_agent import adaptive_interview_agent
from intervuebot.services.resume_analyzer import resume_analyzer
from intervuebot.services.file_processor import file_processor
from intervuebot.core.redis import store_interview_session, get_interview_session, delete_interview_session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start", 
    response_model=InterviewResponse,
    summary="Start Adaptive Interview Session",
    description="""
    Start a new adaptive interview session with comprehensive file processing and AI analysis.
    
    ## Workflow:
    1. **File Processing**: Download and extract text from uploaded files (resume, CV, cover letter)
    2. **AI Analysis**: Analyze extracted content to identify skills, experience, and background
    3. **Session Creation**: Create interview session with AI-enhanced candidate profile
    4. **Context Preparation**: Prepare adaptive interview context based on analysis results
    
    ## Required Information:
    - **Name**: Candidate's full name
    - **Email**: Contact email address
    - **Position**: Job position being applied for
    - **Experience Level**: junior/mid-level/senior/lead
    - **Interview Type**: technical/behavioral/mixed/leadership
    - **Files**: Uploaded resume, CV, and/or cover letter files
    
    ## File Processing:
    - Supports PDF, DOC, DOCX, TXT, RTF formats
    - Extracts text content from all uploaded files
    - Combines content for comprehensive analysis
    - Handles multiple file types in single upload
    """,
    response_description="Created interview session with AI-analyzed resume and session ID",
    tags=["Interviews"],
    responses={
        200: {
            "description": "Interview session created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "550e8400-e29b-41d4-a716-446655440000",
                        "candidate": {
                            "name": "John Doe",
                            "email": "john.doe@example.com",
                            "position": "Software Engineer",
                            "experience_level": "mid-level",
                            "interview_type": "technical",
                            "files": [
                                {
                                    "filename": "john_doe_resume.pdf",
                                    "file_url": "https://example.com/uploads/john_doe_resume.pdf",
                                    "file_type": "resume"
                                }
                            ],
                            "resume_analysis": {
                                "extracted_skills": ["Python", "JavaScript", "React", "Node.js"],
                                "experience_years": 3.5,
                                "education": "BS Computer Science",
                                "current_company": "Tech Corp",
                                "confidence_score": 0.85
                            }
                        },
                        "position": "Software Engineer",
                        "status": "in_progress",
                        "started_at": "2024-01-15T10:30:00Z",
                        "current_question_index": 0,
                        "total_questions_asked": 0,
                        "average_score": 0.0
                    }
                }
            }
        },
        400: {
            "description": "Invalid request data or file processing error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Validation error: files field is required"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error during file processing or analysis",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to start interview: File processing failed"
                    }
                }
            }
        }
    })
async def start_interview(interview_data: InterviewCreate) -> InterviewResponse:
    """
    Start a new adaptive interview session with comprehensive file processing.
    
    This endpoint implements a complete workflow:
    1. **File Processing**: Downloads and extracts text from uploaded files
    2. **AI Analysis**: Analyzes extracted content using AI
    3. **Session Creation**: Creates interview session with enhanced profile
    4. **Context Setup**: Prepares adaptive interview parameters
    
    Args:
        interview_data: Interview creation data including candidate profile and files
        
    Returns:
        InterviewResponse: Created interview session with AI analysis results
        
    Raises:
        HTTPException: If file processing or interview creation fails
        
    Example Request:
        {
            "candidate": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "position": "Software Engineer",
                "experience_level": "mid-level",
                "interview_type": "technical",
                "files": [
                    {
                        "filename": "resume.pdf",
                        "file_url": "https://example.com/resume.pdf",
                        "file_type": "resume"
                    }
                ]
            },
            "duration_minutes": 60
        }
    """
    try:
        # Step 1: Validate and process uploaded files
        logger.info(f"Starting interview session for {interview_data.candidate.name}")
        
        if not interview_data.candidate.files:
            raise HTTPException(
                status_code=400, 
                detail="At least one file (resume, CV, or cover letter) is required"
            )
        
        # Step 2: Process uploaded files
        file_metadata = file_processor.get_file_metadata(interview_data.candidate.files)
        logger.info(f"Processing {file_metadata['total_files']} files: {file_metadata['file_types']}")
        
        # Step 3: Analyze resume content using AI
        resume_analysis = await resume_analyzer.analyze_resume(
            resume_files=interview_data.candidate.files,
            position=interview_data.candidate.position
        )
        
        # Step 4: Create candidate profile with AI analysis
        candidate_profile_with_analysis = CandidateProfileWithAnalysis(
            name=interview_data.candidate.name,
            email=interview_data.candidate.email,
            position=interview_data.candidate.position,
            experience_level=interview_data.candidate.experience_level,
            interview_type=interview_data.candidate.interview_type,
            files=interview_data.candidate.files,
            resume_analysis=resume_analysis
        )
        
        # Step 5: Create interview session
        session_id = str(uuid.uuid4())
        now_iso = datetime.utcnow().isoformat() + "Z"
        
        session_data = {
            "session_id": session_id,
            "candidate": candidate_profile_with_analysis.dict(),
            "position": interview_data.candidate.position,
            "interview_type": interview_data.candidate.interview_type.value,
            "current_phase": "introduction",
            "current_difficulty": DifficultyLevel.MEDIUM.value,
            "current_question_index": 0,
            "total_questions_asked": 0,
            "total_responses_received": 0,
            "average_score": 0.0,
            "questions": [],
            "responses": [],
            "evaluations": [],
            "status": "in_progress",
            "started_at": now_iso,
            "duration_minutes": interview_data.duration_minutes,
            "file_metadata": file_metadata
        }
        
        # Step 6: Store session in Redis
        await store_interview_session(session_id, session_data)
        
        logger.info(f"Interview session {session_id} created successfully for {candidate_profile_with_analysis.name}")
        
        return InterviewResponse(
            session_id=session_id,
            candidate=candidate_profile_with_analysis,
            position=interview_data.candidate.position,
            status="in_progress",
            started_at=now_iso,
            current_question_index=0,
            total_questions_asked=0,
            average_score=0.0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start interview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")


@router.get("/{session_id}/next-question", 
    response_model=QuestionResponse,
    summary="Get Next Adaptive Question",
    description="""
    Get the next adaptive question based on previous responses and AI-analyzed resume content.
    
    This endpoint generates context-aware questions using:
    - Previous responses and their quality assessment
    - AI-analyzed resume content and extracted skills
    - Current interview progress and difficulty adjustment
    - Position requirements and identified skill gaps
    
    ## Question Generation Logic:
    1. **Context Analysis**: Analyzes previous responses and AI-extracted resume content
    2. **Difficulty Adjustment**: Adjusts based on performance (easy/medium/hard)
    3. **Skill Focus**: Targets skills identified in resume analysis
    4. **Follow-up Logic**: Builds on previous responses for deeper exploration
    5. **Progress Tracking**: Ensures appropriate question progression
    
    ## Question Types:
    - **Technical**: Programming, system design, problem-solving
    - **Behavioral**: Past experiences, teamwork, challenges
    - **Situational**: Hypothetical scenarios and decision-making
    - **Leadership**: Management, team building, strategic thinking
    """,
    response_description="Next question with context and time limits",
    tags=["Interviews"],
    responses={
        200: {
            "description": "Next question generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "question": {
                            "id": "q_1",
                            "text": "Can you tell me about your experience with Python and how you would approach optimizing a slow database query?",
                            "category": "technical",
                            "difficulty": "medium",
                            "expected_duration": 300,
                            "context": {
                                "focus_area": "Database optimization",
                                "reasoning": "Based on resume showing Python experience"
                            },
                            "follow_up_hints": [
                                "What specific techniques would you use?",
                                "How would you measure the improvement?"
                            ]
                        },
                        "session_id": "550e8400-e29b-41d4-a716-446655440000",
                        "question_number": 1,
                        "time_limit": 300,
                        "context": {
                            "difficulty": "medium",
                            "category": "technical",
                            "interview_progress": 0.1,
                            "follow_up_hints": [
                                "What specific techniques would you use?",
                                "How would you measure the improvement?"
                            ]
                        }
                    }
                }
            }
        },
        404: {
            "description": "Interview session not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview session not found"
                    }
                }
            }
        },
        400: {
            "description": "Interview session is not in progress",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview session is not in progress"
                    }
                }
            }
        }
    })
async def get_next_question(session_id: str) -> QuestionResponse:
    """
    Get the next adaptive question for an interview session.
    
    This endpoint generates context-aware questions using AI-analyzed resume content
    and previous response quality to create intelligent, adaptive questions.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        QuestionResponse: Next question with context
        
    Raises:
        HTTPException: If session not found or interview completed
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        if session_data["status"] != "in_progress":
            raise HTTPException(status_code=400, detail="Interview session is not in progress")
        
        # Convert session data to objects
        candidate_profile = CandidateProfileWithAnalysis(**session_data["candidate"])
        previous_responses = [Response(**r) for r in session_data["responses"]]
        resume_analysis = candidate_profile.resume_analysis
        
        # Calculate interview progress
        total_questions = session_data["total_questions_asked"]
        interview_progress = min(total_questions / 10.0, 1.0)  # Assume 10 questions max
        
        # Generate next question using adaptive agent
        next_question = await adaptive_interview_agent.generate_next_question(
            candidate_profile=candidate_profile,
            previous_responses=previous_responses,
            resume_analysis=resume_analysis,
            position=session_data["position"],
            current_difficulty=DifficultyLevel(session_data["current_difficulty"]),
            interview_progress=interview_progress,
            question_count=total_questions
        )
        
        # Add question to session
        session_data["questions"].append(next_question.dict())
        session_data["total_questions_asked"] += 1
        
        # Update session in Redis
        await store_interview_session(session_id, session_data)
        
        return QuestionResponse(
            question=next_question,
            session_id=session_id,
            question_number=total_questions + 1,
            time_limit=next_question.expected_duration * 60,  # Convert to seconds
            context={
                "difficulty": next_question.difficulty.value,
                "category": next_question.category,
                "interview_progress": interview_progress,
                "follow_up_hints": next_question.follow_up_hints
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get next question: {str(e)}")


@router.post("/{session_id}/respond",
    summary="Submit Response",
    description="""
    Submit a response to the current question and get comprehensive AI evaluation.
    
    This endpoint evaluates the candidate's response using AI and updates the interview
    session with detailed evaluation results. The evaluation includes multiple
    dimensions and provides adaptive recommendations for the next question.
    
    ## Evaluation Dimensions:
    1. **Technical Accuracy**: How well the technical content is addressed
    2. **Communication Clarity**: How clearly the response is communicated
    3. **Problem-Solving Approach**: Quality of analytical thinking
    4. **Experience Relevance**: How well the response relates to experience
    5. **Overall Score**: Combined evaluation score (1-10 scale)
    
    ## Adaptive Features:
    - **Difficulty Adjustment**: Suggests next question difficulty based on performance
    - **Follow-up Questions**: Provides specific follow-up questions for deeper exploration
    - **Skill Gap Identification**: Identifies areas where candidate may need improvement
    - **Strengths Recognition**: Highlights candidate's strong points
    """,
    response_description="Response evaluation and next steps",
    tags=["Interviews"],
    responses={
        200: {
            "description": "Response submitted and evaluated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Response submitted and evaluated successfully",
                        "evaluation": {
                            "overall_score": 8.5,
                            "technical_accuracy": 9.0,
                            "communication_clarity": 8.0,
                            "problem_solving_approach": 8.5,
                            "experience_relevance": 8.5,
                            "strengths": [
                                "Good understanding of profiling tools",
                                "Comprehensive approach to optimization"
                            ],
                            "areas_for_improvement": [
                                "Could provide more specific examples"
                            ],
                            "suggestions": [
                                "Consider mentioning specific database systems",
                                "Add metrics for measuring success"
                            ],
                            "suggested_difficulty": "hard",
                            "follow_up_questions": [
                                "How would you handle a distributed system optimization?",
                                "What monitoring tools would you use?"
                            ],
                            "skill_gaps": []
                        },
                        "next_steps": "Continue with next question or finalize interview"
                    }
                }
            }
        },
        404: {
            "description": "Interview session not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview session not found"
                    }
                }
            }
        },
        400: {
            "description": "No active question to respond to",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No active question to respond to"
                    }
                }
            }
        }
    })
async def submit_response(session_id: str, response: ResponseSubmit) -> Dict[str, Any]:
    """
    Submit a response to the current question.
    
    This endpoint evaluates the candidate's response using AI and updates
    the interview session with the evaluation results.
    
    Args:
        session_id: Interview session ID
        response: Candidate response data
        
    Returns:
        Dict[str, Any]: Response evaluation and next steps
        
    Raises:
        HTTPException: If session not found or no active question
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        if session_data["status"] != "in_progress":
            raise HTTPException(status_code=400, detail="Interview session is not in progress")
        
        # Get current question
        current_question_index = session_data["current_question_index"]
        if current_question_index >= len(session_data["questions"]):
            raise HTTPException(status_code=400, detail="No active question to respond to")
        
        current_question_data = session_data["questions"][current_question_index]
        from intervuebot.schemas.interview import Question
        current_question = Question(**current_question_data)
        
        # Convert session data to objects for evaluation
        candidate_profile = CandidateProfileWithAnalysis(**session_data["candidate"])
        resume_analysis = candidate_profile.resume_analysis
        
        # Evaluate response using adaptive agent
        evaluation = await adaptive_interview_agent.evaluate_response(
            question=current_question,
            response=response.answer,
            candidate_profile=candidate_profile,
            resume_analysis=resume_analysis,
            position=session_data["position"]
        )
        
        # Create response object
        response_obj = Response(
            question_id=response.question_id,
            answer=response.answer,
            time_taken=response.time_taken,
            evaluation_score=evaluation.overall_score,
            evaluation_details=evaluation.dict()
        )
        
        # Update session data
        session_data["responses"].append(response_obj.dict())
        session_data["evaluations"].append(evaluation.dict())
        session_data["current_question_index"] += 1
        session_data["total_responses_received"] += 1
        
        # Update average score
        scores = [r.get("evaluation_score", 0) for r in session_data["responses"] if r.get("evaluation_score")]
        if scores:
            session_data["average_score"] = sum(scores) / len(scores)
        
        # Update difficulty based on evaluation
        session_data["current_difficulty"] = evaluation.suggested_difficulty.value
        
        # Update session in Redis
        await store_interview_session(session_id, session_data)
        
        return {
            "status": "success",
            "message": "Response submitted and evaluated successfully",
            "evaluation": {
                "overall_score": evaluation.overall_score,
                "technical_accuracy": evaluation.technical_accuracy,
                "communication_clarity": evaluation.communication_clarity,
                "problem_solving_approach": evaluation.problem_solving_approach,
                "experience_relevance": evaluation.experience_relevance,
                "strengths": evaluation.strengths,
                "areas_for_improvement": evaluation.areas_for_improvement,
                "suggestions": evaluation.suggestions,
                "suggested_difficulty": evaluation.suggested_difficulty.value,
                "follow_up_questions": evaluation.follow_up_questions,
                "skill_gaps": evaluation.skill_gaps
            },
            "next_steps": "Continue with next question or finalize interview"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit response: {str(e)}")


@router.post("/{session_id}/finalize",
    summary="Finalize Interview",
    description="""
    End the interview and generate comprehensive AI evaluation report.
    
    This endpoint completes the interview session and generates a comprehensive
    evaluation report based on all responses and AI-analyzed resume content.
    The report includes detailed scoring, hiring recommendations, and actionable feedback.
    
    ## Report Contents:
    1. **Overall Assessment**: Comprehensive evaluation across all dimensions
    2. **Detailed Scoring**: Breakdown by technical, behavioral, communication skills
    3. **Hiring Recommendation**: Hire/Consider/Reject with confidence level
    4. **Strengths & Areas for Improvement**: Specific feedback for candidate
    5. **Skill Gaps**: Identified gaps between requirements and candidate skills
    6. **Interview Statistics**: Questions asked, response times, difficulty progression
    7. **Detailed Feedback**: Comprehensive written assessment
    
    ## Hiring Recommendations:
    - **Hire**: Strong candidate with excellent performance (score 8.0+)
    - **Consider**: Good candidate with potential (score 6.0-7.9)
    - **Reject**: Candidate not suitable for position (score <6.0)
    """,
    response_description="Interview completion and report summary",
    tags=["Interviews"],
    responses={
        200: {
            "description": "Interview completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Interview completed successfully",
                        "session_id": "550e8400-e29b-41d4-a716-446655440000",
                        "report_summary": {
                            "overall_score": 8.2,
                            "hiring_recommendation": "hire",
                            "confidence_level": 0.85,
                            "total_questions": 8,
                            "total_responses": 8,
                            "average_response_time": 145.5
                        }
                    }
                }
            }
        },
        404: {
            "description": "Interview session not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview session not found"
                    }
                }
            }
        },
        400: {
            "description": "Interview session already completed",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview session already completed"
                    }
                }
            }
        }
    })
async def finalize_interview(session_id: str) -> Dict[str, Any]:
    """
    Finalize the interview and generate comprehensive report.
    
    This endpoint ends the interview session and generates a comprehensive
    evaluation report based on all responses and AI analysis.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        Dict[str, Any]: Interview completion and report summary
        
    Raises:
        HTTPException: If session not found or already completed
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        if session_data["status"] == "completed":
            raise HTTPException(status_code=400, detail="Interview session already completed")
        
        now_iso = datetime.utcnow().isoformat() + "Z"
        
        # Update session status
        session_data["status"] = "completed"
        session_data["ended_at"] = now_iso
        
        # Generate comprehensive report
        report = await _generate_comprehensive_report(session_data)
        session_data["final_report"] = report.dict()
        
        # Update session in Redis
        await store_interview_session(session_id, session_data)
        
        return {
            "status": "success",
            "message": "Interview completed successfully",
            "session_id": session_id,
            "report_summary": {
                "overall_score": report.overall_score,
                "hiring_recommendation": report.hiring_recommendation,
                "confidence_level": report.confidence_level,
                "total_questions": report.total_questions,
                "total_responses": report.total_responses,
                "average_response_time": report.average_response_time
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to finalize interview: {str(e)}")


@router.get("/{session_id}/report",
    summary="Get Interview Report",
    description="""
    Get the comprehensive interview evaluation report.
    
    This endpoint returns the complete evaluation report including
    scores, feedback, recommendations, and detailed analysis.
    
    ## Report Sections:
    1. **Candidate Information**: Name, position, experience level
    2. **Overall Assessment**: Comprehensive scoring across all dimensions
    3. **Detailed Analysis**: Breakdown by technical, behavioral, communication skills
    4. **Strengths & Areas for Improvement**: Specific feedback points
    5. **Skill Gaps**: Identified gaps between requirements and candidate skills
    6. **Interview Statistics**: Questions asked, response times, difficulty progression
    7. **Hiring Recommendation**: Final recommendation with confidence level
    8. **Detailed Feedback**: Comprehensive written assessment
    
    ## Scoring Breakdown:
    - **Overall Score**: Combined evaluation (1-10 scale)
    - **Technical Score**: Technical skills and knowledge assessment
    - **Behavioral Score**: Soft skills and experience evaluation
    - **Communication Score**: Clarity and presentation skills
    - **Problem-Solving Score**: Analytical thinking and approach
    - **Cultural Fit Score**: Team fit and company alignment
    """,
    response_description="Complete interview evaluation report",
    tags=["Interviews"],
    responses={
        200: {
            "description": "Interview report retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "550e8400-e29b-41d4-a716-446655440000",
                        "candidate": {
                            "name": "John Doe",
                            "email": "john.doe@example.com",
                            "position": "Software Engineer",
                            "experience_level": "mid-level",
                            "interview_type": "technical"
                        },
                        "position": "Software Engineer",
                        "overall_score": 8.2,
                        "technical_score": 8.5,
                        "behavioral_score": 7.8,
                        "communication_score": 8.0,
                        "problem_solving_score": 8.5,
                        "cultural_fit_score": 8.0,
                        "strengths": [
                            "Strong technical knowledge",
                            "Good problem-solving approach",
                            "Clear communication"
                        ],
                        "areas_for_improvement": [
                            "Could provide more specific examples",
                            "Consider mentioning industry best practices"
                        ],
                        "skill_gaps": [],
                        "recommendations": ["Recommendation: HIRE"],
                        "total_questions": 8,
                        "total_responses": 8,
                        "average_response_time": 145.5,
                        "difficulty_progression": [
                            {"question": 1, "difficulty": "medium", "score": 8.5},
                            {"question": 2, "difficulty": "hard", "score": 8.0}
                        ],
                        "hiring_recommendation": "hire",
                        "confidence_level": 0.85,
                        "detailed_feedback": "Comprehensive Interview Report...",
                        "interview_duration": 45.5
                    }
                }
            }
        },
        404: {
            "description": "Interview session or report not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview report not found"
                    }
                }
            }
        },
        400: {
            "description": "Interview session is not completed",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview session is not completed"
                    }
                }
            }
        }
    })
async def get_interview_report(session_id: str) -> InterviewReport:
    """
    Get the comprehensive interview evaluation report.
    
    This endpoint returns the complete evaluation report including
    scores, feedback, recommendations, and detailed analysis.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        InterviewReport: Comprehensive interview evaluation report
        
    Raises:
        HTTPException: If session not found or not completed
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        if session_data["status"] != "completed":
            raise HTTPException(status_code=400, detail="Interview session is not completed")
        
        # Return the final report
        if "final_report" in session_data:
            return InterviewReport(**session_data["final_report"])
        else:
            raise HTTPException(status_code=404, detail="Interview report not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")


async def _generate_comprehensive_report(session_data: Dict[str, Any]) -> InterviewReport:
    """
    Generate comprehensive interview report.
    
    Args:
        session_data: Session data from Redis
        
    Returns:
        InterviewReport: Comprehensive evaluation report
    """
    # Calculate statistics
    total_questions = session_data["total_questions_asked"]
    total_responses = session_data["total_responses_received"]
    average_score = session_data["average_score"]
    
    # Calculate average response time
    response_times = [r.get("time_taken", 0) for r in session_data["responses"]]
    average_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Calculate interview duration
    started_at = datetime.fromisoformat(session_data["started_at"].replace("Z", "+00:00"))
    ended_at = datetime.fromisoformat(session_data["ended_at"].replace("Z", "+00:00"))
    interview_duration = (ended_at - started_at).total_seconds() / 60
    
    # Determine hiring recommendation based on average score
    if average_score >= 8.0:
        hiring_recommendation = "hire"
    elif average_score >= 6.0:
        hiring_recommendation = "consider"
    else:
        hiring_recommendation = "reject"
    
    # Generate detailed feedback
    detailed_feedback = f"""
    Comprehensive Interview Report
    
    Candidate: {session_data['candidate']['name']}
    Position: {session_data['position']}
    Interview Duration: {interview_duration:.1f} minutes
    
    Performance Summary:
    - Total Questions: {total_questions}
    - Total Responses: {total_responses}
    - Average Score: {average_score:.1f}/10
    - Average Response Time: {average_response_time:.1f} seconds
    
    Overall Assessment:
    The candidate demonstrated {'strong' if average_score >= 8.0 else 'moderate' if average_score >= 6.0 else 'weak'} performance 
    throughout the interview. {'The candidate shows excellent potential for the role.' if average_score >= 8.0 else 
    'The candidate has potential but may need additional training.' if average_score >= 6.0 else 
    'The candidate may not be the best fit for this position.'}
    
    Recommendation: {hiring_recommendation.upper()}
    """
    
    return InterviewReport(
        session_id=session_data["session_id"],
        candidate=CandidateProfileWithAnalysis(**session_data["candidate"]),
        position=session_data["position"],
        overall_score=average_score,
        technical_score=average_score,  # Simplified - in real implementation, calculate from evaluations
        behavioral_score=average_score,
        communication_score=average_score,
        problem_solving_score=average_score,
        cultural_fit_score=average_score,
        strengths=["Good communication", "Technical knowledge"],  # Simplified
        areas_for_improvement=["Could provide more specific examples"],  # Simplified
        skill_gaps=[],  # Simplified
        recommendations=[f"Recommendation: {hiring_recommendation.upper()}"],
        total_questions=total_questions,
        total_responses=total_responses,
        average_response_time=average_response_time,
        difficulty_progression=[],  # Simplified
        hiring_recommendation=hiring_recommendation,
        confidence_level=0.8,  # Simplified
        detailed_feedback=detailed_feedback,
        interview_duration=interview_duration
    ) 