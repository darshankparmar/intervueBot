# 🤖 IntervueBot Backend

AI Interview Taker Agent using Agno Framework and FastAPI

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- Google AI API key (for Gemini models)

### Environment Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start the application**
   ```bash
   python -m src.main
   ```

Visit `http://localhost:8000/docs` for API documentation.

## 📁 Project Structure

```
backend/
├── src/
│   ├── intervuebot/
│   │   ├── api/                    # API routes and endpoints
│   │   │   └── v1/
│   │   │       ├── endpoints/      # Individual endpoint modules
│   │   │       └── router.py       # Main API router
│   │   ├── core/                   # Core configuration and utilities
│   │   │   ├── config.py          # Application settings
│   │   │   └── events.py          # Startup/shutdown handlers
│   │   ├── schemas/                # Pydantic data models
│   │   │   └── interview.py       # Interview-related schemas
│   │   ├── agents/                 # Agno AI agents (TODO)
│   │   ├── models/                 # Database models (TODO)
│   │   ├── services/               # Business logic (TODO)
│   │   └── utils/                  # Utility functions (TODO)
│   └── main.py                     # Application entry point
├── tests/                          # Test suite (TODO)
├── pyproject.toml                  # Project configuration
├── env.example                     # Environment variables template
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

- `DEBUG`: Enable debug mode
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `SECRET_KEY`: Application secret key
- `GOOGLE_API_KEY`: Google AI API key (for Gemini)
- `POSTGRES_*`: Database configuration
- `REDIS_URL`: Redis connection URL

## 📊 API Endpoints

### Health Check
- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/status` - Detailed status
- `GET /api/v1/health/redis` - Redis health check

### Agent Testing
- `POST /api/v1/interviews/start` - Start interview with Agno agents
- `GET /api/v1/interviews/{session_id}/question` - Get next question
- `POST /api/v1/interviews/{session_id}/respond` - Submit and evaluate response
- `GET /api/v1/interviews/{session_id}/report` - Get final evaluation report

### Interviews
- `POST /api/v1/interviews/start` - Start new interview
- `GET /api/v1/interviews/{session_id}/question` - Get next question
- `POST /api/v1/interviews/{session_id}/respond` - Submit response
- `POST /api/v1/interviews/{session_id}/end` - End interview
- `GET /api/v1/interviews/{session_id}/report` - Get evaluation report

## 🧪 Development

### Code Quality

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/

# Run tests
pytest
```

### Running in Development

```bash
# With auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main module
python -m src.main
```

## 🚀 Production Deployment

### Using Docker

```bash
# Build image
docker build -t intervuebot-backend .

# Run container
docker run -p 8000:8000 intervuebot-backend
```

### Manual Deployment

```bash
# Install production dependencies
pip install -e .[dev]

# Run with gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🔮 Next Steps

1. **Database Integration**
   - Set up SQLAlchemy models
   - Configure Alembic migrations
   - Implement database services

2. **AI Agents** ✅
   - ✅ Agno interview agent implemented
   - ✅ Evaluation agent implemented
   - ✅ Question generator agent implemented

3. **Business Logic**
   - Interview session management
   - Response evaluation
   - Report generation

4. **Testing**
   - Unit tests for all modules
   - Integration tests
   - API endpoint tests

## 📝 License

MIT License - see LICENSE file for details. 