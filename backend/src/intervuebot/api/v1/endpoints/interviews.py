"""
Interview endpoints for IntervueBot API.

This module handles interview-related endpoints including starting interviews,
getting questions, submitting responses, and generating reports.
"""

import uuid
from typing import Dict, List, Any
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from intervuebot.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    QuestionResponse,
    ResponseSubmit,
    SubmitResponseResult,
    FinalizeResult,
    InterviewReport,
    CandidateProfile,
    ResumeFile,
    UploadedFileData,
    CandidateProfileWithAnalysis,
    Question,
    FileReference,
)
from ....services.file_upload_service import file_upload_service
from ....services.resume_analyzer import resume_analyzer
from ....agents.adaptive_interview_agent import adaptive_interview_agent
from ....agents.evaluation_agent import evaluation_agent
from ....core.redis import get_redis_client, store_interview_session, get_interview_session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start",
    response_model=InterviewResponse,
    # response_model=Dict,
    summary="Start Adaptive Interview Session",
    description="Start a new adaptive interview session with resume analysis and dynamic question generation",
    response_description="Created interview session with session ID",
    tags=["Interviews"])
async def start_interview(request: InterviewCreate) -> InterviewResponse:
    """
    Start a new adaptive interview session.
    
    This endpoint creates a new interview session, analyzes the candidate's
    resume, and prepares for dynamic question generation based on the
    candidate's background and position requirements.
    
    Args:
        request: Interview creation request with candidate info and files
        
    Returns:
        InterviewResponse: Interview session information
        
    Raises:
        HTTPException: If interview creation fails
    """
    try:
        logger.info(f"Starting interview for candidate: {request.candidate.name}")
        
        # Validate request
        if not request.candidate.files:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
        
        # Process uploaded files
        logger.info(f"Processing {len(request.candidate.files)} uploaded files")
        
        # Get file content for resume analysis
        resume_files_content = []
        for file_ref in request.candidate.files:
            file_content = await file_upload_service.get_file_content(file_ref.file_id)
            if file_content:
                resume_files_content.append({
                    'name': file_ref.filename,
                    'type': file_ref.file_type,
                    'size': len(file_content),
                    'content': file_content
                })
            else:
                logger.warning(f"Could not retrieve content for file: {file_ref.file_id}")
        
        if not resume_files_content:
            raise HTTPException(
                status_code=400,
                detail="No file content could be retrieved for analysis"
            )
        
        # Analyze resume content
        logger.info("Analyzing resume content")
        resume_analysis = await resume_analyzer.analyze_resume(resume_files_content, request.candidate.position)
        
        # Create session ID
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        # Create candidate profile with analysis
        candidate_profile_with_analysis = CandidateProfileWithAnalysis(
            name=request.candidate.name,
            email=request.candidate.email,
            position=request.candidate.position,
            experience_level=request.candidate.experience_level,
            interview_type=request.candidate.interview_type,
            files=request.candidate.files,  # Use file references
            resume_analysis=resume_analysis,
        )
        
        # Store session data in Redis
        session_data = {
            "session_id": session_id,
            "candidate": candidate_profile_with_analysis.dict(),
            "resume_analysis": resume_analysis.dict() if resume_analysis else {},
            "position": request.candidate.position,
            "status": "started",
            "started_at": "2024-01-15T10:30:00Z",  # In real app, use actual timestamp
            "current_question_index": 0,
            "total_questions_asked": 0,
            "average_score": 0.0,
            "responses": [],
            "questions": [],
        }
        
        await store_interview_session(session_id, session_data)
        
        # Create response
        response = InterviewResponse(
            session_id=session_id,
            candidate=candidate_profile_with_analysis,
            position=request.candidate.position,
            status="started",
            started_at="2024-01-15T10:30:00Z",
            current_question_index=0,
            total_questions_asked=0,
            average_score=0.0,
        )
        
        logger.info(f"Interview started successfully: {session_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start interview: {str(e)}"
        )


