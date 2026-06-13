"""Main entrypoint for IndexForge Data Pipeline.

Loads a CSV file from data/raw/, cleans the records,
generates descriptions, enriches with Wikipedia, builds search documents,
exports to JSON, generates embeddings, validates embeddings, and runs
retrieval evaluation.
"""

import logging
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.dataset_reader import DatasetReader
from src.cleaning.data_cleaner import DataCleaner
from src.description_builder.description_builder import DescriptionBuilder
from src.enrichment.wikipedia_enrichment_service import WikipediaEnrichmentService
from src.pipeline.search_document_builder import SearchDocumentBuilder
from src.export.search_document_exporter import SearchDocumentExporter
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.validation.embedding_validator import EmbeddingValidator
from src.embeddings.similarity_tester import SimilarityTester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    """Run the full IndexForge Data Pipeline."""
    raw_data_dir = Path("data/raw")
    output_path = Path("data/processed/animals_search_documents.json")

    print("=" * 70)
    print("IndexForge Data Pipeline - Full Pipeline Run")
    print("=" * 70)

    # Stage 1: Ingestion
    print("\n[Stage 1] Reading dataset...")
    reader = DatasetReader(data_dir=raw_data_dir)
    documents = reader.read_all()
    print(f"  → Loaded {len(documents)} raw records")

    # Stage 2: Cleaning
    print("\n[Stage 2] Cleaning records...")
    cleaner = DataCleaner()
    cleaned_documents = cleaner.clean_all(documents)
    print(f"  → Cleaned: {cleaner.cleaned_count} records")
    print(f"  → Dropped: {cleaner.dropped_count} records")
    print(f"  → Final:   {len(cleaned_documents)} records")

    # Stage 3: Description Generation
    print("\n[Stage 3] Generating descriptions...")
    description_builder = DescriptionBuilder()
    described_documents = description_builder.build_descriptions(cleaned_documents)
    docs_with_desc = sum(1 for d in described_documents if d.description)
    print(f"  → Generated {docs_with_desc} descriptions")

    # Stage 4: Wikipedia Enrichment
    print("\n[Stage 4] Wikipedia enrichment...")
    enrichment_service = WikipediaEnrichmentService()
    enriched_documents = enrichment_service.enrich_batch(described_documents)
    print(f"  → Enriched: {enrichment_service.enriched_count} animals")
    print(f"  → Failed:   {enrichment_service.failed_count} animals")

    # Show example enrichment for Tiger
    tiger = next((d for d in enriched_documents if d.name and "tiger" == d.name.lower()), None)
    if tiger and tiger.wikipedia_summary:
        print(f"\n  Example (Tiger) Wikipedia Summary:")
        print(f"  {tiger.wikipedia_summary[:200]}...")

    # Stage 5: Search Document Creation
    print("\n[Stage 5] Building search documents...")
    search_builder = SearchDocumentBuilder()
    final_documents = search_builder.build_search_documents(enriched_documents)
    docs_with_search = sum(1 for d in final_documents if d.search_document)
    print(f"  → Built {docs_with_search} search documents")

    # Stage 6: Export to JSON
    print("\n[Stage 6] Exporting search documents...")
    exporter = SearchDocumentExporter(output_path=output_path)
    exported_count = exporter.export(final_documents)
    print(f"  → Exported {exported_count} search documents to {output_path}")

    # Stage 7: Embedding Generation
    print("\n[Stage 7] Generating embeddings...")
    embedding_generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    embedded_documents = embedding_generator.generate_embeddings(final_documents)
    docs_with_embedding = sum(1 for d in embedded_documents if d.has_embedding())
    print(f"  → Generated {docs_with_embedding} embeddings")
    print(f"  → Embedding dimension: {EmbeddingGenerator.EXPECTED_DIMENSION}")

    # Stage 8: Embedding Validation (quality gate)
    print("\n[Stage 8] Embedding Validation...")
    validator = EmbeddingValidator()
    report = validator.validate(embedded_documents)
    validator.print_report(report)

    # STOP pipeline if invalid embeddings detected
    if report.invalid_embeddings > 0:
        print("\n❌ Pipeline STOPPED: Fix invalid embeddings before database ingestion.")
        sys.exit(1)

    # Stage 9: Retrieval Evaluation
    print("\n[Stage 9] Running retrieval evaluation...")
    similarity_tester = SimilarityTester(embedding_generator=embedding_generator)

    # --- Section 1: Query-based retrieval ---
    demo_results = similarity_tester.run_demo(embedded_documents)

    print("\n" + "=" * 70)
    print("SECTION 1: Query-Based Retrieval (Top 10)")
    print("=" * 70)

    for query, matches in demo_results.items():
        print(f"\n  Query: \"{query}\"")
        print(f"  {'─' * 50}")
        for rank, (name, score) in enumerate(matches, start=1):
            print(f"    {rank:>2}. {name} ({score:.4f})")

    # --- Section 2: Nearest neighbor evaluation ---
    neighbor_results = similarity_tester.run_neighbor_evaluation(embedded_documents)

    print("\n" + "=" * 70)
    print("SECTION 2: Nearest Neighbor Evaluation (Top 5)")
    print("=" * 70)

    for animal_name, neighbors in neighbor_results.items():
        print(f"\n  Animal: {animal_name}")
        print(f"  Nearest Neighbors:")
        print(f"  {'─' * 50}")
        if not neighbors:
            print(f"    (not found in dataset)")
        else:
            for rank, (name, score) in enumerate(neighbors, start=1):
                print(f"    {rank}. {name} ({score:.4f})")

    print("\n" + "=" * 70)
    print("Pipeline complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()