mypy src/

# IntervueBot Backend

AI-powered interview system using FastAPI.

## Quick Start

1. **Clone & Setup**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   pip install -e .
   cp env.example .env
   # Edit .env as needed
   ```

2. **Run the Server**
   ```bash
   python -m src.main
   # or for auto-reload (dev)
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **API Docs:**  
   Visit [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Project Structure

```
backend/
├── src/
│   ├── intervuebot/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Config, events, redis
│   │   ├── schemas/     # Pydantic models
│   │   ├── agents/      # AI agents
│   │   ├── services/    # Business logic
│   └── main.py          # App entry point
├── tests/               # Unit tests
├── pyproject.toml
├── env.example
└── README.md
```

---

## Configuration

- All settings are in `.env`
- Key variables: `REDIS_URL`, `GOOGLE_API_KEY`, `SECRET_KEY`, `PORT`, etc.

---

## Main API Endpoints

- `POST   /api/v1/interviews/start` — Start interview
- `GET    /api/v1/interviews/{session_id}/next-question` — Get next question
- `POST   /api/v1/interviews/{session_id}/respond` — Submit response
- `POST   /api/v1/interviews/{session_id}/finalize` — End interview & get report
- `GET    /api/v1/interviews/{session_id}/report` — Get evaluation report
- `GET    /api/v1/health/` — Health check

---

## Development

- **Format:** `black src/` & `isort src/`
- **Lint:** `flake8 src/` & `mypy src/`
- **Test:** `pytest`

---

## Production

- **Docker:**
  ```bash
  docker build -t intervuebot-backend .
  docker run -p 8000:8000 intervuebot-backend
  ```
- **Manual:**  
  `gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker`

---

## License

MIT License