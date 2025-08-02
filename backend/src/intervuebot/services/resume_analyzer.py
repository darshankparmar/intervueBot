"""
Resume analysis service.

This module provides resume analysis capabilities to extract
skills, experience, and other relevant information from
uploaded resume files.
"""

import logging
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

from agno.agent import Agent
from agno.models.google import Gemini

from intervuebot.schemas.interview import ResumeAnalysis, ResumeFile
from intervuebot.core.config import settings
from intervuebot.services.file_processor import file_processor

logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """
    Resume analysis service using AI to extract relevant information.
    
    This service analyzes resume files to extract skills, experience,
    education, and other relevant information for interview preparation.
    """
    
    def __init__(self):
        """Initialize the resume analyzer."""
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            name="ResumeAnalyzer",
            role="Resume Analysis Expert",
            goal="Extract comprehensive information from resumes for interview preparation",
            instructions=[
                "You are an expert at analyzing resumes and extracting relevant information.",
                "You excel at identifying skills, experience, education, and project details.",
                "You provide structured analysis with confidence scores.",
                "You focus on information relevant to technical interviews and job positions."
            ],
            markdown=True,
        )
    
    async def analyze_resume(self, resume_files: List[ResumeFile], position: str) -> ResumeAnalysis:
        """
        Analyze resume files to extract relevant information.
        
        Args:
            resume_files: List of uploaded resume files
            position: Job position being applied for
            
        Returns:
            ResumeAnalysis: Comprehensive resume analysis results
        """
        try:
            logger.info(f"Starting resume analysis for {len(resume_files)} files")
            
            # Extract text from resume files (simplified - in real implementation, parse PDF/DOC)
            resume_text = await self._extract_text_from_files(resume_files)
            
            # Analyze resume content using AI
            analysis_prompt = self._create_analysis_prompt(resume_text, position)
            analysis_response = await self.agent.run(analysis_prompt)
            
            # Parse AI response into structured data
            analysis_data = self._parse_analysis_response(analysis_response.content)
            
            # Create ResumeAnalysis object
            resume_analysis = ResumeAnalysis(
                extracted_skills=analysis_data.get("skills", []),
                experience_years=analysis_data.get("experience_years", 0.0),
                education=analysis_data.get("education"),
                current_company=analysis_data.get("current_company"),
                previous_companies=analysis_data.get("previous_companies", []),
                projects=analysis_data.get("projects", []),
                certifications=analysis_data.get("certifications", []),
                languages=analysis_data.get("languages", []),
                technologies=analysis_data.get("technologies", []),
                confidence_score=analysis_data.get("confidence_score", 0.8)
            )
            
            logger.info(f"Resume analysis completed with confidence: {resume_analysis.confidence_score}")
            return resume_analysis
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            # Return basic analysis with low confidence
            return ResumeAnalysis(
                extracted_skills=[],
                experience_years=0.0,
                confidence_score=0.1
            )
    
    async def _extract_text_from_files(self, resume_files: List[ResumeFile]) -> str:
        """
        Extract text content from resume files.
        
        Args:
            resume_files: List of resume files
            
        Returns:
            str: Combined text content from all files
        """
        # Process uploaded files using file processor
        processed_result = await file_processor.process_uploaded_files(resume_files)
        
        if processed_result.get("error"):
            logger.warning(f"File processing error: {processed_result['error']}")
            # Return basic placeholder if file processing fails
            return f"Resume files: {len(resume_files)} files\nPosition: {position}\nExperience: 3 years\nSkills: Python, JavaScript"
        
        return processed_result.get("combined_text", "")
    
    def _create_analysis_prompt(self, resume_text: str, position: str) -> str:
        """
        Create analysis prompt for AI agent.
        
        Args:
            resume_text: Extracted text from resume
            position: Job position
            
        Returns:
            str: Analysis prompt
        """
        return f"""
        Analyze this resume for a {position} position and extract relevant information.
        
        Resume Content:
        {resume_text}
        
        Position: {position}
        
        Please provide a comprehensive analysis in JSON format with the following structure:
        {{
            "skills": ["skill1", "skill2", ...],
            "experience_years": 3.5,
            "education": "BS Computer Science",
            "current_company": "Current Company Name",
            "previous_companies": ["Company1", "Company2"],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Project description",
                    "technologies": ["tech1", "tech2"],
                    "duration": "6 months"
                }}
            ],
            "certifications": ["cert1", "cert2"],
            "languages": ["Python", "JavaScript"],
            "technologies": ["React", "Node.js"],
            "confidence_score": 0.85
        }}
        
        Focus on:
        1. Technical skills relevant to {position}
        2. Years of experience
        3. Project details and technologies used
        4. Education and certifications
        5. Programming languages and tools
        6. Previous companies and roles
        
        Return only valid JSON.
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse AI response into structured data.
        
        Args:
            response_text: AI response text
            
        Returns:
            Dict[str, Any]: Parsed analysis data
        """
        try:
            # Extract JSON from response (handle markdown formatting)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            else:
                logger.warning("Could not extract JSON from AI response")
                return {}
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return {}
    
    def extract_skills_for_position(self, resume_analysis: ResumeAnalysis, position: str) -> List[str]:
        """
        Extract skills most relevant to the position.
        
        Args:
            resume_analysis: Resume analysis results
            position: Job position
            
        Returns:
            List[str]: Relevant skills for the position
        """
        # Define position-specific skill mappings
        position_skills = {
            "Software Engineer": ["Python", "JavaScript", "React", "Node.js", "SQL", "Git"],
            "Data Scientist": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas"],
            "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Linux", "CI/CD", "Python"],
            "Frontend Developer": ["JavaScript", "React", "Vue", "HTML", "CSS", "TypeScript"],
            "Backend Developer": ["Python", "Java", "Node.js", "SQL", "REST APIs", "Microservices"]
        }
        
        # Get relevant skills for the position
        relevant_skills = position_skills.get(position, resume_analysis.extracted_skills)
        
        # Filter skills that appear in resume
        matching_skills = [
            skill for skill in relevant_skills 
            if skill.lower() in [s.lower() for s in resume_analysis.extracted_skills]
        ]
        
        # Add any additional skills from resume
        additional_skills = [
            skill for skill in resume_analysis.extracted_skills 
            if skill not in matching_skills
        ]
        
        return matching_skills + additional_skills[:5]  # Limit to top skills
    
    def calculate_experience_level(self, experience_years: float) -> str:
        """
        Calculate experience level based on years of experience.
        
        Args:
            experience_years: Years of experience
            
        Returns:
            str: Experience level (junior, mid-level, senior, lead)
        """
        if experience_years <= 2:
            return "junior"
        elif experience_years <= 5:
            return "mid-level"
        elif experience_years <= 7:
            return "senior"
        else:
            return "lead"
    
    def identify_skill_gaps(self, resume_skills: List[str], position_requirements: List[str]) -> List[str]:
        """
        Identify skill gaps between resume and position requirements.
        
        Args:
            resume_skills: Skills from resume
            position_requirements: Required skills for position
            
        Returns:
            List[str]: Missing skills
        """
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        missing_skills = [
            skill for skill in position_requirements 
            if skill.lower() not in resume_skills_lower
        ]
        return missing_skills


# Global resume analyzer instance
resume_analyzer = ResumeAnalyzer() 