# IntervueBot

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/darshankparmar/intervueBot)

AI-powered interview platform with FastAPI backend and React frontend.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Agno](https://img.shields.io/badge/Agno-Framework-green.svg)](https://github.com/agno-ai/agno)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features
- Multi-agent interview process (question, evaluation, report)
- Real-time Q&A, session management, and detailed reports
- Modern UI with React

## Quick Start

1. **Clone & Setup**
   ```bash
   git clone https://github.com/yourusername/intervuebot.git
   cd intervuebot
   ```

2. **Backend**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -e .
   cp env.example .env
   # Edit .env as needed
   python -m src.main
   ```

3. **Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

Visit [http://localhost:3000](http://localhost:3000)

---

## Project Structure

```
intervuebot/
├── backend/   # FastAPI backend
├── frontend/  # React frontend
├── uploads/   # Uploaded files
├── README.md
```

---

## Configuration

- Backend: see `backend/env.example`
- Frontend: see `frontend/.env` (if needed)

---

## API Docs

- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## License
Licensed under the [MIT License](LICENSE)
---

## Contributing

Contributors are welcome! This project is not yet fully polished or production-ready—your feedback, issues, and pull requests are appreciated.