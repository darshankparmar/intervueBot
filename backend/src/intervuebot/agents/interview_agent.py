"""
Interview Agent using Agno Framework.

This module implements the main interview agent that conducts
AI-powered interviews using the Agno framework.
"""

import logging
from typing import Dict, List, Optional, Any

from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat

from intervuebot.core.config import settings
from intervuebot.schemas.interview import Question, Response, CandidateProfile

logger = logging.getLogger(__name__)


class InterviewAgent:
    """
    Main interview agent using Agno framework.
    
    This agent conducts comprehensive technical and behavioral interviews,
    manages conversation context, and adapts to candidate responses.
    """
    
    def __init__(self):
        """Initialize the interview agent with dynamic LLM selection."""
        provider = settings.DEFAULT_LLM_PROVIDER.lower()
        model_id = settings.DEFAULT_LLM_MODEL
        if provider == "openai":
            model = OpenAIChat(id=model_id, api_key=settings.OPENAI_API_KEY)
        else:
            model = Gemini(id=model_id, api_key=settings.GOOGLE_API_KEY)
        self.agent = Agent(
            model=model,
            name="IntervueBot",
            role="AI Interview Conductor",
            goal="Conduct comprehensive technical and behavioral interviews to assess candidate skills and fit",
            instructions=[
                "You are an expert AI interviewer with deep knowledge across multiple domains",
                "including software engineering, data science, product management, and business roles.",
                "You excel at asking insightful questions, evaluating responses, and providing constructive feedback.",
                "You adapt your interview style based on the candidate's experience level and the specific role requirements."
            ],
            markdown=True,
        )
    
    def generate_question(self, position: str, category: str, difficulty: str, previous_questions: List[str] = None) -> str:
        """
        Generate an interview question based on position, category, and difficulty.
        
        Args:
            position: Job position being interviewed for
            category: Question category (technical, behavioral, situational)
            difficulty: Question difficulty level (easy, medium, hard)
            previous_questions: List of previously asked questions to avoid repetition
            
        Returns:
            str: Generated interview question
        """
        prompt = f"""
        Generate a {difficulty} level {category} question for a {position} interview.
        
        Requirements:
        - Make it specific to {position}
        - Ensure it's appropriate for {difficulty} level
        - Focus on {category} aspects
        - Keep it clear and concise
        - Include context if needed
        
        {f'Previously asked questions: {", ".join(previous_questions or [])}. Avoid similar questions.' if previous_questions else ''}
        
        Return only the question text, no additional formatting.
        """
        
        agent_response = self.agent.run(prompt)
        return agent_response.content
    
    def evaluate_response(self, question: str, response: str, position: str, category: str) -> Dict[str, Any]:
        """
        Evaluate a candidate's response to an interview question.
        
        Args:
            question: The interview question
            response: Candidate's response
            position: Job position
            category: Question category
            
        Returns:
            Dict containing evaluation score and feedback
        """
        prompt = f"""
        Evaluate this interview response for a {position} position.
        
        Question: {question}
        Response: {response}
        Category: {category}
        
        Evaluation criteria:
        - Technical accuracy (for technical questions)
        - Communication clarity
        - Relevance to the question
        - Depth of understanding
        - Practical experience demonstrated
        
        Provide:
        1. A score from 1-10
        2. Detailed feedback
        3. Areas for improvement
        4. Overall assessment
        
        Format your response as JSON with keys: score, feedback, areas_for_improvement, assessment
        """
        
        agent_response = self.agent.run(prompt)
        return {
            "score": 7,  # Placeholder - would parse from LLM response
            "feedback": agent_response.content,
            "areas_for_improvement": [],
            "assessment": "Good response with room for improvement"
        }
    
    async def conduct_interview_session(
        self,
        candidate: CandidateProfile,
        position: str,
        interview_type: str = "technical",
        max_questions: int = 10
    ) -> Dict[str, Any]:
        """
        Conduct a complete interview session.
        
        Args:
            candidate: Candidate profile information
            position: Job position
            interview_type: Type of interview (technical, behavioral, mixed)
            max_questions: Maximum number of questions to ask
            
        Returns:
            Dict containing interview results and evaluation
        """
        logger.info(f"Starting interview session for {candidate.name} - {position}")
        
        # Initialize interview session
        session_data = {
            "candidate": candidate,
            "position": position,
            "interview_type": interview_type,
            "questions": [],
            "responses": [],
            "evaluations": [],
            "current_difficulty": "medium"
        }
        
        # Conduct interview
        for question_num in range(max_questions):
            # Generate question
            question = self.generate_question(
                position=position,
                category=interview_type,
                difficulty=session_data["current_difficulty"],
                previous_questions=[q["text"] for q in session_data["questions"]]
            )
            
            # Store question
            session_data["questions"].append({
                "number": question_num + 1,
                "text": question,
                "category": interview_type,
                "difficulty": session_data["current_difficulty"]
            })
            
            # In a real implementation, you'd wait for candidate response here
            # For now, we'll simulate a response
            simulated_response = f"Simulated response to question {question_num + 1}"
            
            # Evaluate response
            evaluation = self.evaluate_response(
                question=question,
                response=simulated_response,
                position=position,
                category=interview_type
            )
            
            # Store response and evaluation
            session_data["responses"].append(simulated_response)
            session_data["evaluations"].append(evaluation)
        
        # Generate final assessment
        final_assessment = self._generate_final_assessment(session_data)
        session_data["final_assessment"] = final_assessment
        
        logger.info(f"Completed interview session for {candidate.name}")
        return session_data
    
    def _generate_final_assessment(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final interview assessment."""
        prompt = f"""
        Generate a final assessment for this interview session.
        
        Position: {session_data['position']}
        Candidate: {session_data['candidate'].name}
        Total questions: {len(session_data['questions'])}
        Average score: {sum(e['score'] for e in session_data['evaluations']) / len(session_data['evaluations'])}
        
        Provide:
        1. Overall score (1-10)
        2. Key strengths
        3. Areas for improvement
        4. Recommendation (hire, consider, reject)
        5. Detailed feedback
        
        Format as JSON with keys: overall_score, strengths, areas_for_improvement, recommendation, feedback
        """
        
        agent_response = self.agent.run(prompt)
        
        # Parse assessment (in real implementation, use proper JSON parsing)
        return {
            "overall_score": 7.5,
            "strengths": ["Technical knowledge", "Communication"],
            "areas_for_improvement": ["Experience depth"],
            "recommendation": "consider",
            "feedback": agent_response.content
        }


# Global interview agent instance
interview_agent = InterviewAgent() 