"""Animal Document Model.

Defines the core data model representing an animal document
in the IndexForge semantic search index.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class AnimalDocument:
    """Represents a fully enriched animal document ready for indexing.

    This model captures all stages of the pipeline transformation:
    raw structured data, generated description, Wikipedia enrichment,
    composite search document, and the final vector embedding.
    """

    # TODO: Consider using Pydantic BaseModel for validation in production
    # TODO: Add field validators for required fields
    # TODO: Add serialization/deserialization methods

    id: Optional[UUID] = None
    name: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    color: Optional[str] = None
    lifespan: Optional[str] = None
    diet: Optional[str] = None
    habitat: Optional[str] = None
    predators: list[str] = field(default_factory=list)
    average_speed: Optional[str] = None
    countries_found: list[str] = field(default_factory=list)

    # Generated natural language description
    description: Optional[str] = None

    # Enriched Wikipedia summary
    wikipedia_summary: Optional[str] = None

    # Composite search document (description + wikipedia_summary + metadata)
    search_document: Optional[str] = None

    # 384-dimensional vector embedding
    embedding: Optional[list[float]] = None

    # Metadata
    created_at: Optional[datetime] = None