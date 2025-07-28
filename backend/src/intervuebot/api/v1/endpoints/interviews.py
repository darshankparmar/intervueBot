"""
Interview endpoints.

This module provides endpoints for managing interview sessions,
questions, and responses using Agno agents.
"""

import uuid
from typing import Dict, List, Any

from fastapi import APIRouter, HTTPException

from intervuebot.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    QuestionResponse,
    ResponseSubmit,
    CandidateProfile,
)
from intervuebot.agents.interview_agent import interview_agent
from intervuebot.agents.evaluation_agent import evaluation_agent
from intervuebot.agents.question_generator_agent import question_generator_agent
from intervuebot.core.redis import store_interview_session, get_interview_session, delete_interview_session
from intervuebot.core.interview_sequence import interview_sequence_manager

router = APIRouter()


@router.post("/start", 
    response_model=InterviewResponse,
    summary="Start Interview Session",
    description="Start a new AI-powered interview session using Agno agents",
    response_description="Created interview session with session ID",
    tags=["Interviews"])
async def start_interview(interview_data: InterviewCreate) -> InterviewResponse:
    """
    Start a new interview session using Agno agents.
    
    This endpoint creates a new interview session and generates initial
    questions using the question generator agent. The session is stored
    in Redis for persistence.
    
    Args:
        interview_data: Interview creation data including candidate profile
        
    Returns:
        InterviewResponse: Created interview session with session ID
        
    Raises:
        HTTPException: If interview creation fails
        
    Example Request:
        {
            "candidate": {
                "name": "John Doe",
                "email": "john@example.com",
                "experience_years": 3,
                "skills": ["Python", "JavaScript"]
            },
            "position": "Software Engineer",
            "interview_type": "technical",
            "duration_minutes": 60
        }
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Generate interview sequence based on candidate profile
        interview_phases = interview_sequence_manager.generate_interview_sequence(
            candidate=interview_data.candidate,
            position=interview_data.position,
            interview_type=interview_data.interview_type,
            total_duration=interview_data.duration_minutes
        )
        
        # Generate questions for each phase
        all_questions = []
        for phase in interview_phases:
            phase_questions = question_generator_agent.generate_question_sequence(
                position=interview_data.position,
                interview_type=interview_data.interview_type,
                experience_level=f"{interview_data.candidate.experience_years} years",
                required_skills=interview_data.candidate.skills
            )
            # Limit questions to phase count
            phase_questions = phase_questions[:phase.question_count]
            for question in phase_questions:
                question["phase"] = phase.phase_name
                question["phase_order"] = phase.phase_order
            all_questions.extend(phase_questions)
        
        # Create interview session data
        session_data = {
            "session_id": session_id,
            "candidate": interview_data.candidate.dict(),
            "position": interview_data.position,
            "interview_type": interview_data.interview_type,
            "duration_minutes": interview_data.duration_minutes,
            "phases": [phase.dict() for phase in interview_phases],
            "questions": all_questions,
            "current_phase": interview_phases[0].phase_name if interview_phases else "introduction",
            "current_question_index": 0,
            "responses": [],
            "evaluations": [],
            "status": "in_progress",
            "started_at": "2024-01-01T00:00:00Z"  # TODO: Add proper timestamp
        }
        
        # Store session in Redis
        await store_interview_session(session_id, session_data)
        
        return InterviewResponse(
            session_id=session_id,
            candidate=interview_data.candidate,
            position=interview_data.position,
            status="in_progress",
            started_at="2024-01-01T00:00:00Z",  # TODO: Add proper timestamp
            total_questions=len(questions),
            completed_questions=0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")


@router.get("/{session_id}/question", response_model=QuestionResponse)
async def get_next_question(session_id: str) -> QuestionResponse:
    """
    Get the next question for an interview session using Agno agents.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        QuestionResponse: Next question
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        if session_data["status"] != "in_progress":
            raise HTTPException(status_code=400, detail="Interview session is not in progress")
        
        current_index = session_data["current_question_index"]
        if current_index >= len(session_data["questions"]):
            raise HTTPException(status_code=404, detail="No more questions available")
        
        # Get current question
        question_data = session_data["questions"][current_index]
        
        return QuestionResponse(
            question={
                "id": f"q_{current_index}",
                "text": question_data["question"],
                "category": question_data["category"],
                "difficulty": question_data.get("difficulty", "medium"),
                "expected_duration": question_data.get("time_estimate", 300)
            },
            session_id=session_id,
            question_number=current_index + 1,
            time_limit=question_data.get("time_estimate", 300) * 60  # Convert to seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get question: {str(e)}")


@router.post("/{session_id}/respond")
async def submit_response(session_id: str, response: ResponseSubmit) -> Dict[str, str]:
    """
    Submit a response to a question using Agno agents.
    
    Args:
        session_id: Interview session ID
        response: Candidate response
        
    Returns:
        Dict[str, str]: Response confirmation
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        if session_data["status"] != "in_progress":
            raise HTTPException(status_code=400, detail="Interview session is not in progress")
        
        current_index = session_data["current_question_index"]
        if current_index >= len(session_data["questions"]):
            raise HTTPException(status_code=400, detail="No active question to respond to")
        
        # Get current question
        question_data = session_data["questions"][current_index]
        
        # Evaluate response using evaluation agent
        evaluation = await evaluation_agent.evaluate_complete_response(
            question=question_data["question"],
            response=response.answer,
            position=session_data["position"],
            category=question_data["category"],
            required_skills=session_data["candidate"]["skills"]
        )
        
        # Store response and evaluation
        session_data["responses"].append({
            "question_id": response.question_id,
            "answer": response.answer,
            "time_taken": response.time_taken
        })
        
        session_data["evaluations"].append(evaluation)
        session_data["current_question_index"] += 1
        
        # Update session in Redis
        await store_interview_session(session_id, session_data)
        
        return {
            "status": "success",
            "message": "Response submitted and evaluated successfully",
            "evaluation_score": evaluation["score"]["overall_score"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit response: {str(e)}")


@router.post("/{session_id}/end")
async def end_interview(session_id: str) -> Dict[str, str]:
    """
    End an interview session using Agno agents.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        Dict[str, str]: Session end confirmation
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        # Update session status
        session_data["status"] = "completed"
        session_data["ended_at"] = "2024-01-01T00:00:00Z"  # TODO: Add proper timestamp
        
        # Generate final assessment using interview agent
        candidate_profile = CandidateProfile(**session_data["candidate"])
        final_assessment = await interview_agent.conduct_interview_session(
            candidate=candidate_profile,
            position=session_data["position"],
            interview_type=session_data["interview_type"],
            max_questions=len(session_data["questions"])
        )
        
        session_data["final_assessment"] = final_assessment["final_assessment"]
        
        # Update session in Redis
        await store_interview_session(session_id, session_data)
        
        return {
            "status": "success",
            "message": "Interview completed successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end interview: {str(e)}")


@router.get("/{session_id}/report")
async def get_interview_report(session_id: str) -> Dict[str, Any]:
    """
    Get interview evaluation report using Agno agents.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        Dict[str, Any]: Interview evaluation report
    """
    try:
        # Get session data from Redis
        session_data = await get_interview_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        if session_data["status"] != "completed":
            raise HTTPException(status_code=400, detail="Interview session is not completed")
        
        # Return the final assessment
        return {
            "session_id": session_id,
            "candidate": session_data["candidate"],
            "position": session_data["position"],
            "final_assessment": session_data["final_assessment"],
            "questions_asked": len(session_data["questions"]),
            "responses_evaluated": len(session_data["evaluations"]),
            "average_score": sum(e["score"]["overall_score"] for e in session_data["evaluations"]) / len(session_data["evaluations"]) if session_data["evaluations"] else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}") 