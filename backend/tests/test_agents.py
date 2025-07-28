"""
Tests for Agno agents.
"""

import pytest
from unittest.mock import AsyncMock, patch

from intervuebot.agents.interview_agent import InterviewAgent
from intervuebot.agents.evaluation_agent import EvaluationAgent
from intervuebot.agents.question_generator_agent import QuestionGeneratorAgent


@pytest.fixture
def interview_agent():
    """Create interview agent instance for testing."""
    return InterviewAgent()


@pytest.fixture
def evaluation_agent():
    """Create evaluation agent instance for testing."""
    return EvaluationAgent()


@pytest.fixture
def question_generator_agent():
    """Create question generator agent instance for testing."""
    return QuestionGeneratorAgent()


def test_interview_agent_initialization():
    """Test interview agent initialization."""
    agent = InterviewAgent()
    assert agent.name == "IntervueBot"
    assert agent.role == "AI Interview Conductor"
    assert agent.goal is not None


def test_evaluation_agent_initialization():
    """Test evaluation agent initialization."""
    agent = EvaluationAgent()
    assert agent.name == "EvaluationBot"
    assert agent.role == "Interview Response Evaluator"
    assert agent.goal is not None


def test_question_generator_agent_initialization():
    """Test question generator agent initialization."""
    agent = QuestionGeneratorAgent()
    assert agent.name == "QuestionBot"
    assert agent.role == "Dynamic Interview Question Generator"
    assert agent.goal is not None


@pytest.mark.asyncio
async def test_interview_agent_generate_question():
    """Test interview agent question generation."""
    with patch('intervuebot.agents.interview_agent.GoogleGenerativeAI') as mock_llm:
        # Mock the LLM response
        mock_llm_instance = AsyncMock()
        mock_llm_instance.run.return_value = "What is your experience with Python?"
        mock_llm.return_value = mock_llm_instance
        
        agent = InterviewAgent()
        agent.llm = mock_llm_instance
        
        question = agent.generate_question_tool(
            position="Software Engineer",
            category="technical",
            difficulty="medium"
        )
        
        assert "Python" in question or "experience" in question


@pytest.mark.asyncio
async def test_evaluation_agent_score_response():
    """Test evaluation agent response scoring."""
    with patch('intervuebot.agents.evaluation_agent.GoogleGenerativeAI') as mock_llm:
        # Mock the LLM response
        mock_llm_instance = AsyncMock()
        mock_llm_instance.run.return_value = "Score: 8/10. Good technical understanding."
        mock_llm.return_value = mock_llm_instance
        
        agent = EvaluationAgent()
        agent.llm = mock_llm_instance
        
        evaluation = agent.score_response_tool(
            question="What is Python?",
            response="Python is a programming language",
            position="Software Engineer",
            category="technical"
        )
        
        assert "score" in evaluation
        assert "feedback" in evaluation


@pytest.mark.asyncio
async def test_question_generator_generate_sequence():
    """Test question generator sequence generation."""
    with patch('intervuebot.agents.question_generator_agent.GoogleGenerativeAI') as mock_llm:
        # Mock the LLM response
        mock_llm_instance = AsyncMock()
        mock_llm_instance.run.return_value = "Technical question for Software Engineer"
        mock_llm.return_value = mock_llm_instance
        
        agent = QuestionGeneratorAgent()
        agent.llm = mock_llm_instance
        
        questions = await agent.generate_question_sequence(
            position="Software Engineer",
            interview_type="technical",
            experience_level="mid-level",
            required_skills=["Python", "JavaScript"]
        )
        
        assert isinstance(questions, list)
        assert len(questions) > 0


@pytest.mark.asyncio
async def test_interview_agent_conduct_session():
    """Test interview agent conducting a complete session."""
    with patch('intervuebot.agents.interview_agent.GoogleGenerativeAI') as mock_llm:
        # Mock the LLM response
        mock_llm_instance = AsyncMock()
        mock_llm_instance.run.return_value = "Test question"
        mock_llm.return_value = mock_llm_instance
        
        agent = InterviewAgent()
        agent.llm = mock_llm_instance
        
        from intervuebot.schemas.interview import CandidateProfile
        
        candidate = CandidateProfile(
            name="Test Candidate",
            email="test@example.com",
            position="Software Engineer",
            experience_years=3,
            skills=["Python", "JavaScript"]
        )
        
        session = await agent.conduct_interview_session(
            candidate=candidate,
            position="Software Engineer",
            interview_type="technical",
            max_questions=3
        )
        
        assert "candidate" in session
        assert "questions" in session
        assert "evaluations" in session
        assert "final_assessment" in session


@pytest.mark.asyncio
async def test_evaluation_agent_complete_evaluation():
    """Test evaluation agent complete response evaluation."""
    with patch('intervuebot.agents.evaluation_agent.GoogleGenerativeAI') as mock_llm:
        # Mock the LLM response
        mock_llm_instance = AsyncMock()
        mock_llm_instance.run.return_value = "Comprehensive evaluation"
        mock_llm.return_value = mock_llm_instance
        
        agent = EvaluationAgent()
        agent.llm = mock_llm_instance
        
        evaluation = await agent.evaluate_complete_response(
            question="What is Python?",
            response="Python is a programming language",
            position="Software Engineer",
            category="technical",
            required_skills=["Python", "JavaScript"]
        )
        
        assert "question" in evaluation
        assert "response" in evaluation
        assert "score" in evaluation
        assert "feedback" in evaluation 