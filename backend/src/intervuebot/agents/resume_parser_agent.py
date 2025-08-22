import fitz  # PyMuPDF
from agno.agent import Agent
from agno.models.google import Gemini
import json
import re
from ..core.config import settings

class ResumeParserAgent(Agent):
    def __init__(self):
        self.agent = Agent(
            model=Gemini("gemini-2.0-flash-exp", api_key=settings.GOOGLE_API_KEY),
            name="ResumeParserAgent",
            role="Resume Parser Agent",
            goal="Parse resumes and extract relevant information",
            instructions=[
                "You are an expert resume parser with deep knowledge of various industries and job roles.",
                "You excel at extracting relevant information from resumes and extracting it in a structured format.",
                "You provide structured analysis with confidence scores.",
                "You focus on information relevant to technical interviews and job positions."
            ],
            markdown=True,
        )
    

    def extract_data_from_pdf(self, pdf_text, json_template):   
        print("inside json", json_template)
        prompt = f"""
        You are an AI assistant. 
        Here is the PDF content:
        ---
        {pdf_text}
        ---

        Extract the following fields from the PDF and return ONLY valid JSON
        without markdown, backticks, or any extra formatting.
        JSON structure to follow:
        {json.dumps(json_template, indent=2)}
        Output ONLY JSON. Do not include any text outside the JSON.
        """
        
        response = self.agent.run(prompt)
        response_text = str(response.content).strip()

        # Remove markdown code block markers if present
        if response_text.startswith("```"):
            response_text = re.sub(r"^```[a-zA-Z]*\n?", "", response_text)  # Remove ```json or ```
            response_text = re.sub(r"\n?```$", "", response_text)  # Remove ending ```

        print("response_text : ", response_text)
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON structure in AI output: {e}")
        else:
            raise ValueError("No JSON found in AI output")
