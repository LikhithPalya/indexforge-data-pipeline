"""Main entrypoint for IndexForge Data Pipeline.

Loads a CSV file from data/raw/, cleans the records,
generates descriptions, builds search documents,
exports to JSON, and prints the first 5 search documents.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.dataset_reader import DatasetReader
from src.cleaning.data_cleaner import DataCleaner
from src.description_builder.description_builder import DescriptionBuilder
from src.pipeline.search_document_builder import SearchDocumentBuilder
from src.export.search_document_exporter import SearchDocumentExporter


def main() -> None:
    """Load CSV data, clean, generate descriptions, build search docs, export, and print results."""
    raw_data_dir = Path("data/raw")
    output_path = Path("data/processed/animals_search_documents.json")

    print("=" * 70)
    print("IndexForge Data Pipeline - Ingestion, Cleaning & Description")
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

    # Stage 4: Search Document Creation
    print("\n[Stage 4] Building search documents...")
    search_builder = SearchDocumentBuilder()
    final_documents = search_builder.build_search_documents(described_documents)
    docs_with_search = sum(1 for d in final_documents if d.search_document)
    print(f"  → Built {docs_with_search} search documents")

    # Stage 5: Export to JSON
    print("\n[Stage 5] Exporting search documents...")
    exporter = SearchDocumentExporter(output_path=output_path)
    exported_count = exporter.export(final_documents)
    print(f"  → Exported {exported_count} search documents to {output_path}")

    # Print first 5 search documents
    print("\n" + "=" * 70)
    print("First 5 Search Documents:")
    print("=" * 70)

    for i, doc in enumerate(final_documents[:5], start=1):
        print(f"\n{'─' * 70}")
        print(f"  [{i}] {doc.name}")
        print(f"{'─' * 70}")
        print(f"  {doc.search_document}")

    print("\n" + "=" * 70)
    print("Pipeline complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()