@router.get("/{session_id}/next-question",
    response_model=QuestionResponse,
    summary="Get Next Question",
    description="""
    Get the next question for an interview session.
    
    This endpoint uses the adaptive interview agent to generate
    contextually relevant questions based on:
    - Candidate's resume analysis
    - Previous responses and performance
    - Position requirements and experience level
    - Interview type and difficulty progression
    
    ## Adaptive Features:
    - Questions adapt to candidate's skill level
    - Difficulty increases based on performance
    - Context-aware question generation
    - Follow-up questions based on responses
    """,
    response_description="Next question with context and timing information",
    tags=["Interviews"],
    responses={
        200: {
            "description": "Next question retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "question": {
                            "id": "q_123",
                            "text": "Can you explain the difference between REST and GraphQL APIs?",
                            "category": "API Design",
                            "difficulty": "medium",
                            "expected_duration": 300,
                            "context": {
                                "focus_area": "API Design",
                                "skill_level": "mid-level"
                            },
                            "follow_up_hints": [
                                "Consider performance implications",
                                "Think about client-server communication"
                            ]
                        },
                        "session_id": "session_123456789",
                        "question_number": 1,
                        "time_limit": 300,
                        "context": {
                            "previous_performance": "good",
                            "difficulty_level": "medium"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview session not found"
                    }
                }
            }
        }
    })
async def get_next_question(session_id: str) -> QuestionResponse:
    """
    Get the next question for an interview session.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        QuestionResponse: Next question with context
        
    Raises:
        HTTPException: If session not found or question generation fails
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="Interview session not found"
            )
        
        # Generate next question using adaptive agent
        question = await adaptive_interview_agent.generate_next_question(
            candidate_profile=session_data.get("candidate", {}),
            previous_responses=session_data.get("responses", []),
            resume_analysis=session_data.get("resume_analysis", {}),
            position=session_data.get("position", "Software Engineer"),
            current_difficulty=session_data.get("current_difficulty", "medium"),
            interview_progress=float(session_data.get("current_question_index", 0)) / 10.0,  # Assuming 10 questions total
            question_count=int(session_data.get("current_question_index", 0))
        )
        
        # Update session data
        updated_session_data = session_data.copy()
        updated_session_data["current_question_index"] = int(session_data.get("current_question_index", 0)) + 1
        updated_session_data["total_questions_asked"] = int(session_data.get("total_questions_asked", 0)) + 1
        await store_interview_session(session_id, updated_session_data)
        
        return QuestionResponse(
            question=question,
            session_id=session_id,
            question_number=int(session_data.get("current_question_index", 0)) + 1,
            time_limit=question.expected_duration,
            context=question.context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next question: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get next question: {str(e)}"
        )


@router.post("/{session_id}/respond",
    response_model=SubmitResponseResult,
    summary="Submit Response",
    description="Submit a response to the current question and get evaluation",
    response_description="Response evaluation and next steps",
    tags=["Interviews"])
async def submit_response(session_id: str, request: ResponseSubmit) -> JSONResponse:
    """
    Submit a response to the current question.
    
    Args:
        session_id: Interview session ID
        request: Response submission data
        
    Returns:
        JSONResponse: Response evaluation and next steps
        
    Raises:
        HTTPException: If session not found or evaluation fails
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="Interview session not found"
            )
        
        # Get the current question from session or create a placeholder
        current_question = Question(
            id=request.question_id,
            text="Current interview question",  # This should come from session
            category="technical",
            difficulty="medium",
            expected_duration=300,
            context={},
            follow_up_hints=[]
        )
        
        # Evaluate response using AI agent
        evaluation = await adaptive_interview_agent.evaluate_response(
            question=current_question,
            response=request.answer,
            candidate_profile=session_data.get("candidate", {}),
            resume_analysis=session_data.get("resume_analysis", {}),
            position=session_data.get("position", "Software Engineer")
        )
        
        # Store response in session
        response_data = {
            "question_id": request.question_id,
            "answer": request.answer,
            "time_taken": request.time_taken,
            "evaluation": evaluation.dict(),
            "timestamp": "2024-01-15T10:35:00Z"  # In real app, use actual timestamp
        }
        
        # Add response to session
        responses = session_data.get("responses", [])
        responses.append(response_data)
        await store_interview_session(session_id, {"responses": str(responses)})
        
        # Update average score
        scores = [r.get("evaluation_score", 0) for r in session_data["responses"] if r.get("evaluation_score")]
        if scores:
            session_data["average_score"] = sum(scores) / len(scores)
        
        # Update difficulty based on evaluation
        session_data["current_difficulty"] = evaluation.suggested_difficulty.value
        
        # Update session in Redis
        await store_interview_session(session_id, session_data)
        
        response_data = {
            "evaluation": evaluation,
            "next_steps": "Continue with next question or finalize interview"
        }
        logging.warning(f"Returning from /respond: {response_data}")
        try:
            encoded = jsonable_encoder(response_data)
        except Exception as e:
            logging.error(f"jsonable_encoder failed: {e}")
            raise HTTPException(status_code=500, detail=f"Serialization error: {e}")
        return JSONResponse(content=encoded)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit response: {str(e)}"
        )


