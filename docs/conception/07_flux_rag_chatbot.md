# 🤖 Diagramme de Flux RAG Chatbot – Smart Focus & Life Assistant

**Version** : 1.0  
**Date** : 01 Mars 2026  
**Phase** : Conception  
**Technologies** : LangChain · ChromaDB · OpenAI GPT-3.5/4 · FastAPI

---

## 1. Vue d'Ensemble du Pipeline RAG

```mermaid
flowchart TD
    subgraph INGEST["📥 Phase 1 – Ingestion (Upload)"]
        UP["📄 Upload Document\n(PDF / PPTX / DOCX)"]
        PARSE["📝 Parsing du fichier\n(PyMuPDF / python-pptx)"]
        CHUNK["✂️ Chunking\n(500 tokens, overlap 50)"]
        EMBED["🔢 Génération Embeddings\n(text-embedding-3-small)"]
        STORE["💾 Stockage\nChromaDB (vecteurs)\n+ PostgreSQL (métadonnées)"]

        UP --> PARSE --> CHUNK --> EMBED --> STORE
    end

    subgraph QUERY["🔍 Phase 2 – Requête (Question)"]
        QUESTION["❓ Question Utilisateur\n(via Flutter Chatbot)"]
        EMBED_Q["🔢 Embedding de la question\n(text-embedding-3-small)"]
        SEARCH["🔎 Recherche Sémantique\n(ChromaDB cosine similarity\nTop-K = 5 chunks)"]
        RERANK["📊 Re-ranking\n(pertinence + diversité)"]
        CONTEXT["📋 Construction du Contexte\n(chunks sélectionnés + historique chat)"]

        QUESTION --> EMBED_Q --> SEARCH --> RERANK --> CONTEXT
    end

    subgraph GENERATE["💬 Phase 3 – Génération"]
        PROMPT["🧩 Construction du Prompt\nSystem + Context + Question"]
        LLM["🤖 LLM (GPT-3.5-turbo)\nGénération de la réponse"]
        SOURCES["📎 Attribution des sources\n(doc + page + chunk)"]
        ANSWER["✅ Réponse finale\n+ sources affichées"]

        PROMPT --> LLM --> SOURCES --> ANSWER
    end

    STORE -.->|"Vecteurs disponibles"| SEARCH
    CONTEXT --> PROMPT
```
