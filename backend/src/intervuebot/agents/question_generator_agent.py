"""
Question Generator Agent using Agno Framework.

This module implements the question generator agent that creates
dynamic and contextual interview questions using the Agno framework.
"""

import logging
from typing import Dict, List, Any, Optional

from agno.agent import Agent
from agno.models.google import Gemini

from intervuebot.core.config import settings

logger = logging.getLogger(__name__)


class QuestionGeneratorAgent:
    """
    Question generator agent using Agno framework.
    
    This agent specializes in generating dynamic, contextual interview
    questions based on position, experience level, and interview progress.
    """
    
    def __init__(self):
        """Initialize the question generator agent."""
        # Initialize LLM with Google Gemini
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash-lite", api_key=settings.GOOGLE_API_KEY),
            name="QuestionBot",
            role="Dynamic Interview Question Generator",
            goal="Generate relevant, engaging, and adaptive interview questions that effectively assess candidate skills and fit",
            instructions=[
                "You are an expert question generator with deep knowledge of various industries and job roles.",
                "You excel at creating questions that are specific to the position, appropriate for the candidate's experience level.",
                "You design questions to reveal both technical skills and soft skills.",
                "You adapt question difficulty and focus based on interview progress."
            ],
            markdown=True,
        )
    
    async def generate_technical_question(
        self,
        position: str,
        difficulty: str,
        skills: List[str],
        experience_level: str
    ) -> Dict[str, Any]:
        """
        Generate a technical interview question.
        
        Args:
            position: Job position
            difficulty: Question difficulty (easy, medium, hard)
            skills: Required technical skills
            experience_level: Candidate experience level
            
        Returns:
            Dict containing question and metadata
        """
        prompt = f"""
        Generate a {difficulty} level technical question for a {position} position.
        
        Required skills: {', '.join(skills)}
        Experience level: {experience_level}
        
        Requirements:
        - Question should test {', '.join(skills)}
        - Appropriate for {experience_level} level
        - {difficulty} difficulty
        - Clear and specific
        - Include context if needed
        - Should reveal both knowledge and problem-solving ability
        
        Return only the question text, no additional formatting.
        """
        
        agent_response = self.agent.run(prompt)
        
        return {
            "question": agent_response.content if hasattr(agent_response, 'content') else str(agent_response),
            "expected_points": ["Point 1", "Point 2"],
            "time_estimate": 5,
            "skills_tested": skills[:2],
            "category": "technical",
            "difficulty": difficulty
        }
    
    async def generate_question_sequence(
        self,
        position: str,
        interview_type: str,
        experience_level: str,
        required_skills: List[str],
        interview_progress: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a sequence of questions for an interview.
        
        Args:
            position: Job position
            interview_type: Type of interview (technical, behavioral, mixed)
            experience_level: Candidate experience level
            required_skills: Required skills for the position
            interview_progress: Current interview progress data
            
        Returns:
            List of question dictionaries
        """
        logger.info(f"Generating question sequence for {position} - {interview_type}")
        
        questions = []
        current_difficulty = "medium"
        
        # Determine question distribution based on interview type
        if interview_type == "technical":
            question_distribution = {"technical": 8, "situational": 2}
        elif interview_type == "behavioral":
            question_distribution = {"behavioral": 8, "situational": 2}
        else:  # mixed
            question_distribution = {"technical": 4, "behavioral": 4, "situational": 2}
        
        # Generate questions for each category
        for category, count in question_distribution.items():
            for i in range(count):
                try:
                    if category == "technical":
                        question = await self.generate_technical_question(
                            position=position,
                            difficulty=current_difficulty,
                            skills=required_skills,
                            experience_level=experience_level
                        )
                    elif category == "behavioral":
                        competencies = ["leadership", "teamwork", "problem-solving", "communication"]
                        competency = competencies[i % len(competencies)]
                        question = await self.generate_behavioral_question(
                            position=position,
                            competency=competency,
                            experience_level=experience_level
                        )
                    else:  # situational
                        scenario_types = ["conflict", "challenge", "deadline", "innovation"]
                        scenario_type = scenario_types[i % len(scenario_types)]
                        question = await self.generate_situational_question(
                            position=position,
                            scenario_type=scenario_type,
                            difficulty=current_difficulty
                        )
                    
                    questions.append(question)
                except Exception as e:
                    logger.error(f"Error generating {category} question: {str(e)}")
                    continue
        
        logger.info(f"Generated {len(questions)} questions for {position}")
        return questions
    
    async def generate_behavioral_question(
        self,
        position: str,
        competency: str,
        experience_level: str
    ) -> Dict[str, Any]:
        """Generate a behavioral interview question."""
        prompt = f"""
        Generate a behavioral question for a {position} position.
        
        Competency to assess: {competency}
        Experience level: {experience_level}
        
        Requirements:
        - Focus on {competency} competency
        - Appropriate for {experience_level} level
        - Use STAR method (Situation, Task, Action, Result)
        - Clear and specific
        - Should reveal past behavior and decision-making
        
        Return only the question text.
        """
        
        agent_response = self.agent.run(prompt)
        
        return {
            "question": agent_response.content if hasattr(agent_response, 'content') else str(agent_response),
            "what_to_look_for": ["Specific examples", "Clear outcomes"],
            "red_flags": ["Vague answers", "No specific examples"],
            "time_estimate": 3,
            "category": "behavioral",
            "competency": competency
        }
    
    async def generate_situational_question(
        self,
        position: str,
        scenario_type: str,
        difficulty: str
    ) -> Dict[str, Any]:
        """Generate a situational interview question."""
        prompt = f"""
        Generate a situational question for a {position} position.
        
        Scenario type: {scenario_type}
        Difficulty: {difficulty}
        
        Requirements:
        - Realistic scenario for {position}
        - {difficulty} level complexity
        - Focus on {scenario_type} situations
        - Should test problem-solving and decision-making
        - Include relevant context
        
        Return only the question text.
        """
        
        agent_response = self.agent.run(prompt)
        
        return {
            "question": agent_response.content if hasattr(agent_response, 'content') else str(agent_response),
            "expected_approach": ["Analysis", "Action plan"],
            "time_estimate": 4,
            "category": "situational",
            "scenario_type": scenario_type
        }
    



# Global question generator agent instance
question_generator_agent = QuestionGeneratorAgent() 