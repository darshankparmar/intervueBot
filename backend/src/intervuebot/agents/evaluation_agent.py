"""
Evaluation Agent using Agno Framework.

This module implements the evaluation agent that scores candidate responses
and provides detailed feedback using the Agno framework.
"""

import logging
from typing import Dict, List, Any

from agno.agent import Agent
from agno.models.google import Gemini

from ..core.config import settings

logger = logging.getLogger(__name__)


class EvaluationAgent:
    """
    Evaluation agent using Agno framework.
    
    This agent specializes in evaluating candidate responses and providing
    detailed feedback and scoring.
    """
    
    def __init__(self):
        """Initialize the evaluation agent."""
        # Initialize LLM with Google Gemini
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash-lite", api_key=settings.GOOGLE_API_KEY),
            name="EvaluationBot",
            role="Interview Response Evaluator",
            goal="Provide comprehensive and fair evaluation of candidate responses with detailed feedback",
            instructions=[
                "You are an expert evaluator with deep understanding of various job roles and industries.",
                "You excel at assessing technical skills, communication abilities, problem-solving approaches, and cultural fit.",
                "You provide constructive feedback that helps candidates understand their strengths and areas for improvement."
            ],
            markdown=True,
        )
    
    def score_response(self, question: str, response: str, position: str, category: str) -> Dict[str, Any]:
        """
        Score a candidate's response to an interview question.
        
        Args:
            question: The interview question
            response: Candidate's response
            position: Job position
            category: Question category
            
        Returns:
            Dict containing score and evaluation details
        """
        prompt = f"""
        Score this interview response on a scale of 1-10.
        
        Position: {position}
        Category: {category}
        Question: {question}
        Response: {response}
        
        Scoring criteria:
        - Technical accuracy (for technical questions): 0-3 points
        - Communication clarity: 0-2 points
        - Relevance to question: 0-2 points
        - Depth of understanding: 0-2 points
        - Practical experience demonstrated: 0-1 point
        
        Provide:
        1. Overall score (1-10)
        2. Breakdown by criteria
        3. Justification for score
        
        Format as JSON with keys: overall_score, breakdown, justification
        """
        
        agent_response = self.agent.run(prompt)
        
        # Parse evaluation (in real implementation, use proper JSON parsing)
        return {
            "overall_score": 7,
            "breakdown": {
                "technical_accuracy": 2,
                "communication_clarity": 2,
                "relevance": 1,
                "depth": 1,
                "experience": 1
            },
            "justification": agent_response.content
        }
    
    def evaluate_complete_response(
        self,
        question: str,
        response: str,
        position: str,
        category: str,
        required_skills: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform complete evaluation of a candidate response.
        
        Args:
            question: The interview question
            response: Candidate's response
            position: Job position
            category: Question category
            required_skills: List of required skills for the position
            
        Returns:
            Dict containing complete evaluation
        """
        logger.info(f"Evaluating response for {position} position")
        
        # Score the response
        score_data = self.score_response(question, response, position, category)
        
        # Generate comprehensive feedback
        feedback_prompt = f"""
        Generate comprehensive feedback for this candidate response.
        
        Question: {question}
        Response: {response}
        Position: {position}
        Category: {category}
        Score: {score_data['overall_score']}/10
        
        Provide:
        1. Detailed analysis of the response
        2. Specific strengths demonstrated
        3. Areas for improvement
        4. Suggestions for better answers
        5. Overall assessment
        
        Write clear, actionable feedback that would help the candidate improve.
        """
        
        feedback_response = self.agent.run(feedback_prompt)
        
        # Compile complete evaluation
        complete_evaluation = {
            "question": question,
            "response": response,
            "position": position,
            "category": category,
            "score": score_data,
            "feedback": feedback_response.content,
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: Add proper timestamp
        }
        
        logger.info(f"Completed evaluation for {position} position")
        return complete_evaluation

    async def generate_final_report(
        self,
        session_id: str,
        candidate_profile: Dict[str, Any],
        resume_analysis: Dict[str, Any],
        responses: List[Dict[str, Any]],
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive final interview report.
        
        Args:
            session_id: Interview session ID
            candidate_profile: Candidate profile information
            resume_analysis: Resume analysis results
            responses: List of candidate responses
            questions: List of questions asked
            
        Returns:
            Dict containing comprehensive interview report
        """
        logger.info(f"Generating final report for session {session_id}")
        
        try:
            # Calculate overall metrics
            total_questions = len(questions)
            total_responses = len(responses)
            
            # Calculate average score
            scores = []
            response_times = []
            for response in responses:
                if 'evaluation_score' in response and response['evaluation_score']:
                    scores.append(response['evaluation_score'])
                if 'time_taken' in response and response['time_taken']:
                    response_times.append(response['time_taken'])
            
            overall_score = sum(scores) / len(scores) if scores else 0.0
            average_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            
            # Determine hiring recommendation based on score
            if overall_score >= 8.0:
                hiring_recommendation = "strong_hire"
                confidence_level = 0.9
            elif overall_score >= 7.0:
                hiring_recommendation = "hire"
                confidence_level = 0.8
            elif overall_score >= 6.0:
                hiring_recommendation = "consider"
                confidence_level = 0.6
            else:
                hiring_recommendation = "do_not_hire"
                confidence_level = 0.7
            
            # Generate comprehensive report using AI
            report_prompt = f"""
            Generate a comprehensive interview report for this candidate.
            
            CANDIDATE INFORMATION:
            - Name: {candidate_profile.get('name', 'Unknown')}
            - Position: {candidate_profile.get('position', 'Unknown')}
            - Experience Level: {candidate_profile.get('experience_level', 'Unknown')}
            
            INTERVIEW PERFORMANCE:
            - Total Questions: {total_questions}
            - Total Responses: {total_responses}
            - Overall Score: {overall_score:.1f}/10
            - Average Response Time: {average_response_time:.1f} seconds
            
            RESUME ANALYSIS:
            - Skills: {', '.join(resume_analysis.get('extracted_skills', [])[:5])}
            - Experience: {resume_analysis.get('experience_years', 0)} years
            - Education: {resume_analysis.get('education', 'Not specified')}
            
            Provide a comprehensive report including:
            1. Executive Summary
            2. Technical Assessment
            3. Communication Evaluation
            4. Problem-solving Analysis
            5. Cultural Fit Assessment
            6. Hiring Recommendation
            7. Improvement Suggestions
            8. Next Steps
            
            Make the report professional, detailed, and actionable.
            """
            
            report_response = self.agent.run(report_prompt)
            
            # Create final report structure
            final_report = {
                "session_id": session_id,
                "candidate": candidate_profile,
                "overall_score": round(overall_score, 1),
                "technical_score": round(overall_score * 0.4, 1),
                "communication_score": round(overall_score * 0.3, 1),
                "problem_solving_score": round(overall_score * 0.3, 1),
                "hiring_recommendation": hiring_recommendation,
                "confidence_level": confidence_level,
                "total_questions": total_questions,
                "total_responses": total_responses,
                "average_response_time": round(average_response_time, 1),
                "detailed_analysis": report_response.content,
                "strengths": self._extract_strengths(responses, overall_score),
                "areas_for_improvement": self._extract_improvement_areas(responses, overall_score),
                "recommendations": self._generate_recommendations(hiring_recommendation, overall_score),
                "timestamp": "2024-01-01T00:00:00Z"  # TODO: Add proper timestamp
            }
            
            logger.info(f"Generated final report for session {session_id}")
            return final_report
            
        except Exception as e:
            logger.error(f"Failed to generate final report: {e}")
            # Return basic report on error
            return {
                "session_id": session_id,
                "candidate": candidate_profile,
                "overall_score": 0.0,
                "hiring_recommendation": "error",
                "confidence_level": 0.0,
                "error": str(e)
            }
    
    def _extract_strengths(self, responses: List[Dict[str, Any]], overall_score: float) -> List[str]:
        """Extract candidate strengths from responses."""
        if overall_score >= 7.0:
            return ["Strong technical foundation", "Good communication skills", "Demonstrates practical experience"]
        elif overall_score >= 5.0:
            return ["Basic technical knowledge", "Some relevant experience"]
        else:
            return ["Shows willingness to learn"]
    
    def _extract_improvement_areas(self, responses: List[Dict[str, Any]], overall_score: float) -> List[str]:
        """Extract areas for improvement from responses."""
        if overall_score >= 7.0:
            return ["Could provide more specific examples", "Consider deeper technical explanations"]
        elif overall_score >= 5.0:
            return ["Improve technical depth", "Enhance communication clarity", "Provide more concrete examples"]
        else:
            return ["Focus on fundamental concepts", "Improve technical knowledge", "Enhance communication skills"]
    
    def _generate_recommendations(self, hiring_recommendation: str, overall_score: float) -> List[str]:
        """Generate recommendations based on performance."""
        if hiring_recommendation == "strong_hire":
            return ["Immediate hire", "Consider for leadership roles", "Provide mentorship opportunities"]
        elif hiring_recommendation == "hire":
            return ["Recommend for hire", "Provide onboarding support", "Assign to appropriate team"]
        elif hiring_recommendation == "consider":
            return ["Consider with reservations", "Provide additional training", "Re-evaluate after probation"]
        else:
            return ["Not recommended for this position", "Consider for other roles", "Provide constructive feedback"]


# Global evaluation agent instance
evaluation_agent = EvaluationAgent() 