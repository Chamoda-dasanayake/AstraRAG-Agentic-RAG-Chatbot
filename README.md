AstraRAG – Agentic RAG Chatbot

AstraRAG is an Agentic Retrieval-Augmented Generation (RAG) chatbot that answers user questions using custom documents. The system integrates Streamlit, FastAPI, CrewAI agents, LlamaIndex, ChromaDB, and Groq LLM to build a modular AI application.

🚀 Features

Agent-based AI architecture using CrewAI

Retrieval-Augmented Generation (RAG)

Semantic document search using ChromaDB

Fast inference using Groq LLM

Clean chat interface built with Streamlit

REST API backend with FastAPI

Document ingestion pipeline for knowledge base creation


🏗️ System Architecture

The system consists of five main components:

Document Ingestion Pipeline

Loads documents from docs_dir

Splits documents into smaller chunks

Generates embeddings using BAAI/bge-small-en-v1.5

Stores embeddings in ChromaDB vector database

Agentic AI Layer

Built using CrewAI

A Question Answer Agent acts as a knowledge analyst

Uses Groq LLM (llama-3.1-8b-instant) for reasoning

RAG Retrieval Tool

Converts user query into embeddings

Performs semantic search on ChromaDB

Retrieves the most relevant document chunks

Backend API

Implemented using FastAPI

Provides endpoint: /chat/answer

Handles communication between frontend and AI agents

Frontend Interface

Built using Streamlit

Provides a chat-style interface

Displays answers and document sources

🔄 System Workflow

Add documents to the docs_dir folder

Run the ingestion pipeline to create vector embeddings

Start the FastAPI backend

Launch the Streamlit frontend

Ask questions through the chat interface

The AI agent retrieves relevant document information and generates answers

🛠️ Tech Stack

Frontend

Streamlit

Backend

FastAPI

AI Frameworks

CrewAI

LlamaIndex

Vector Database

ChromaDB

LLM Provider

Groq API

Embedding Model

BAAI/bge-small-en-v1.5
