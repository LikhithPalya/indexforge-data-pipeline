"""Embedding Generator Module.

Responsible for generating vector embeddings from search documents
using the sentence-transformers library with all-MiniLM-L6-v2 model.
"""

import logging
from sentence_transformers import SentenceTransformer

from src.models.animal_document import AnimalDocument

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates vector embeddings for animal search documents.

    Uses sentence-transformers (all-MiniLM-L6-v2) to encode
    search document text into 384-dimensional vector embeddings
    suitable for semantic similarity search.
    """

    EXPECTED_DIMENSION = 384

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize EmbeddingGenerator by loading the sentence-transformer model.

        Args:
            model_name: Name of the sentence-transformer model to use.
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        logger.info(f"Model loaded successfully. Embedding dimension: {self.EXPECTED_DIMENSION}")

    def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text string.

        Args:
            text: Text string to encode.

        Returns:
            384-dimensional embedding vector as a list of floats.

        Raises:
            ValueError: If text is None or empty.
            ValueError: If generated embedding dimension does not match expected.
        """
        if not text or text.strip() == "":
            raise ValueError("Cannot generate embedding for empty text.")

        embedding = self.model.encode(text).tolist()

        if len(embedding) != self.EXPECTED_DIMENSION:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.EXPECTED_DIMENSION}, "
                f"got {len(embedding)}"
            )

        return embedding

    def generate_embeddings(self, animals: list[AnimalDocument]) -> list[AnimalDocument]:
        """Generate embeddings for a list of AnimalDocument instances.

        Encodes each animal's search_document field into a 384-dimensional
        vector and stores it in the animal's embedding field.

        Args:
            animals: List of AnimalDocument instances with populated search_document fields.

        Returns:
            List of AnimalDocument instances with populated embedding fields.
        """
        total = len(animals)
        logger.info(f"Generating embeddings for {total} animals...")
        processed = 0
        skipped = 0

        for i, animal in enumerate(animals, start=1):
            # Validate search_document exists
            if not animal.has_search_document():
                logger.warning(f"Skipping '{animal.name}': no search_document available.")
                skipped += 1
                continue

            # Generate and store embedding
            animal.embedding = self.generate_embedding(animal.search_document)
            processed += 1

            # Log progress every 25 animals
            if i % 25 == 0:
                logger.info(f"  Progress: {i}/{total} animals processed")

        logger.info(
            f"Embedding generation complete. "
            f"Processed: {processed}, Skipped: {skipped}, "
            f"Dimension: {self.EXPECTED_DIMENSION}"
        )

        return animals