# Environment Setup Guide

## Quick Setup

1. **Copy the environment template:**
   ```bash
   cp env.example .env
   ```

2. **Configure your API keys:**
   ```bash
   # Edit .env file and add your API keys
   GOOGLE_API_KEY=your-actual-google-api-key
   ```

3. **Start the application:**
   ```bash
   python -m src.main
   ```

## Required Configuration

### **Essential Settings (Required)**

#### **Google AI API Key**
```bash
GOOGLE_API_KEY=your-google-api-key-here
```
- Get your API key from: https://makersuite.google.com/app/apikey
- Required for AI agent functionality

#### **Redis Configuration**
```bash
REDIS_URL=redis://localhost:6379
```
- Default Redis connection (localhost:6379)
- Make sure Redis is running locally

### **Optional Settings**

#### **Database Configuration**
```bash
POSTGRES_SERVER=localhost
POSTGRES_USER=intervuebot
POSTGRES_PASSWORD=intervuebot
POSTGRES_DB=intervuebot
```
- Only needed if you plan to use PostgreSQL
- Currently using Redis for session storage

#### **Alternative LLM Providers**
```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key
```

#### **Interview Settings**
```bash
# Duration settings
DEFAULT_INTERVIEW_DURATION_MINUTES=60
MAX_INTERVIEW_DURATION_MINUTES=120

# Phase durations (in minutes)
INTRODUCTION_PHASE_DURATION=5
WARM_UP_PHASE_DURATION=8
TECHNICAL_BASIC_PHASE_DURATION=15
TECHNICAL_ADVANCED_PHASE_DURATION=20
BEHAVIORAL_PHASE_DURATION=15
PROBLEM_SOLVING_PHASE_DURATION=12
SITUATIONAL_PHASE_DURATION=10
CULTURAL_FIT_PHASE_DURATION=8
CLOSING_PHASE_DURATION=5
```

## Development vs Production

### **Development Settings**
```bash
DEBUG=True
ENVIRONMENT=development
ENABLE_AGENT_INITIALIZATION_TESTS=true
ENABLE_DETAILED_LOGGING=true
```

### **Production Settings**
```bash
DEBUG=False
ENVIRONMENT=production
ENABLE_AGENT_INITIALIZATION_TESTS=false
ENABLE_DETAILED_LOGGING=false
SECRET_KEY=your-secure-production-secret-key
```

## Environment Variables Reference

### **Application Settings**
- `DEBUG`: Enable debug mode (True/False)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `SECRET_KEY`: Application secret key

### **LLM Configuration**
- `DEFAULT_LLM_PROVIDER`: Primary LLM provider (google/openai/anthropic)
- `DEFAULT_LLM_MODEL`: LLM model to use
- `GOOGLE_API_KEY`: Google AI API key
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key

### **Interview Settings**
- `MAX_INTERVIEW_DURATION_MINUTES`: Maximum interview duration
- `MAX_QUESTIONS_PER_INTERVIEW`: Maximum questions per interview
- `QUESTION_TIMEOUT_SECONDS`: Timeout for individual questions

### **Cache Settings**
- `ENABLE_LLM_CACHE`: Enable LLM response caching
- `LLM_CACHE_TTL_HOURS`: Cache TTL for LLM responses
- `ENABLE_SESSION_CACHE`: Enable session caching
- `SESSION_CACHE_TTL_HOURS`: Cache TTL for sessions

### **Rate Limiting**
- `ENABLE_RATE_LIMITING`: Enable API rate limiting
- `RATE_LIMIT_REQUESTS_PER_MINUTE`: Requests per minute limit
- `RATE_LIMIT_REQUESTS_PER_HOUR`: Requests per hour limit

## Troubleshooting

### **Common Issues**

#### **1. Redis Connection Error**
```
Failed to connect to Redis: Timeout connecting to server
```
**Solution:** Make sure Redis is running:
```bash
# Start Redis (Windows)
redis-server

# Or check if Redis is running
redis-cli ping
```

#### **2. Gemini API Rate Limit**
```
429 RESOURCE_EXHAUSTED
```
**Solution:** This is normal for free tier. The application will still work, but agent initialization tests may fail.

#### **3. Missing Dependencies**
```
ModuleNotFoundError: No module named 'intervuebot'
```
**Solution:** Install the package in editable mode:
```bash
pip install -e .
```

### **Testing Configuration**

1. **Test Redis connection:**
   ```bash
   python -c "import redis; r = redis.Redis(host='localhost', port=6379); print(r.ping())"
   ```

2. **Test API endpoints:**
   ```bash
   # Health check
   curl http://localhost:8000/api/v1/health/
   
   # Root endpoint
   curl http://localhost:8000/
   ```

3. **Test Swagger documentation:**
   - Visit: http://localhost:8000/docs
   - Visit: http://localhost:8000/redoc

## Security Notes

### **Production Security**
- Change `SECRET_KEY` to a secure random string
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS in production
- Secure your API keys

### **API Key Security**
- Never commit API keys to version control
- Use environment variables for all secrets
- Rotate API keys regularly
- Monitor API usage for unexpected charges

## Next Steps

1. **Set up your environment:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

2. **Start the application:**
   ```bash
   python -m src.main
   ```

3. **Test the API:**
   - Visit: http://localhost:8000/
   - Visit: http://localhost:8000/docs

4. **Start developing:**
   - Add new endpoints
   - Customize interview sequences
   - Integrate with your frontend 