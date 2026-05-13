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
| OpenAI | Language model |
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
