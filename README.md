# AI Research Assistant

An AI-powered research assistant for organizing, searching, summarizing, and querying academic papers.

The system provides a full-stack platform for managing research papers, extracting academic content and metadata, creating research notes, searching paper content, generating research-focused summaries, and asking grounded questions about uploaded papers.

## Overview

The AI Research Assistant is designed to support researchers through the early stages of literature review and academic information management.

Users can upload PDF papers, automatically extract their text and metadata, search their paper collection, create research notes, generate summaries, and ask questions about individual papers.

The application combines:

* **FastAPI** for the backend API
* **React + Vite** for the frontend
* **SQLite + SQLAlchemy** for persistence
* **Alembic** for database migrations
* **PyMuPDF** for PDF text extraction
* **Gemini** for research-focused summarization and question answering
* **Retrieval-based context selection** for grounded responses
* **Pytest** for automated testing

---

## Key Features

### Paper Management

* Upload academic PDF papers
* Extract PDF text automatically
* Store paper information in a relational database
* Extract academic metadata such as:

  * Title
  * Authors
  * DOI
  * Publication year
  * Keywords
* View stored papers
* Update paper metadata
* Delete papers
* Search papers by keywords and titles

### AI-Assisted Research

* Generate research-focused summaries
* Ask questions about individual papers
* Retrieve relevant passages before generating answers
* Ground Gemini responses in retrieved paper content
* Preserve important quantitative results from source material
* Return source excerpts alongside generated answers
* Fall back to local processing when Gemini is unavailable

### Research Notes

* Create notes associated with individual papers
* Retrieve notes
* Update notes
* Delete notes
* Maintain relationships between papers and their research notes

### Web Interface

The React frontend provides a dashboard for:

* Viewing the paper collection
* Searching papers
* Uploading papers
* Viewing paper content
* Generating summaries
* Asking research questions
* Accessing research notes

---

## AI / Retrieval Workflow

The current question-answering pipeline follows a retrieval-grounded approach:

```text
Academic PDF
     │
     ▼
PDF Text Extraction
     │
     ▼
Text Normalization
     │
     ▼
Sentence-Aware Chunking
     │
     ▼
Cosine Similarity + Academic Keyword Boost
     │
     ▼
Relevant Context Retrieval
     │
     ▼
Gemini 3.6 Flash
     │
     ▼
Grounded Answer
     │
     ▼
Source Excerpts
```

The system deliberately retrieves relevant passages before sending context to the language model. This reduces irrelevant context and helps keep responses grounded in the uploaded paper.

The Gemini prompt also instructs the model to:

* Use only information explicitly contained in retrieved passages
* Avoid unsupported inference
* Preserve reported quantitative results
* Avoid unrelated information
* State when the retrieved context is insufficient

---

## Architecture

```text
┌─────────────────────────────────────────────┐
│              React Frontend                 │
│              Vite Development Server        │
└──────────────────────┬──────────────────────┘
                       │ HTTP / REST
                       ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
│                                             │
│  Papers API                                 │
│  Research Notes API                         │
│  AI / Retrieval API                         │
└──────────────┬───────────────┬──────────────┘
               │               │
               ▼               ▼
       ┌──────────────┐  ┌──────────────────┐
       │ SQLite /     │  │ AI Services      │
       │ SQLAlchemy   │  │                  │
       │              │  │ Retrieval        │
       │ Papers       │  │ Summarization    │
       │ Notes        │  │ Gemini Q&A       │
       └──────────────┘  └──────────────────┘
               │
               ▼
       ┌──────────────────┐
       │      Alembic     │
       │ Database Migrate │
       └──────────────────┘
```

---

## Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* SQLite
* PyMuPDF
* Pydantic
* Pytest

### AI

* Google Gemini API
* `google-genai`
* `python-dotenv`
* Retrieval-based context selection
* Cosine similarity
* Academic keyword weighting

### Frontend

* React
* Vite
* Axios
* Lucide React

### Development

* Git
* GitHub
* Virtual environments
* Automated testing

---

## Project Structure