@router.post("/{session_id}/finalize",
    response_model=FinalizeResult,
    summary="Finalize Interview",
    description="""
    Finalize the interview and generate comprehensive report.
    
    This endpoint:
    1. Analyzes all responses and performance data
    2. Generates detailed evaluation report
    3. Provides hiring recommendations
    4. Identifies skill gaps and improvement areas
    5. Creates final interview summary
    
    ## Report Features:
    - Overall performance assessment
    - Detailed skill evaluation
    - Hiring recommendation with confidence
    - Improvement suggestions
    - Performance trends and patterns
    """,
    response_description="Interview finalization with comprehensive report",
    tags=["Interviews"],
    responses={
        200: {
            "description": "Interview finalized successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "completed",
                        "message": "Interview finalized successfully",
                        "session_id": "session_123456789",
                        "report_summary": {
                            "overall_score": 8.2,
                            "hiring_recommendation": "hire",
                            "confidence_level": 0.85,
                            "total_questions": 5,
                            "total_responses": 5,
                            "average_response_time": 180
                        }
                    }
                }
            }
        },
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview session not found"
                    }
                }
            }
        }
    })
async def finalize_interview(session_id: str) -> FinalizeResult:
    """
    Finalize the interview and generate comprehensive report.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        FinalizeResult: Interview finalization with report summary
        
    Raises:
        HTTPException: If session not found or finalization fails
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="Interview session not found"
            )
        
        # Generate comprehensive report using evaluation agent
        report = await evaluation_agent.generate_final_report(
            session_id=session_id,
            candidate_profile=session_data.get("candidate", {}),
            resume_analysis=session_data.get("resume_analysis", {}),
            responses=session_data.get("responses", []),
            questions=session_data.get("questions", [])
        )
        
        # Update session status
        await store_interview_session(session_id, {"status": "completed"})
        await store_interview_session(session_id, {"final_report": report})
        
        return FinalizeResult(
            status="completed",
            message="Interview finalized successfully",
            session_id=session_id,
            report_summary={
                "overall_score": report.get("overall_score", 0.0),
                "hiring_recommendation": report.get("hiring_recommendation", "unknown"),
                "confidence_level": report.get("confidence_level", 0.0),
                "total_questions": report.get("total_questions", 0),
                "total_responses": report.get("total_responses", 0),
                "average_response_time": report.get("average_response_time", 0.0)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finalizing interview: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to finalize interview: {str(e)}"
        )


@router.get("/{session_id}/report",
    response_model=InterviewReport,
    summary="Get Interview Report",
    description="""
    Retrieve the complete interview report.
    
    This endpoint returns the comprehensive interview report including:
    - Overall performance assessment
    - Detailed skill evaluations
    - Hiring recommendations
    - Improvement suggestions
    - Performance analytics
    
    ## Report Sections:
    - Executive Summary
    - Technical Assessment
    - Communication Evaluation
    - Problem-solving Analysis
    - Cultural Fit Assessment
    - Hiring Recommendation
    - Improvement Suggestions
    """,
    response_description="Complete interview report with detailed analysis",
    tags=["Interviews"],
    responses={
        200: {
            "description": "Interview report retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "session_123456789",
                        "candidate": {
                            "name": "John Doe",
                            "email": "john.doe@example.com",
                            "position": "Software Engineer"
                        },
                        "overall_score": 8.2,
                        "technical_score": 8.5,
                        "communication_score": 8.0,
                        "hiring_recommendation": "hire",
                        "confidence_level": 0.85,
                        "strengths": ["Strong technical skills", "Good communication"],
                        "areas_for_improvement": ["Could provide more examples"],
                        "recommendations": ["Consider for hire", "Provide mentorship"]
                    }
                }
            }
        },
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Interview session not found"
                    }
                }
            }
        }
    })
async def get_interview_report(session_id: str) -> InterviewReport:
    """
    Get the complete interview report.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        InterviewReport: Complete interview report
        
    Raises:
        HTTPException: If session not found
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="Interview session not found"
            )
        
        # Get final report if available
        final_report = session_data.get("final_report", {})
        
        if not final_report:
            raise HTTPException(
                status_code=404,
                detail="Interview report not available"
            )
        
        return InterviewReport(**final_report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get interview report: {str(e)}"
        ) 