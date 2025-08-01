# IntervueBot API Examples

## Simplified Interview API

The interview API now only requires essential information to start an interview.

### 1. Start Interview

**Endpoint:** `POST /api/v1/interviews/start`

**Request Body:**
```json
{
  "candidate": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "position": "Software Engineer",
    "experience_level": "mid-level",
    "interview_type": "technical",
    "files": [
      {
        "filename": "john_doe_resume.pdf",
        "file_url": "https://example.com/uploads/john_doe_resume.pdf",
        "file_type": "resume"
      },
      {
        "filename": "john_doe_cover_letter.pdf",
        "file_url": "https://example.com/uploads/john_doe_cover_letter.pdf",
        "file_type": "cover_letter"
      }
    ]
  },
  "duration_minutes": 60
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidate": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "position": "Software Engineer",
    "experience_level": "mid-level",
    "interview_type": "technical",
    "files": [...],
    "resume_analysis": {
      "extracted_skills": ["Python", "JavaScript", "React", "Node.js"],
      "experience_years": 3.5,
      "education": "BS Computer Science",
      "current_company": "Tech Corp",
      "confidence_score": 0.85
    }
  },
  "position": "Software Engineer",
  "status": "in_progress",
  "started_at": "2024-01-15T10:30:00Z",
  "current_question_index": 0,
  "total_questions_asked": 0,
  "average_score": 0.0
}
```

### 2. Get Next Question

**Endpoint:** `GET /api/v1/interviews/{session_id}/next-question`

**Response:**
```json
{
  "question": {
    "id": "q_1",
    "text": "Can you tell me about your experience with Python and how you would approach optimizing a slow database query?",
    "category": "technical",
    "difficulty": "medium",
    "expected_duration": 300,
    "context": {
      "focus_area": "Database optimization",
      "reasoning": "Based on resume showing Python experience"
    },
    "follow_up_hints": [
      "What specific techniques would you use?",
      "How would you measure the improvement?"
    ]
  },
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question_number": 1,
  "time_limit": 300,
  "context": {
    "difficulty": "medium",
    "category": "technical",
    "interview_progress": 0.1,
    "follow_up_hints": [...]
  }
}
```

### 3. Submit Response

**Endpoint:** `POST /api/v1/interviews/{session_id}/respond`

**Request Body:**
```json
{
  "question_id": "q_1",
  "answer": "I would first analyze the query execution plan to identify bottlenecks. For Python applications, I'd use tools like cProfile to profile the code and identify slow operations. For database optimization, I'd look at indexes, query structure, and consider caching strategies like Redis for frequently accessed data.",
  "time_taken": 180
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Response submitted and evaluated successfully",
  "evaluation": {
    "overall_score": 8.5,
    "technical_accuracy": 9.0,
    "communication_clarity": 8.0,
    "problem_solving_approach": 8.5,
    "experience_relevance": 8.5,
    "strengths": [
      "Good understanding of profiling tools",
      "Comprehensive approach to optimization"
    ],
    "areas_for_improvement": [
      "Could provide more specific examples"
    ],
    "suggestions": [
      "Consider mentioning specific database systems",
      "Add metrics for measuring success"
    ],
    "suggested_difficulty": "hard",
    "follow_up_questions": [
      "How would you handle a distributed system optimization?",
      "What monitoring tools would you use?"
    ],
    "skill_gaps": []
  },
  "next_steps": "Continue with next question or finalize interview"
}
```

### 4. Finalize Interview

**Endpoint:** `POST /api/v1/interviews/{session_id}/finalize`

**Response:**
```json
{
  "status": "success",
  "message": "Interview completed successfully",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "report_summary": {
    "overall_score": 8.2,
    "hiring_recommendation": "hire",
    "confidence_level": 0.85,
    "total_questions": 8,
    "total_responses": 8,
    "average_response_time": 145.5
  }
}
```

### 5. Get Final Report

**Endpoint:** `GET /api/v1/interviews/{session_id}/report`

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidate": {...},
  "position": "Software Engineer",
  "overall_score": 8.2,
  "technical_score": 8.5,
  "behavioral_score": 7.8,
  "communication_score": 8.0,
  "problem_solving_score": 8.5,
  "cultural_fit_score": 8.0,
  "strengths": [
    "Strong technical knowledge",
    "Good problem-solving approach",
    "Clear communication"
  ],
  "areas_for_improvement": [
    "Could provide more specific examples",
    "Consider mentioning industry best practices"
  ],
  "skill_gaps": [],
  "recommendations": ["Recommendation: HIRE"],
  "total_questions": 8,
  "total_responses": 8,
  "average_response_time": 145.5,
  "difficulty_progression": [
    {"question": 1, "difficulty": "medium", "score": 8.5},
    {"question": 2, "difficulty": "hard", "score": 8.0}
  ],
  "hiring_recommendation": "hire",
  "confidence_level": 0.85,
  "detailed_feedback": "Comprehensive Interview Report...",
  "interview_duration": 45.5
}
```

## Experience Levels

- **junior**: 0-2 years experience
- **mid-level**: 2-5 years experience  
- **senior**: 5+ years experience
- **lead**: 7+ years with leadership experience

## Interview Types

- **technical**: Focus on technical skills and problem-solving
- **behavioral**: Focus on past experiences and soft skills
- **mixed**: Combination of technical and behavioral questions
- **leadership**: Focus on leadership and management skills

## File Types

- **resume**: Main resume/CV file
- **cv**: Alternative CV format
- **cover_letter**: Cover letter or motivation letter 