```text
ai-research-assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── ai.py
│   │   │   ├── papers.py
│   │   │   └── research_notes.py
│   │   │
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   ├── init_db.py
│   │   │   └── models.py
│   │   │
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── metadata_service.py
│   │   │   └── pdf_service.py
│   │   │
│   │   ├── main.py
│   │   └── schemas.py
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_ai_service.py
│       ├── test_metadata_service.py
│       ├── test_paper_management.py
│       ├── test_pdf_service.py
│       └── test_research_notes.py
│
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── App.css
│
├── docs/
│   ├── architecture.md
│   └── requirements.md
│
├── data/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## API Capabilities

### Papers

| Method | Endpoint                  | Purpose                 |
| ------ | ------------------------- | ----------------------- |
| POST   | `/papers/upload`          | Upload a PDF paper      |
| GET    | `/papers`                 | List papers             |
| GET    | `/papers/search`          | Search papers           |
| GET    | `/papers/{paper_id}`      | Retrieve a paper        |
| GET    | `/papers/{paper_id}/text` | Retrieve extracted text |
| PUT    | `/papers/{paper_id}`      | Update paper metadata   |
| DELETE | `/papers/{paper_id}`      | Delete a paper          |

### Research Notes

| Method | Endpoint                   | Purpose          |
| ------ | -------------------------- | ---------------- |
| POST   | `/papers/{paper_id}/notes` | Create a note    |
| GET    | `/papers/{paper_id}/notes` | List paper notes |
| GET    | `/notes/{note_id}`         | Retrieve a note  |
| PUT    | `/notes/{note_id}`         | Update a note    |
| DELETE | `/notes/{note_id}`         | Delete a note    |

### AI

The AI API provides:

* Paper summarization
* Question answering
* Retrieved source excerpts
* Gemini-backed generation
* Local fallback processing

Interactive API documentation is available through FastAPI's Swagger interface.

---

## Testing

The project currently has:

**47 automated tests passing.**

The test suite covers:

* PDF processing
* Metadata extraction
* Paper management
* Paper search
* Research notes
* AI services
* Gemini integration
* Error handling
* Database behavior

The Gemini unit tests use mocked clients, so the test suite does not require live Gemini API calls.

Run the complete test suite:

```bash
pytest -q
```

Expected result:

```text
47 passed
```

The project currently reports some dependency deprecation warnings related to `datetime.utcnow()` and Starlette/AnyIO. These do not cause test failures and are planned maintenance items.

---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/julaskky/ai-research-assistant.git
cd ai-research-assistant
```

### 2. Create a virtual environment

Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`.

Windows:

```cmd
copy .env.example .env
```

Then configure:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
AI_PROVIDER=gemini
```

Never commit the `.env` file or expose the API key.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the backend

```bash
uvicorn backend.app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Start the frontend

Open another terminal:

```cmd
cd frontend
npm install
npm run dev
```

The Vite development server will normally be available at:

```text
http://localhost:5173
```

---

## Environment Variables

| Variable         | Description                      |
| ---------------- | -------------------------------- |
| `GEMINI_API_KEY` | Gemini API authentication key    |
| `GEMINI_MODEL`   | Gemini model used for generation |
| `AI_PROVIDER`    | AI provider selection            |

The repository contains `.env.example` as a configuration template.

Actual credentials should remain in `.env`, which is excluded through `.gitignore`.

---

## Engineering Approach

The project is being developed using a structured software engineering workflow:

```text
Requirements
     ↓
System Architecture
     ↓
Database Design
     ↓
API Design
     ↓
Implementation
     ↓
Automated Testing
     ↓
AI Integration
     ↓
Frontend Integration
     ↓
Git / GitHub
     ↓
Future CI/CD
```

The architecture emphasizes:

* Modularity
* Separation of concerns
* Testability
* Maintainability
* Secure configuration
* Extensibility
* Incremental development

---

## Current Limitations

The current retrieval implementation uses lexical similarity and academic keyword weighting rather than a vector database or embedding-based semantic retrieval system.

SQLite is currently used for local development and can be replaced by PostgreSQL as the application scales.

The current system is also primarily designed for individual-paper retrieval and question answering rather than large-scale multi-document research synthesis.

---

## Planned Improvements

Future development may include:

* Embedding-based semantic search
* Vector database integration
* Advanced Retrieval-Augmented Generation (RAG)
* Multi-document question answering
* Citation extraction
* Reference management
* Research-paper recommendations
* Improved metadata extraction
* PostgreSQL support
* Authentication and user accounts
* Docker containerization
* CI/CD with GitHub Actions
* Production deployment
* Expanded frontend testing
* Improved observability and logging

---

## Project Status

**Current status: Functional full-stack prototype with tested Gemini integration.**

The project demonstrates an end-to-end AI application workflow covering:

**PDF ingestion → information extraction → database persistence → retrieval → LLM generation → grounded responses → web interface → automated testing.**

---

## License

This project is currently maintained as a personal research and software engineering portfolio project.
