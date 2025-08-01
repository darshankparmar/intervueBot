"""
Adaptive Interview endpoints.

This module provides endpoints for managing adaptive interview sessions
with resume analysis and dynamic question generation.
"""

import uuid
from typing import Dict, List, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException

from intervuebot.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    QuestionResponse,
    ResponseSubmit,
    CandidateProfile,
    InterviewSession,
    Response,
    InterviewReport,
    DifficultyLevel
)
from intervuebot.agents.adaptive_interview_agent import adaptive_interview_agent
from intervuebot.services.resume_analyzer import resume_analyzer
from intervuebot.core.redis import store_interview_session, get_interview_session, delete_interview_session

router = APIRouter()


@router.post("/start", 
    response_model=InterviewResponse,
    summary="Start Adaptive Interview Session",
    description="Start a new adaptive interview session with resume analysis and dynamic question generation",
    response_description="Created interview session with session ID",
    tags=["Interviews"])
async def start_interview(interview_data: InterviewCreate) -> InterviewResponse:
    """
    Start a new adaptive interview session.
    
    This endpoint creates a new interview session, analyzes the candidate's
    resume, and prepares for dynamic question generation based on the
    candidate's background and position requirements.
    
    Args:
        interview_data: Interview creation data including candidate profile and resume
        
    Returns:
        InterviewResponse: Created interview session with session ID
        
    Raises:
        HTTPException: If interview creation fails
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        now_iso = datetime.utcnow().isoformat() + "Z"
        
        # Analyze resume if provided
        resume_analysis = None
        if interview_data.candidate.files:
            resume_analysis = await resume_analyzer.analyze_resume(
                resume_files=interview_data.candidate.files,
                position=interview_data.candidate.position
            )
        
        # Update candidate profile with resume analysis
        candidate_profile = interview_data.candidate
        if resume_analysis:
            candidate_profile.resume_analysis = resume_analysis
        
        # Create interview session data
        session_data = {
            "session_id": session_id,
            "candidate": candidate_profile.dict(),
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
            "duration_minutes": interview_data.duration_minutes
        }
        
        # Store session in Redis
        await store_interview_session(session_id, session_data)
        
        return InterviewResponse(
            session_id=session_id,
            candidate=candidate_profile,
            position=interview_data.candidate.position,
            status="in_progress",
            started_at=now_iso,
            current_question_index=0,
            total_questions_asked=0,
            average_score=0.0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")


@router.get("/{session_id}/next-question", 
    response_model=QuestionResponse,
    summary="Get Next Adaptive Question",
    description="Get the next question based on previous responses and resume analysis",
    response_description="Next question with context",
    tags=["Interviews"])
async def get_next_question(session_id: str) -> QuestionResponse:
    """
    Get the next adaptive question for an interview session.
    
    This endpoint generates the next question based on:
    - Previous responses and their quality
    - Resume analysis and candidate background
    - Current interview progress and difficulty
    - Position requirements and skill gaps
    
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
        candidate_profile = CandidateProfile(**session_data["candidate"])
        previous_responses = [Response(**r) for r in session_data["responses"]]
        resume_analysis = None
        if session_data["candidate"].get("resume_analysis"):
            from intervuebot.schemas.interview import ResumeAnalysis
            resume_analysis = ResumeAnalysis(**session_data["candidate"]["resume_analysis"])
        
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
    description="Submit a response to the current question and get evaluation",
    response_description="Response evaluation and next steps",
    tags=["Interviews"])
async def submit_response(session_id: str, response: ResponseSubmit) -> Dict[str, Any]:
    """
    Submit a response to the current question.
    
    This endpoint evaluates the candidate's response and updates
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
        candidate_profile = CandidateProfile(**session_data["candidate"])
        resume_analysis = None
        if session_data["candidate"].get("resume_analysis"):
            from intervuebot.schemas.interview import ResumeAnalysis
            resume_analysis = ResumeAnalysis(**session_data["candidate"]["resume_analysis"])
        
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
    description="End the interview and generate comprehensive evaluation report",
    response_description="Interview completion confirmation",
    tags=["Interviews"])
async def finalize_interview(session_id: str) -> Dict[str, Any]:
    """
    Finalize the interview and generate comprehensive report.
    
    This endpoint ends the interview session and generates a comprehensive
    evaluation report based on all responses and resume analysis.
    
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
    description="Get the comprehensive interview evaluation report",
    response_description="Complete interview evaluation report",
    tags=["Interviews"])
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
        candidate=CandidateProfile(**session_data["candidate"]),
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