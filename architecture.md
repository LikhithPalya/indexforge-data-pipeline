# Architecture: IndexForge Data Pipeline

## System Overview

IndexForge Data Pipeline is an offline batch processing system that transforms raw animal data into semantically searchable, vector-indexed documents stored in PostgreSQL with pgvector.

---

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PIPELINE ORCHESTRATOR                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1: INGESTION                                                  │
│  ┌──────────────┐                                                    │
│  │ DatasetReader │ → Reads CSV/JSON raw files from data/raw/         │
│  └──────────────┘                                                    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2: CLEANING                                                   │
│  ┌─────────────┐                                                     │
│  │ DataCleaner │ → Normalizes fields, handles missing data,          │
│  └─────────────┘   validates types, deduplicates                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 3: DESCRIPTION GENERATION                                     │
│  ┌────────────────────┐                                              │
│  │ DescriptionBuilder │ → Generates natural language descriptions    │
│  └────────────────────┘   from structured fields                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 4: ENRICHMENT                                                 │
│  ┌──────────────────────────────┐                                    │
│  │ WikipediaEnrichmentService   │ → Fetches Wikipedia summaries      │
│  └──────────────────────────────┘   via Wikipedia API                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 5: SEARCH DOCUMENT CREATION                                   │
│  ┌───────────────────────┐                                           │
│  │ SearchDocumentBuilder │ → Composes a unified searchable text      │
│  └───────────────────────┘   from description + wikipedia_summary    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 6: EMBEDDING GENERATION                                       │
│  ┌────────────────────┐                                              │
│  │ EmbeddingGenerator │ → Encodes search_document into a 384-dim    │
│  └────────────────────┘   vector using all-MiniLM-L6-v2             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 7: PERSISTENCE                                                │
│  ┌──────────────────┐                                                │
│  │ AnimalRepository │ → Saves AnimalDocument to PostgreSQL           │
│  └──────────────────┘   with pgvector for embedding storage          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Model: AnimalDocument

| Field              | Type          | Description                                      |
|--------------------|---------------|--------------------------------------------------|
| `id`              | UUID          | Unique identifier                                |
| `name`           | str           | Common name of the animal                        |
| `height`         | str           | Average height (with unit)                       |
| `weight`         | str           | Average weight (with unit)                       |
| `color`          | str           | Primary coloring                                 |
| `lifespan`       | str           | Average lifespan                                 |
| `diet`           | str           | Dietary classification                           |
| `habitat`        | str           | Primary habitat                                  |
| `predators`      | list[str]     | Known natural predators                          |
| `average_speed`  | str           | Average movement speed                           |
| `countries_found`| list[str]     | Countries where the animal is found              |
| `description`    | str           | Generated natural language description           |
| `wikipedia_summary` | str        | Enriched summary from Wikipedia                  |
| `search_document`| str           | Composite searchable text                        |
| `embedding`      | list[float]   | 384-dimensional vector embedding                 |
| `created_at`     | datetime      | Timestamp of document creation                   |

---

## Component Responsibilities

### DatasetReader
- Reads raw data files (CSV, JSON) from `data/raw/`
- Parses records into intermediate dictionaries
- Handles multiple file formats

### DataCleaner
- Normalizes field values (case, units, whitespace)
- Validates required fields
- Handles missing or malformed data
- Deduplicates records

### DescriptionBuilder
- Takes structured animal data
- Produces a human-readable natural language description
- Template-based generation

### WikipediaEnrichmentService
- Queries Wikipedia API for animal summaries
- Handles rate limiting and retries
- Caches results to `data/enriched/`

### SearchDocumentBuilder
- Combines `description` + `wikipedia_summary`
- May include additional structured metadata
- Produces the final `search_document` field

### EmbeddingGenerator
- Loads sentence-transformers model (all-MiniLM-L6-v2)
- Generates 384-dimensional embeddings
- Supports batch processing

### AnimalRepository
- CRUD operations for AnimalDocument
- Uses SQLAlchemy with pgvector extension
- Connection pooling and transaction management

### PipelineOrchestrator
- Coordinates all pipeline stages
- Manages error handling and retries
- Supports partial re-runs
- Logs progress and metrics

---

## Database Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE animals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    height VARCHAR(100),
    weight VARCHAR(100),
    color VARCHAR(100),
    lifespan VARCHAR(100),
    diet VARCHAR(100),
    habitat VARCHAR(255),
    predators TEXT[],
    average_speed VARCHAR(100),
    countries_found TEXT[],
    description TEXT,
    wikipedia_summary TEXT,
    search_document TEXT,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_animals_embedding ON animals
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## Configuration

All configuration is managed via environment variables (`.env` file):

- `DATABASE_URL` — PostgreSQL connection string
- `WIKIPEDIA_API_BASE_URL` — Wikipedia API endpoint
- `EMBEDDING_MODEL_NAME` — Sentence transformer model name
- `BATCH_SIZE` — Processing batch size
- `LOG_LEVEL` — Logging verbosity

---

## Error Handling Strategy

1. **Stage-level retries** — Each stage can be retried independently
2. **Dead letter queue** — Failed records are logged for manual review
3. **Idempotency** — Re-running the pipeline does not create duplicates
4. **Checkpointing** — Pipeline can resume from last successful stage

---

## Future Enhancements

- [ ] Add Apache Airflow DAG for scheduled runs
- [ ] Implement incremental indexing (delta updates)
- [ ] Add data quality monitoring and alerting
- [ ] Support multi-model embeddings (comparison)
- [ ] Add CDC (Change Data Capture) from source systems