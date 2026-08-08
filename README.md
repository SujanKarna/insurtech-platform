# InsurTech Platform

An enterprise-oriented insurance platform combining **Java, Spring Boot, Python, and AI**.

The project explores the development of an insurance application with document intelligence, policy management, claims processing, and evidence-grounded AI assistance.

## Current Status

🚧 **Phase 1 — Insurance Document Intelligence**

The project currently focuses on processing German insurance documents and transforming them into structured, searchable data.

The initial document corpus is based on the **Allgemeine Unfallversicherungsbedingungen (AUB 2020)** published by the Gesamtverband der Deutschen Versicherungswirtschaft (GDV), version **June 2025**.

### Current work

* [x] Project initialization
* [x] Initial insurance document selected
* [ ] PDF extraction
* [ ] Document cleaning
* [ ] Structural analysis
* [ ] Section hierarchy reconstruction
* [ ] Provenance-aware representation

## Planned Direction

The document intelligence component will later become part of a larger insurance platform built around a **Spring Boot backend**.

The planned system will eventually combine:

* Insurance policy and claims management
* Document processing
* AI/RAG-based policy assistance
* Secure REST APIs
* Enterprise-oriented backend architecture

More components will be introduced incrementally as the project develops.

## Technology

### Current

* Python
* PyMuPDF
* Pydantic
* pytest

### Planned

* Java / Spring Boot
* PostgreSQL
* Spring Security
* Kafka
* Docker
* React
* RAG / LLM

## Data Source

The initial document is a GDV model insurance condition:

**Allgemeine Unfallversicherungsbedingungen (AUB 2020)**
**Stand: Juni 2025**

The original document is not included in this repository. Source and provenance information will be maintained separately.

---

**Project status:** 🟡 In active development
