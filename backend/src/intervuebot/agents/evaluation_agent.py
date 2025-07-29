"""
Evaluation Agent using Agno Framework.

This module implements the evaluation agent that scores candidate responses
and provides detailed feedback using the Agno framework.
"""

import logging
from typing import Dict, List, Any

from agno.agent import Agent
from agno.models.google import Gemini

from intervuebot.core.config import settings

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
            model=Gemini(id="gemini-2.0-flash-lite"),
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
    



# Global evaluation agent instance
evaluation_agent = EvaluationAgent() 