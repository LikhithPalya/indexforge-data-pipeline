# IndexForge Data Pipeline

## Overview

**IndexForge Data Pipeline** is a production-grade offline ingestion and indexing pipeline for building and maintaining the semantic search index for the **Animal Kingdom** dataset.

This repository is responsible for:
- Ingesting raw animal data from structured datasets
- Cleaning and normalizing records
- Generating rich natural language descriptions
- Enriching documents with Wikipedia summaries
- Building composite search documents
- Generating vector embeddings
- Persisting indexed documents to PostgreSQL with pgvector

> ⚠️ This repository performs **offline ingestion and indexing only**. It does **NOT** serve search requests.

---

## Pipeline Flow

```
Animal Dataset
     ↓
  Cleaning
     ↓
Description Generation
     ↓
Wikipedia Enrichment
     ↓
Search Document Creation
     ↓
Embedding Generation
     ↓
PostgreSQL + pgvector
```

For detailed architecture documentation, see [architecture.md](./architecture.md).

---

## Tech Stack

| Component         | Technology              |
|-------------------|-------------------------|
| Language          | Python 3.12             |
| Database          | PostgreSQL + pgvector   |
| Embeddings        | all-MiniLM-L6-v2       |
| Enrichment        | Wikipedia API           |
| ORM               | SQLAlchemy              |
| Configuration     | python-dotenv / Pydantic |

---

## Project Structure

```
indexforge-data-pipeline/
│
├── data/
│   ├── raw/                    # Raw animal dataset files
│   ├── processed/              # Cleaned and normalized data
│   └── enriched/               # Data with Wikipedia enrichment
│
├── src/
│   ├── ingestion/              # Dataset reading and parsing
│   ├── cleaning/               # Data cleaning and normalization
│   ├── description_builder/    # Natural language description generation
│   ├── enrichment/             # Wikipedia enrichment service
│   ├── embeddings/             # Vector embedding generation
│   ├── database/               # Repository layer (PostgreSQL/pgvector)
│   ├── config/                 # Application configuration
│   ├── models/                 # Data models (AnimalDocument)
│   └── pipeline/               # Pipeline orchestration
│
├── tests/                      # Unit and integration tests
│
├── requirements.txt
├── .env.example
├── README.md
└── architecture.md
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 15+ with pgvector extension
- Virtual environment (recommended)

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### Configuration

Edit `.env` with your database credentials and API keys.

### Running the Pipeline

```bash
python -m src.pipeline.pipeline_orchestrator
```

---

## Pipeline Components

| Component                     | Responsibility                                      |
|-------------------------------|-----------------------------------------------------|
| `DatasetReader`               | Reads and parses raw animal dataset files           |
| `DataCleaner`                 | Normalizes, validates, and cleans raw records       |
| `DescriptionBuilder`          | Generates natural language descriptions             |
| `WikipediaEnrichmentService`  | Fetches Wikipedia summaries for animals             |
| `SearchDocumentBuilder`       | Composes the final searchable document text         |
| `EmbeddingGenerator`          | Generates vector embeddings from search documents   |
| `AnimalRepository`            | Persists and retrieves documents from PostgreSQL    |
| `PipelineOrchestrator`        | Coordinates the full end-to-end pipeline            |

---

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

```bash
ruff check src/ tests/
black src/ tests/
mypy src/
```

---

## License

MIT License