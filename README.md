# Insurtech Platform

An enterprise-oriented insurance knowledge platform that combines a
Python-based document/RAG pipeline with a Java Spring Boot backend.

The project is based on the GDV Allgemeine Unfallversicherungsbedingungen
(AUB 2020) and is designed to provide reliable, source-grounded answers
to questions about insurance conditions.

The primary goal of the project is to explore how modern Java backend
engineering can be combined with Retrieval-Augmented Generation (RAG)
for an insurance-domain application.

---

## Project Status

### Completed

- [x] Automated insurance document download
- [x] SHA-256 document hashing and provenance tracking
- [x] PDF text extraction
- [x] Document cleaning and normalization
- [x] Structural document analysis
- [x] Section-aware chunking
- [x] Chunk metadata and provenance
- [x] BAAI/bge-m3 embeddings
- [x] Embedding generation and storage
- [x] Retrieval evaluation
- [x] Qdrant vector database
- [x] Qdrant Docker setup
- [x] Python Qdrant ingestion pipeline
- [x] Python semantic retrieval

### Current Development

- [ ] Spring Boot backend
- [ ] REST API
- [ ] PostgreSQL persistence
- [ ] Java ↔ Qdrant integration
- [ ] Java RAG orchestration
- [ ] LLM integration with Qwen
- [ ] Source-grounded answer generation

### Planned

- [ ] Authentication and authorization
- [ ] API validation and standardized error handling
- [ ] OpenAPI documentation
- [ ] Unit and integration testing
- [ ] Testcontainers
- [ ] Observability and health monitoring
- [ ] Dockerized application stack
- [ ] CI/CD
- [ ] Kubernetes deployment
- [ ] Frontend application

---

# Architecture

The project is intentionally divided into two major parts:

1. **Python Data / AI Pipeline**
2. **Java Spring Boot Application Backend**

The Python pipeline prepares and indexes the insurance knowledge base,
while the Java backend will provide the application-facing API and
orchestrate retrieval and LLM-based answer generation.

```text
                         Client
                           │
                           │ HTTPS / REST
                           ▼
              ┌──────────────────────────┐
              │     Spring Boot API      │
              │                          │
              │  REST Controllers        │
              │        │                 │
              │     Services             │
              │        │                 │
              │  ┌─────┴──────────────┐  │
              │  │                    │  │
              │  ▼                    ▼  │
              │ PostgreSQL          RAG  │
              │                    Service│
              │                       │  │
              └───────────────────────┼──┘
                                      │
                                      ▼
                              ┌─────────────┐
                              │   Qdrant    │
                              │ Vector DB   │
                              └──────┬──────┘
                                     │
                               Retrieved
                                Context
                                     │
                                     ▼
                              ┌─────────────┐
                              │    Qwen     │
                              │     LLM     │
                              └─────────────┘


                 DATA / AI INGESTION PIPELINE

     GDV PDF
        │
        ▼
   Extraction
        │
        ▼
    Cleaning
        │
        ▼
   Structuring
        │
        ▼
    Chunking
        │
        ▼
   BGE-M3 Embedding
        │
        ▼
      Qdrant