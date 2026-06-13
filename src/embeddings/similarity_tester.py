"""Similarity Tester Module.

Provides cosine similarity computation and semantic search
demonstrations using generated embeddings.
"""

import math

from src.embeddings.embedding_generator import EmbeddingGenerator
from src.models.animal_document import AnimalDocument


class SimilarityTester:
    """Tests semantic similarity between query texts and animal embeddings.

    Computes cosine similarity between query embeddings and
    pre-computed animal document embeddings to find the most
    semantically similar animals.
    """

    DEMO_QUERIES: list[str] = [
        "large predators in asia",
        "animals that live in forests",
        "fast carnivores",
        "carnivorous animals",
        "animals found in africa",
        "herbivores living in forests",
        "group based carnivores",
        "animals with least concern conservation status",
        "solitary insectivores",
        "fast predators",
    ]

    NEIGHBOR_ANIMALS: list[str] = [
        "Tiger",
        "African Lion",
        "Wolf",
        "African Elephant",
    ]

    def __init__(self, embedding_generator: EmbeddingGenerator) -> None:
        """Initialize SimilarityTester with an embedding generator.

        Args:
            embedding_generator: EmbeddingGenerator instance for encoding queries.
        """
        self.embedding_generator = embedding_generator

    def cosine_similarity(self, embedding_a: list[float], embedding_b: list[float]) -> float:
        """Compute cosine similarity between two embedding vectors.

        Args:
            embedding_a: First embedding vector.
            embedding_b: Second embedding vector.

        Returns:
            Cosine similarity score between -1.0 and 1.0.

        Raises:
            ValueError: If embeddings have different dimensions.
        """
        if len(embedding_a) != len(embedding_b):
            raise ValueError(
                f"Embedding dimension mismatch: {len(embedding_a)} vs {len(embedding_b)}"
            )

        dot_product = sum(a * b for a, b in zip(embedding_a, embedding_b))
        magnitude_a = math.sqrt(sum(a * a for a in embedding_a))
        magnitude_b = math.sqrt(sum(b * b for b in embedding_b))

        if magnitude_a == 0.0 or magnitude_b == 0.0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    def find_most_similar(
        self,
        query_embedding: list[float],
        animals: list[AnimalDocument],
        top_k: int = 5,
        exclude_name: str | None = None,
    ) -> list[tuple[str, float]]:
        """Find the most similar animals to a query embedding.

        Args:
            query_embedding: Embedding vector for the search query.
            animals: List of AnimalDocument instances with embeddings.
            top_k: Number of top results to return.
            exclude_name: Optional animal name to exclude from results (for neighbor search).

        Returns:
            List of tuples containing (animal_name, similarity_score),
            sorted by similarity in descending order.
        """
        scores: list[tuple[str, float]] = []

        for animal in animals:
            if not animal.has_embedding():
                continue

            # Skip the animal itself for nearest neighbor search
            if exclude_name and animal.name and animal.name.lower() == exclude_name.lower():
                continue

            similarity = self.cosine_similarity(query_embedding, animal.embedding)
            scores.append((animal.name or "Unknown", similarity))

        # Sort by similarity score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_k]

    def run_demo(self, animals: list[AnimalDocument]) -> dict[str, list[tuple[str, float]]]:
        """Run similarity demonstrations with predefined queries.

        Generates embeddings for demo queries and finds the top 10
        most similar animals for each.

        Args:
            animals: List of AnimalDocument instances with embeddings.

        Returns:
            Dictionary mapping query text to list of (animal_name, score) tuples.
        """
        results: dict[str, list[tuple[str, float]]] = {}

        for query in self.DEMO_QUERIES:
            query_embedding = self.embedding_generator.generate_embedding(query)
            top_matches = self.find_most_similar(query_embedding, animals, top_k=10)
            results[query] = top_matches

        return results

    def run_neighbor_evaluation(
        self, animals: list[AnimalDocument]
    ) -> dict[str, list[tuple[str, float]]]:
        """Find nearest neighbors for specific animals in the dataset.

        For each animal in NEIGHBOR_ANIMALS, uses its own search_document
        embedding to find the top 5 most similar animals (excluding itself).

        Args:
            animals: List of AnimalDocument instances with embeddings.

        Returns:
            Dictionary mapping animal name to list of (neighbor_name, score) tuples.
        """
        results: dict[str, list[tuple[str, float]]] = {}

        for animal_name in self.NEIGHBOR_ANIMALS:
            # Find the animal in the dataset
            target_animal = next(
                (a for a in animals if a.name and a.name.lower() == animal_name.lower()),
                None,
            )

            if target_animal is None or not target_animal.has_embedding():
                results[animal_name] = []
                continue

            # Find nearest neighbors excluding itself
            neighbors = self.find_most_similar(
                target_animal.embedding,
                animals,
                top_k=5,
                exclude_name=animal_name,
            )
            results[animal_name] = neighbors

        return results