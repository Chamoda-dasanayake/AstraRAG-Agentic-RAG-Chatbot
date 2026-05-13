# 🚀 AstraRAG – Agentic RAG Chatbot

AstraRAG is an intelligent chatbot that combines **Retrieval-Augmented Generation (RAG)** with AI agents to deliver accurate, context-aware answers from your custom documents.

---

## 📌 Problem Statement
Traditional chatbots often generate inaccurate or hallucinated responses due to limited context awareness and lack of real-time knowledge retrieval.  

Basic RAG systems also follow a static pipeline, making them less effective for complex queries and multi-step reasoning.

---

## 💡 Solution
AstraRAG enhances RAG by integrating **AI agents** that can plan, retrieve, and refine information before generating responses.  

This enables:
- Better reasoning  
- Dynamic query handling  
- More accurate, context-aware answers  

---

## 🧠 Core Concept
Instead of relying only on pre-trained knowledge, AstraRAG:
- Retrieves relevant information from your documents  
- Augments prompts with contextual data  
- Generates accurate, source-backed responses  

---

## ⚙️ How It Works

| Step | Component            | Description |
|------|---------------------|------------|
| 1    | Document Ingestion  | Files are chunked, embedded, and stored in ChromaDB |
| 2    | Query Embedding     | User query is converted into a vector |
| 3    | Semantic Search     | Relevant document chunks are retrieved |
| 4    | Agent Reasoning     | AI agent analyzes and refines the response |
| 5    | LLM Generation      | LLM generates the final answer |

---

## ✨ Key Features
- 🤖 Agentic AI with autonomous reasoning  
- 📚 Custom document-based knowledge  
- 🔍 Source-aware responses  
- ⚡ Fast inference using optimized LLMs  
- 💻 Streamlit-based chat UI  
- 🔗 FastAPI backend for integration  

---

## 🎯 Use Cases
- Internal knowledge bases  
- Research assistants  
- Customer support systems  
- Domain-specific Q&A (technical, academic, etc.)  

---

## 🛠️ Tech Stack

| Technology | Role |
|-----------|------|
| Streamlit | Frontend UI |
| FastAPI | Backend API |
| CrewAI | AI Agent orchestration |
| ChromaDB | Vector database |
| OpenAI / Google Gemini | LLM (via `.env`) |
| BAAI/bge-small-en-v1.5 | Embedding model |

---

## ☁️ Deploy (simple path)

Step-by-step **Render (API) + Streamlit Cloud (UI)** is in **[DEPLOY.md](DEPLOY.md)**.

---

## ⚙️ How to Run

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Chamoda-dasanayake/AstraRAG-Agentic-RAG-Chatbot.git
cd AstraRAG-Agentic-RAG-Chatbot
```

### 2️⃣ Environment
Copy `.env.example` to `.env`. Set **`OPENAI_API_KEY`** for OpenAI models (`MODEL_NAME=gpt-4o-mini`), or **`GOOGLE_API_KEY`** plus a Gemini **`MODEL_NAME`** (see `.env.example`).

### 3️⃣ Install and run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**API** (terminal 1): `python -m src.backend_src.main`  
**UI** (terminal 2): `streamlit run src/frontend_src/app.py`

Point `API_BASE_URL` / `CHAT_ENDPOINT_URL` in `.env` at the API (defaults: `http://localhost:8001`).

### 4️⃣ Smoke test
`GET http://localhost:8001/health` should return `{"status":"healthy",...}`.

---

## 📁 Repository layout (short)

| Path | Purpose |
|------|---------|
| `src/backend_src/` | FastAPI app, document + chat services |
| `src/agents_src/` | CrewAI agents, tasks, tools, settings |
| `src/frontend_src/` | Streamlit UI |
| `src/rag_doc_ingestion/` | Optional CLI ingestion |
| `DEPLOY.md` | Production deploy steps |

---
