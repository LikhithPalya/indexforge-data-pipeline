"""Animal Document Model.

Defines the core data model representing an animal document
in the IndexForge semantic search index.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AnimalDocument:
    """Represents a fully enriched animal document ready for indexing.

    This model captures all stages of the pipeline transformation:
    raw structured data, generated description, Wikipedia enrichment,
    composite search document, and the final vector embedding.
    """

    id: Optional[int] = None
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

    # Additional structured fields
    conservation_status: Optional[str] = None
    family: Optional[str] = None
    gestation_period: Optional[str] = None
    top_speed: Optional[str] = None
    social_structure: Optional[str] = None
    offspring_per_birth: Optional[str] = None

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

    def to_dict(self) -> dict:
        """Return a dictionary representation of the AnimalDocument.

        Returns:
            Dictionary containing all fields and their values.
        """
        return asdict(self)

    def has_embedding(self) -> bool:
        """Check whether this document has a valid embedding.

        Returns:
            True if embedding exists and contains values, False otherwise.
        """
        return self.embedding is not None and len(self.embedding) > 0

    def has_search_document(self) -> bool:
        """Check whether this document has a valid search document.

        Returns:
            True if search_document exists and is not empty, False otherwise.
        """
        return self.search_document is not None and self.search_document.strip() != ""