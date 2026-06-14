"""Animal Repository Module.

Responsible for persisting AnimalDocument instances
to PostgreSQL with pgvector extension using psycopg2.
"""

import logging
from typing import Optional

import psycopg2
import psycopg2.extras

from src.config.settings import Settings
from src.models.animal_document import AnimalDocument

logger = logging.getLogger(__name__)


class AnimalRepository:
    """Repository layer for AnimalDocument persistence.

    Manages insert operations against PostgreSQL with pgvector,
    using psycopg2 for database connectivity.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize AnimalRepository with database connection settings.

        Args:
            settings: Application settings containing database configuration.
        """
        self.settings = settings
        self._connection = None

    def _get_connection(self):
        """Get or create a database connection.

        Returns:
            psycopg2 connection object.
        """
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                host=self.settings.database_host,
                port=self.settings.database_port,
                dbname=self.settings.database_name,
                user=self.settings.database_user,
                password=self.settings.database_password,
            )
        return self._connection

    def close(self) -> None:
        """Close the database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("Database connection closed.")

    def truncate(self) -> None:
        """Truncate the animals table and restart identity sequence.

        This is acceptable for V1 to ensure clean re-runs.
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE animals RESTART IDENTITY;")
            conn.commit()
            logger.info("Truncated animals table.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to truncate animals table: {e}")
            raise

    def save_animal(self, animal: AnimalDocument) -> None:
        """Save a single AnimalDocument to the database.

        Args:
            animal: AnimalDocument to persist.

        Raises:
            Exception: If the insert operation fails.
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO animals (
                        name, description, wikipedia_summary, search_document,
                        habitat, diet, family, conservation_status,
                        embedding
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        animal.name,
                        animal.description,
                        animal.wikipedia_summary,
                        animal.search_document,
                        animal.habitat,
                        animal.diet,
                        animal.family,
                        animal.conservation_status,
                        self._format_embedding(animal.embedding),
                    ),
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save animal '{animal.name}': {e}")
            raise

    def save_animals(self, animals: list[AnimalDocument]) -> int:
        """Save a batch of AnimalDocuments to the database.

        Commits only after successful batch insert.
        Rolls back on any failure.

        Args:
            animals: List of AnimalDocument instances to persist.

        Returns:
            Number of animals successfully inserted.

        Raises:
            Exception: If the batch insert operation fails.
        """
        conn = self._get_connection()
        inserted_count = 0

        try:
            with conn.cursor() as cursor:
                for animal in animals:
                    cursor.execute(
                        """
                        INSERT INTO animals (
                            name, description, wikipedia_summary, search_document,
                            habitat, diet, family, conservation_status,
                            embedding
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            animal.name,
                            animal.description,
                            animal.wikipedia_summary,
                            animal.search_document,
                            animal.habitat,
                            animal.diet,
                            animal.family,
                            animal.conservation_status,
                            self._format_embedding(animal.embedding),
                        ),
                    )
                    inserted_count += 1

            conn.commit()
            logger.info(f"Successfully persisted {inserted_count} animals to PostgreSQL.")

        except Exception as e:
            conn.rollback()
            logger.error(f"Batch insert failed after {inserted_count} records: {e}")
            raise

        return inserted_count

    def _format_embedding(self, embedding: Optional[list[float]]) -> Optional[str]:
        """Convert Python embedding list to pgvector format string.

        Converts [0.12, -0.45, 0.89] to '[0.12,-0.45,0.89]'

        Args:
            embedding: List of float values or None.

        Returns:
            pgvector-compatible string representation or None.
        """
        if embedding is None:
            return None

        values = ",".join(str(v) for v in embedding)
        return f"[{values}]"