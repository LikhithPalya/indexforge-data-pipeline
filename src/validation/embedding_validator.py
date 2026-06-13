"""Embedding Validator Module.

Provides pre-database validation of embedding quality and integrity.
Acts as a quality gate before PostgreSQL/pgvector ingestion.
"""

import math
import random
from dataclasses import dataclass

from src.models.animal_document import AnimalDocument


@dataclass
class ValidationReport:
    """Structured report from embedding validation."""

    total_records: int = 0
    valid_embeddings: int = 0
    invalid_embeddings: int = 0
    invalid_names: list[str] = None

    # Vector stats
    min_value: float = 0.0
    max_value: float = 0.0
    mean_value: float = 0.0
    std_dev: float = 0.0

    # Self similarity check
    self_similarity_pass: bool = False
    self_similarity_min: float = 0.0

    # Sample similarities
    sample_neighbors: dict = None

    def __post_init__(self):
        if self.invalid_names is None:
            self.invalid_names = []
        if self.sample_neighbors is None:
            self.sample_neighbors = {}


class EmbeddingValidator:
    """Validates embedding quality and integrity before database ingestion.

    Performs:
    1. Embedding integrity checks (null, length, numeric, NaN/Inf)
    2. Vector consistency (self-similarity)
    3. Embedding distribution statistics
    4. Duplicate/clustering sanity check (nearest neighbors)
    """

    EXPECTED_DIMENSION = 384

    def __init__(self) -> None:
        """Initialize EmbeddingValidator."""
        pass

    def validate(self, animals: list[AnimalDocument]) -> ValidationReport:
        """Run all validation checks and produce a structured report.

        Args:
            animals: List of AnimalDocument instances with embeddings.

        Returns:
            ValidationReport containing all check results.
        """
        report = ValidationReport()
        report.total_records = len(animals)

        # 1. Integrity checks
        valid_animals, invalid_names = self._check_integrity(animals)
        report.valid_embeddings = len(valid_animals)
        report.invalid_embeddings = len(invalid_names)
        report.invalid_names = invalid_names[:10]  # First 10 only

        # Only proceed with further checks if we have valid embeddings
        if not valid_animals:
            return report

        # 2. Distribution stats
        stats = self._compute_distribution_stats(valid_animals)
        report.min_value = stats["min"]
        report.max_value = stats["max"]
        report.mean_value = stats["mean"]
        report.std_dev = stats["std_dev"]

        # 3. Self-similarity check
        self_sim_pass, self_sim_min = self._check_self_similarity(valid_animals)
        report.self_similarity_pass = self_sim_pass
        report.self_similarity_min = self_sim_min

        # 4. Nearest neighbor sanity check
        report.sample_neighbors = self._check_nearest_neighbors(valid_animals)

        return report

    def _check_integrity(
        self, animals: list[AnimalDocument]
    ) -> tuple[list[AnimalDocument], list[str]]:
        """Check embedding integrity for all animals.

        Validates:
        - embedding is not None
        - embedding length == 384
        - all values are numeric (float/int)
        - no NaN or Inf values

        Args:
            animals: List of AnimalDocument instances.

        Returns:
            Tuple of (valid_animals, invalid_animal_names).
        """
        valid: list[AnimalDocument] = []
        invalid_names: list[str] = []

        for animal in animals:
            name = animal.name or "Unknown"

            # Check not null
            if animal.embedding is None:
                invalid_names.append(name)
                continue

            # Check dimension
            if len(animal.embedding) != self.EXPECTED_DIMENSION:
                invalid_names.append(name)
                continue

            # Check all values are numeric and not NaN/Inf
            has_invalid_value = False
            for val in animal.embedding:
                if not isinstance(val, (int, float)):
                    has_invalid_value = True
                    break
                if math.isnan(val) or math.isinf(val):
                    has_invalid_value = True
                    break

            if has_invalid_value:
                invalid_names.append(name)
                continue

            valid.append(animal)

        return valid, invalid_names

    def _compute_distribution_stats(self, animals: list[AnimalDocument]) -> dict:
        """Compute min, max, mean, std dev across all embedding values.

        Args:
            animals: List of valid AnimalDocument instances with embeddings.

        Returns:
            Dictionary with min, max, mean, std_dev.
        """
        all_values: list[float] = []
        for animal in animals:
            all_values.extend(animal.embedding)

        n = len(all_values)
        if n == 0:
            return {"min": 0.0, "max": 0.0, "mean": 0.0, "std_dev": 0.0}

        min_val = min(all_values)
        max_val = max(all_values)
        mean_val = sum(all_values) / n
        variance = sum((x - mean_val) ** 2 for x in all_values) / n
        std_dev = math.sqrt(variance)

        return {
            "min": min_val,
            "max": max_val,
            "mean": mean_val,
            "std_dev": std_dev,
        }

    def _check_self_similarity(
        self, animals: list[AnimalDocument]
    ) -> tuple[bool, float]:
        """Verify that each animal's embedding has ~1.0 cosine similarity with itself.

        Tests a sample of animals.

        Args:
            animals: List of valid AnimalDocument instances.

        Returns:
            Tuple of (pass/fail, minimum self-similarity score).
        """
        sample_size = min(20, len(animals))
        sample = random.sample(animals, sample_size)

        min_self_sim = 1.0
        for animal in sample:
            sim = self._cosine_similarity(animal.embedding, animal.embedding)
            if sim < min_self_sim:
                min_self_sim = sim

        passed = min_self_sim >= 0.999
        return passed, min_self_sim

    def _check_nearest_neighbors(
        self, animals: list[AnimalDocument]
    ) -> dict[str, list[tuple[str, float]]]:
        """Find top-3 nearest neighbors for 5 random animals.

        Args:
            animals: List of valid AnimalDocument instances.

        Returns:
            Dictionary mapping animal name to list of (neighbor_name, score).
        """
        sample_size = min(5, len(animals))
        sample = random.sample(animals, sample_size)
        results: dict[str, list[tuple[str, float]]] = {}

        for target in sample:
            scores: list[tuple[str, float]] = []
            for other in animals:
                if other.name == target.name:
                    continue
                sim = self._cosine_similarity(target.embedding, other.embedding)
                scores.append((other.name or "Unknown", sim))

            scores.sort(key=lambda x: x[1], reverse=True)
            results[target.name or "Unknown"] = scores[:3]

        return results

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            a: First vector.
            b: Second vector.

        Returns:
            Cosine similarity score.
        """
        dot_product = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))

        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0

        return dot_product / (mag_a * mag_b)

    def print_report(self, report: ValidationReport) -> None:
        """Print a formatted validation report.

        Args:
            report: ValidationReport to display.
        """
        print("\n" + "=" * 70)
        print("IndexForge Embedding Validation Report")
        print("=" * 70)

        print(f"\n  Total Records:      {report.total_records}")
        print(f"  Valid Embeddings:   {report.valid_embeddings}")
        print(f"  Invalid Embeddings: {report.invalid_embeddings}")

        if report.invalid_names:
            print(f"\n  Invalid Animals (first 10):")
            for name in report.invalid_names:
                print(f"    ✗ {name}")

        print(f"\n  Vector Stats:")
        print(f"    - Min:     {report.min_value:.6f}")
        print(f"    - Max:     {report.max_value:.6f}")
        print(f"    - Mean:    {report.mean_value:.6f}")
        print(f"    - Std Dev: {report.std_dev:.6f}")

        status = "PASS ✓" if report.self_similarity_pass else "FAIL ✗"
        print(f"\n  Self Similarity Check: {status} (min: {report.self_similarity_min:.6f})")

        if report.sample_neighbors:
            print(f"\n  Sample Nearest Neighbors:")
            for animal_name, neighbors in report.sample_neighbors.items():
                neighbor_str = ", ".join(
                    f"{name} ({score:.4f})" for name, score in neighbors
                )
                print(f"    {animal_name} → {neighbor_str}")

        print("\n" + "=" * 70)

        if report.invalid_embeddings > 0:
            print("  ⚠️  VALIDATION FAILED: Invalid embeddings detected!")
            print("  Pipeline will STOP. Fix issues before database ingestion.")
        else:
            print("  ✅ VALIDATION PASSED: All embeddings are valid.")
            print("  Ready for PostgreSQL/pgvector ingestion.")

        print("=" * 70)