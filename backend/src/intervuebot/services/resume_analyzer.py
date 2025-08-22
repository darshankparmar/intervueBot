import io
import re
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

import pdfplumber

from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat

from intervuebot.schemas.interview import ResumeAnalysis
from intervuebot.core.config import settings

logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    def __init__(self):
        """Initialize ResumeAnalyzer with dynamic LLM selection."""
        provider = settings.DEFAULT_LLM_PROVIDER.lower()
        model_id = settings.DEFAULT_LLM_MODEL
        if provider == "openai":
            model = OpenAIChat(id=model_id, api_key=settings.OPENAI_API_KEY)
        else:
            model = Gemini(id=model_id, api_key=settings.GOOGLE_API_KEY)
        self.agent = Agent(
            model=model,
            name="ResumeAnalyzer",
            role="Resume Analysis Expert",
            goal="Extract structured information from resumes for interview preparation",
            instructions=[
                "Analyze resumes and extract skills, experience, education, projects, and more.",
                "Avoid returning null values. Use empty lists or empty strings instead.",
                "Infer values from context if possible, instead of leaving them blank.",
                "Always return valid JSON in the required format."
            ],
            markdown=True,
        )

    async def analyze_resume(self, resume_files: List[Dict[str, Any]], position: str) -> ResumeAnalysis:
        try:
            logger.info(f"Analyzing {len(resume_files)} resumes for position: {position}")

            # Extract text from resumes
            resume_text = await self._extract_text_from_files(resume_files)

            # Build prompt
            analysis_prompt = self._create_analysis_prompt(resume_text, position)

            # Run LLM
            analysis_response = self.agent.run(analysis_prompt)

            # Parse response
            analysis_data = self._parse_analysis_response(analysis_response.content)

            # Build ResumeAnalysis object
            return ResumeAnalysis(
                extracted_skills=analysis_data.get("skills", []),
                experience_years=analysis_data.get("experience_years", 0.0) or 0.0,
                education=analysis_data.get("education", "Not specified") or "Not specified",
                current_company=analysis_data.get("current_company", "Not specified") or "Not specified",
                previous_companies=analysis_data.get("previous_companies", []),
                projects=analysis_data.get("projects", []),
                certifications=analysis_data.get("certifications", []),
                languages=analysis_data.get("languages", []),
                technologies=analysis_data.get("technologies", []),
                confidence_score=analysis_data.get("confidence_score", 0.7),
            )

        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return ResumeAnalysis(
                extracted_skills=[],
                experience_years=0.0,
                confidence_score=0.1
            )

    async def _extract_text_from_files(self, resume_files: List[Dict[str, Any]]) -> str:
        """Extract text from resume files (supports PDF & plain text)."""
        combined_text = ""
        for file_data in resume_files:
            combined_text += f"\n--- {file_data['name']} ---\n"
            try:
                if file_data['name'].lower().endswith(".pdf"):
                    with pdfplumber.open(io.BytesIO(file_data['content'])) as pdf:
                        for page in pdf.pages:
                            combined_text += page.extract_text() or ""
                else:
                    if isinstance(file_data['content'], bytes):
                        combined_text += file_data['content'].decode("utf-8", errors="ignore")
                    else:
                        combined_text += str(file_data['content'])
            except Exception as e:
                logger.warning(f"Failed to process {file_data['name']}: {e}")
        return combined_text

    def _create_analysis_prompt(self, resume_text: str, position: str) -> str:
        """Prompt template for LLM analysis."""
        return f"""
        Analyze this resume for a {position} role.
        
        Resume Content:
        {resume_text}

        Return valid JSON in this schema:
        {{
            "skills": ["skill1", "skill2"],
            "experience_years": 3.5,
            "education": "BS Computer Science",
            "current_company": "Current Company",
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
            "confidence_score": 0.85,
            "email": "optional email",
            "linkedin": "optional linkedin url",
            "github": "optional github url"
        }}

        Rules:
        - Never return null values. Use empty strings/lists instead.
        - Infer data from context if possible.
        - Return only the JSON object (no markdown fences).
        """

    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Clean and parse AI JSON response."""
        try:
            cleaned = response_text.strip()

            # Remove markdown fences
            cleaned = re.sub(r"^```(json)?", "", cleaned, flags=re.MULTILINE).strip()
            cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

            # Extract JSON
            json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            logger.warning("No JSON found in response")
            return {}
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return {}


# Global instance
resume_analyzer = ResumeAnalyzer()
