"""
Adaptive Interview Agent using Agno Framework.

This module implements the adaptive interview agent that generates
questions dynamically based on candidate responses, resume analysis,
and interview context.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from agno.agent import Agent
from agno.models.google import Gemini

from intervuebot.schemas.interview import (
    CandidateProfile, Question, Response, ResumeAnalysis,
    DifficultyLevel, InterviewType, ResponseEvaluation
)
from intervuebot.core.config import settings

logger = logging.getLogger(__name__)


class AdaptiveInterviewAgent:
    """
    Adaptive interview agent using Agno framework.
    
    This agent generates questions dynamically based on:
    - Previous responses and their quality
    - Resume analysis and candidate profile
    - Current interview context and progress
    - Position requirements and skill gaps
    """
    
    def __init__(self):
        """Initialize the adaptive interview agent."""
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            name="AdaptiveInterviewBot",
            role="Adaptive Interview Conductor",
            goal="Conduct intelligent, adaptive interviews that adjust based on candidate responses and background",
            instructions=[
                "You are an expert adaptive interviewer who generates questions based on context.",
                "You analyze previous responses to determine next questions.",
                "You consider resume analysis and position requirements.",
                "You adjust difficulty based on response quality.",
                "You provide follow-up questions based on candidate answers."
            ],
            markdown=True,
        )
    
    async def generate_next_question(
        self,
        candidate_profile: CandidateProfile,
        previous_responses: List[Response],
        resume_analysis: ResumeAnalysis,
        position: str,
        current_difficulty: DifficultyLevel,
        interview_progress: float,
        question_count: int
    ) -> Question:
        """
        Generate the next question based on current context.
        
        Args:
            candidate_profile: Candidate profile information
            previous_responses: List of previous responses
            resume_analysis: Resume analysis results
            position: Job position
            current_difficulty: Current difficulty level
            interview_progress: Interview progress (0.0 to 1.0)
            question_count: Number of questions asked so far
            
        Returns:
            Question: Next question to ask
        """
        try:
            # Create context for question generation
            context = self._build_question_context(
                candidate_profile, previous_responses, resume_analysis,
                position, current_difficulty, interview_progress, question_count
            )
            
            # Generate question using AI
            question_prompt = self._create_question_prompt(context)
            question_response = await self.agent.run(question_prompt)
            
            # Parse question from AI response
            question_data = self._parse_question_response(question_response.content)
            
            # Create Question object
            question = Question(
                id=f"q_{question_count + 1}",
                text=question_data.get("question", "Tell me about your experience."),
                category=question_data.get("category", "technical"),
                difficulty=DifficultyLevel(question_data.get("difficulty", "medium")),
                expected_duration=max(30, question_data.get("expected_duration", 300)),
                context=question_data.get("context", {}),
                follow_up_hints=question_data.get("follow_up_hints", [])
            )
            
            logger.info(f"Generated question {question.id} with difficulty {question.difficulty}")
            return question
            
        except Exception as e:
            logger.error(f"Failed to generate next question: {e}")
            # Return a fallback question
            return Question(
                id=f"q_{question_count + 1}",
                text="Tell me about your experience with the technologies mentioned in your resume.",
                category="technical",
                difficulty=DifficultyLevel.MEDIUM,
                expected_duration=300
            )
    
    def _build_question_context(
        self,
        candidate_profile: CandidateProfile,
        previous_responses: List[Response],
        resume_analysis: ResumeAnalysis,
        position: str,
        current_difficulty: DifficultyLevel,
        interview_progress: float,
        question_count: int
    ) -> Dict[str, Any]:
        """
        Build context for question generation.
        
        Args:
            candidate_profile: Candidate profile
            previous_responses: Previous responses
            resume_analysis: Resume analysis
            position: Job position
            current_difficulty: Current difficulty
            interview_progress: Interview progress
            question_count: Question count
            
        Returns:
            Dict[str, Any]: Context for question generation
        """
        # Calculate average response score
        avg_score = 0.0
        if previous_responses:
            scores = [r.evaluation_score for r in previous_responses if r.evaluation_score]
            avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine next difficulty based on performance
        next_difficulty = self._determine_next_difficulty(
            current_difficulty, avg_score, interview_progress
        )
        
        # Extract relevant skills from resume
        relevant_skills = resume_analysis.extracted_skills if resume_analysis else []
        
        # Get recent response themes
        recent_themes = self._extract_recent_themes(previous_responses)
        
        return {
            "candidate_name": candidate_profile.name,
            "position": position,
            "experience_level": candidate_profile.experience_level.value,
            "interview_type": candidate_profile.interview_type.value,
            "resume_skills": relevant_skills,
            "resume_experience": resume_analysis.experience_years if resume_analysis else 0.0,
            "current_difficulty": current_difficulty.value,
            "next_difficulty": next_difficulty.value,
            "interview_progress": interview_progress,
            "question_count": question_count,
            "average_score": avg_score,
            "recent_themes": recent_themes,
            "previous_responses_count": len(previous_responses)
        }
    
    def _determine_next_difficulty(
        self,
        current_difficulty: DifficultyLevel,
        average_score: float,
        interview_progress: float
    ) -> DifficultyLevel:
        """
        Determine next difficulty level based on performance.
        
        Args:
            current_difficulty: Current difficulty
            average_score: Average response score
            interview_progress: Interview progress
            
        Returns:
            DifficultyLevel: Next difficulty level
        """
        if interview_progress < 0.3:
            # Early in interview - start with medium
            return DifficultyLevel.MEDIUM
        elif average_score >= 8.0:
            # Performing well - increase difficulty
            if current_difficulty == DifficultyLevel.EASY:
                return DifficultyLevel.MEDIUM
            elif current_difficulty == DifficultyLevel.MEDIUM:
                return DifficultyLevel.HARD
            else:
                return DifficultyLevel.HARD
        elif average_score <= 5.0:
            # Struggling - decrease difficulty
            if current_difficulty == DifficultyLevel.HARD:
                return DifficultyLevel.MEDIUM
            elif current_difficulty == DifficultyLevel.MEDIUM:
                return DifficultyLevel.EASY
            else:
                return DifficultyLevel.EASY
        else:
            # Moderate performance - maintain difficulty
            return current_difficulty
    
    def _extract_recent_themes(self, previous_responses: List[Response]) -> List[str]:
        """
        Extract themes from recent responses.
        
        Args:
            previous_responses: Previous responses
            
        Returns:
            List[str]: Recent themes
        """
        if not previous_responses:
            return []
        
        # Get last 3 responses for theme analysis
        recent_responses = previous_responses[-3:]
        themes = []
        
        for response in recent_responses:
            # Simple keyword extraction (in real implementation, use NLP)
            keywords = ["python", "javascript", "react", "node", "database", "api", "testing"]
            response_lower = response.answer.lower()
            
            for keyword in keywords:
                if keyword in response_lower:
                    themes.append(keyword)
        
        return list(set(themes))  # Remove duplicates
    
    def _create_question_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create prompt for question generation.
        
        Args:
            context: Question generation context
            
        Returns:
            str: Question generation prompt
        """
        return f"""
        Generate the next interview question based on the following context:
        
        Position: {context['position']}
        Experience Level: {context['experience_level']}
        Interview Type: {context['interview_type']}
        Current Difficulty: {context['current_difficulty']}
        Next Difficulty: {context['next_difficulty']}
        Interview Progress: {context['interview_progress']:.1%}
        Questions Asked: {context['question_count']}
        Average Score: {context['average_score']:.1f}/10
        Resume Skills: {', '.join(context['resume_skills'][:5])}
        Recent Themes: {', '.join(context['recent_themes'])}
        
        Requirements:
        1. Question should be appropriate for {context['next_difficulty']} difficulty
        2. Consider the candidate's skills: {', '.join(context['resume_skills'][:3])}
        3. Build on recent themes: {', '.join(context['recent_themes'])}
        4. Focus on {context['interview_type']} aspects
        5. Question should take 3-5 minutes to answer
        
        Return JSON with structure:
        {{
            "question": "Your question here",
            "category": "technical|behavioral|situational",
            "difficulty": "easy|medium|hard",
            "expected_duration": 300,
            "context": {{
                "focus_area": "specific skill or topic",
                "reasoning": "why this question"
            }},
            "follow_up_hints": [
                "Follow-up question 1",
                "Follow-up question 2"
            ]
        }}
        
        Return only valid JSON.
        """
    
    def _parse_question_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse AI response into question data.
        
        Args:
            response_text: AI response text
            
        Returns:
            Dict[str, Any]: Parsed question data
        """
        try:
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                logger.warning("Could not extract JSON from question response")
                return {
                    "question": "Tell me about your experience with the technologies mentioned in your resume.",
                    "category": "technical",
                    "difficulty": "medium",
                    "expected_duration": 300
                }
        except Exception as e:
            logger.error(f"Failed to parse question response: {e}")
            return {
                "question": "Tell me about your experience with the technologies mentioned in your resume.",
                "category": "technical",
                "difficulty": "medium",
                "expected_duration": 300
            }
    
    async def evaluate_response(
        self,
        question: Question,
        response: str,
        candidate_profile: CandidateProfile,
        resume_analysis: ResumeAnalysis,
        position: str
    ) -> ResponseEvaluation:
        """
        Evaluate a candidate response comprehensively.
        
        Args:
            question: The question that was asked
            response: Candidate's response
            candidate_profile: Candidate profile
            resume_analysis: Resume analysis
            position: Job position
            
        Returns:
            ResponseEvaluation: Comprehensive response evaluation
        """
        try:
            # Create evaluation context
            context = {
                "question": question.text,
                "question_category": question.category,
                "question_difficulty": question.difficulty.value,
                "response": response,
                "position": position,
                "experience_level": candidate_profile.experience_level.value,
                "resume_skills": resume_analysis.extracted_skills if resume_analysis else [],
                "resume_experience": resume_analysis.experience_years if resume_analysis else 0.0
            }
            
            # Generate evaluation using AI
            evaluation_prompt = self._create_evaluation_prompt(context)
            evaluation_response = await self.agent.run(evaluation_prompt)
            
            # Parse evaluation from AI response
            evaluation_data = self._parse_evaluation_response(evaluation_response.content)
            
            # Create ResponseEvaluation object
            evaluation = ResponseEvaluation(
                question_id=question.id,
                response_text=response,
                technical_accuracy=evaluation_data.get("technical_accuracy", 7.0),
                communication_clarity=evaluation_data.get("communication_clarity", 7.0),
                problem_solving_approach=evaluation_data.get("problem_solving_approach", 7.0),
                experience_relevance=evaluation_data.get("experience_relevance", 7.0),
                overall_score=evaluation_data.get("overall_score", 7.0),
                strengths=evaluation_data.get("strengths", []),
                areas_for_improvement=evaluation_data.get("areas_for_improvement", []),
                suggestions=evaluation_data.get("suggestions", []),
                suggested_difficulty=DifficultyLevel(evaluation_data.get("suggested_difficulty", "medium")),
                follow_up_questions=evaluation_data.get("follow_up_questions", []),
                skill_gaps=evaluation_data.get("skill_gaps", [])
            )
            
            logger.info(f"Evaluated response with score: {evaluation.overall_score}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Failed to evaluate response: {e}")
            # Return basic evaluation
            return ResponseEvaluation(
                question_id=question.id,
                response_text=response,
                technical_accuracy=7.0,
                communication_clarity=7.0,
                problem_solving_approach=7.0,
                experience_relevance=7.0,
                overall_score=7.0,
                suggested_difficulty=DifficultyLevel.MEDIUM
            )
    
    def _create_evaluation_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create prompt for response evaluation.
        
        Args:
            context: Evaluation context
            
        Returns:
            str: Evaluation prompt
        """
        return f"""
        Evaluate this interview response comprehensively:
        
        Question: {context['question']}
        Category: {context['question_category']}
        Difficulty: {context['question_difficulty']}
        Position: {context['position']}
        Experience Level: {context['experience_level']}
        
        Response: {context['response']}
        
        Resume Skills: {', '.join(context['resume_skills'][:5])}
        Resume Experience: {context['resume_experience']} years
        
        Evaluate on a scale of 1-10 for each criterion:
        1. Technical accuracy (for technical questions)
        2. Communication clarity
        3. Problem-solving approach
        4. Experience relevance
        
        Return JSON with structure:
        {{
            "technical_accuracy": 8.5,
            "communication_clarity": 7.0,
            "problem_solving_approach": 9.0,
            "experience_relevance": 8.0,
            "overall_score": 8.1,
            "strengths": ["Clear explanation", "Good examples"],
            "areas_for_improvement": ["Could provide more detail"],
            "suggestions": ["Consider mentioning specific technologies"],
            "suggested_difficulty": "medium",
            "follow_up_questions": [
                "Can you elaborate on the scalability aspect?",
                "What challenges did you face?"
            ],
            "skill_gaps": ["Advanced system design"]
        }}
        
        Return only valid JSON.
        """
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse AI response into evaluation data.
        
        Args:
            response_text: AI response text
            
        Returns:
            Dict[str, Any]: Parsed evaluation data
        """
        try:
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                logger.warning("Could not extract JSON from evaluation response")
                return {
                    "technical_accuracy": 7.0,
                    "communication_clarity": 7.0,
                    "problem_solving_approach": 7.0,
                    "experience_relevance": 7.0,
                    "overall_score": 7.0,
                    "suggested_difficulty": "medium"
                }
        except Exception as e:
            logger.error(f"Failed to parse evaluation response: {e}")
            return {
                "technical_accuracy": 7.0,
                "communication_clarity": 7.0,
                "problem_solving_approach": 7.0,
                "experience_relevance": 7.0,
                "overall_score": 7.0,
                "suggested_difficulty": "medium"
            }


# Global adaptive interview agent instance
adaptive_interview_agent = AdaptiveInterviewAgent() 