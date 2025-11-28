# AI Legal Negotiation & Mediation Agent

**By Stella Gituire**

## Overview

The AI Legal Negotiation & Mediation Agent is a full-stack, agentic artificial intelligence system designed to automate and support complex legal workflows including contract clause analysis, negotiation simulation, and dispute mediation.
Built with a modular architecture and grounded in Kenyan legal standards, the system functions as an intelligent assistant capable of interpreting agreements, identifying risks, generating negotiation strategies, and proposing fair, legally compliant resolutions.

This project demonstrates how advanced agentic AI systems can support legal professionals, businesses, and individuals by providing accessible, transparent, and cost-efficient legal reasoning.

---

## Key Features

### Automated Contract Clause Analysis

* Extracts and segments contract clauses.
* Identifies risks, ambiguities, conflicts, and compliance gaps.
* Generates structured legal reasoning with Kenyan law context.

### Negotiation Simulator

* Produces multi-turn negotiation between Party A and Party B.
* Generates negotiation dialogue, trade-offs, mutually beneficial revisions, and justifications.
* Designed to mimic professional contract negotiation practices.

### Mediation Engine

* Provides a neutral dispute summary.
* Extracts interests for each party.
* Offers objective evaluation and fair, legally grounded compromise.
* Aligned with Alternative Dispute Resolution (ADR) principles under Kenyan law.

### Feedback and Adaptive Learning

* Captures user ratings and comments.
* Uses memory and vector embeddings for improved future reasoning.

### Streamlit User Interface

* Clean, interactive web interface.
* Real-time rendering of negotiation and mediation results.
* Export functionality for generated outputs.

---

## System Architecture

### High-Level Architecture

```
Frontend (Streamlit UI)
        │
        ▼
Backend API (FastAPI)
    - Clause Parsing
    - Negotiation Engine
    - Mediation Engine
    - Feedback Manager
    - Memory and Embedding Utilities
        │
        ▼
LLM Reasoning Layer (OpenAI GPT Models)
        │
        ▼
Persistent Memory (ChromaDB / Embedding Storage)
```

The architecture follows a modular, extensible design suitable for research, enterprise integrations, and future expansion.

---

## Agent Design (PEAS Framework)

### Performance Measures

* Accuracy of clause interpretation
* Fairness of negotiation proposals
* Legal compliance
* User satisfaction
* Efficiency in dispute resolution

### Environment

* Uploaded legal documents
* Multi-party negotiation and mediation scenarios
* Real-time user inputs

### Actuators

* Draft clause generation
* Negotiation dialogue
* Mediation proposals
* Explanatory reasoning
* Structured outputs delivered through API and UI

### Sensors

* Contract parser
* User input forms
* Embedding memory store
* Feedback collection system

---

## Implementation Roadmap

### Phase 1: Research & Design

* Contract dataset study
* Clause structure mapping
* System architecture planning

### Phase 2: Prototype Development

* Backend API
* Contract parser
* Initial negotiation engine

### Phase 3: Memory and Feedback Integration

* Embedding manager
* Chroma-based memory
* Feedback loop

### Phase 4: User Interface & Testing

* Streamlit UI
* Live testing and refinement

### Phase 5: Evaluation & Documentation

* Performance metrics
* Reporting and presentation

---

## Relevance to Legal Practice in Kenya

The system addresses core challenges in the Kenyan legal sector:

### Efficiency and Cost Reduction

Automates repetitive tasks such as clause extraction, risk detection, and compliance checks.
Enables law firms to handle higher volumes of contracts without increasing headcount.

### Accessibility

Supports SMEs and individuals who cannot afford full legal representation.
Acts as an AI-assisted legal analyst, enhancing access to justice.

### Compliance and Governance

Aligns clauses with:

* Data Protection Act (2019)
* Companies Act (2015)
* Employment Act
* ADR frameworks under the Arbitration Act

### Capacity Building

Assists junior advocates by explaining legal reasoning and negotiation logic.

### Alignment with National Priorities

Supports Kenya’s Judiciary modernization efforts and Digital Economy Blueprint.

---

## Technology Stack

### Backend

* Python
* FastAPI
* OpenAI API
* SpaCy, PyPDF2
* Hugging Face transformers
* ChromaDB (embeddings and memory)

### Frontend

* Streamlit
* Custom markdown and clause rendering

### Data and Persistence

* Embedding store
* Optional PostgreSQL integration

### Deployment

* Docker-ready
* Compatible with AWS, Azure, GCP

---

## Directory Structure

```
ai-legal-negotiation-agent/
│
├── backend/
│   ├── negotiation.py
│   ├── mediation.py
│   ├── reasoning.py
│   ├── feedback.py
│   ├── parser.py
│   ├── routes.py
│   ├── server.py
│   ├── pdf_utils.py
│   ├── utils/
│   │    ├── embedding_manager.py
│   │    ├── sentiment_analyzer.py
│
├── frontend/
│   └── ui.py
│
├── notebooks/
│   ├── clean_and_embed.ipynb
│   ├── adaptive_learning_test.ipynb
│
└── README.md
```

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/SWangechi/ai-legal-negotiation-agent.git
cd ai-legal-negotiation-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Install project dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env`:

```
OPENAI_API_KEY=your_key_here
```

### 5. Run the backend API

```bash
uvicorn backend.server:app --reload
```

### 6. Launch the frontend UI

```bash
streamlit run frontend/ui.py
```

---

## Usage Guide

### Contract Analysis

* Paste or upload contract text
* System extracts clauses and performs structured analysis
* Displays reasoning, risks, and compliance notes

### Negotiation Simulation

* Enter clause and counterparty position
* AI generates negotiation dialogue and revised clause
* Download results as text

### Mediation

* Enter positions for Party A and Party B
* System generates a neutral summary, interests, evaluation, and compromise

---

## Future Enhancements

* Full Retrieval-Augmented Generation (RAG) with Kenyan law corpora
* Multi-party live negotiation environment
* Automatic clause drafting templates
* Domain-specific fine-tuning
* Voice-based negotiation and mediation
* Legal risk scoring engine

---

## Contributing

Contributions are welcome.
To propose improvements or add features, open an issue or submit a pull request.

---

## License

This project is released under the MIT License.

---

## Author

**Stella Gituire**
AI Engineer, LegalTech Innovator
GitHub: [https://github.com/SWangechi](https://github.com/SWangechi)

