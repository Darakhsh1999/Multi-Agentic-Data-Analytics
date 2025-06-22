# Distributed Data Analytics Agents

### A production-ready, multi-agent framework that automates data ingestion, cleaning, and indexing with Large Language Models.

[![Demo Video](https://cdn.loom.com/sessions/thumbnails/e1595ccafa004ec1887eb939d96410cb-f539aa7e878733ee-full-play.gif)](https://www.loom.com/share/e1595ccafa004ec1887eb939d96410cb?sid=e26f1db6-0067-4a8b-9c90-003984f3dc2f)

---

## Overview
`distributed-data-analytics-agents` orchestrates specialised LangGraph/LangChain agents to transform raw datasets into analysis-ready assets. Upload a collection of CSV, Excel, PDF or text files and the system will:

1. Profile and lint each file.
2. Apply context-aware cleaning and normalisation.
3. Generate metadata and embeddings for fast retrieval.
4. Persist cleaned outputs and an index for downstream analytics.

---

## Architecture

| Component | Responsibility |
|-----------|---------------|
| **Streamlit Front-End** | Provides an interactive web interface for file upload and chat-style control. |
| **UI Agent** | Parses user instructions and launches workflows via LangGraph. |
| **Data-Cleaning Agent** | Executes a React-style plan to cleanse, convert, and standardise tabular/text data using Pandas & LLM tools. |
| **Indexing Agent** | Extracts schema, summarises content, and stores metadata for quick retrieval. |

---

## Tech Stack

- **Streamlit** – interactive front-end
- **LangChain + LangGraph** – agent framework & workflow orchestration
- **Pandas** – data manipulation
- **LLMs** – OpenAI GPT-4o *(optional)* or Qwen via **Ollama** *(default)*

---

## Getting Started

### Installation & Setup

```bash
uv sync
uv venv
source .venv/bin/activate
```

### Running the Application
```bash
streamlit run src/app.py
```