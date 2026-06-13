"""Search Document Exporter Module.

Responsible for exporting processed AnimalDocument objects
to JSON format for downstream consumption.
"""

import json
from pathlib import Path

from src.models.animal_document import AnimalDocument


class SearchDocumentExporter:
    """Exports AnimalDocument objects to JSON files.

    Serializes selected fields from processed documents
    and writes them to the data/processed/ directory.
    """

    def __init__(self, output_path: str | Path) -> None:
        """Initialize SearchDocumentExporter with output file path.

        Args:
            output_path: Path to the output JSON file.
        """
        self.output_path = Path(output_path)

    def export(self, documents: list[AnimalDocument]) -> int:
        """Export a list of AnimalDocuments to JSON.

        Extracts selected fields from each document and writes
        them as a JSON array to the configured output path.

        Args:
            documents: List of AnimalDocument instances to export.

        Returns:
            Number of documents exported.
        """
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build export records with selected fields
        export_records: list[dict] = []
        for doc in documents:
            record = {
                "name": doc.name,
                "description": doc.description,
                "search_document": doc.search_document,
                "conservation_status": doc.conservation_status,
                "habitat": doc.habitat,
                "diet": doc.diet,
                "family": doc.family,
            }
            export_records.append(record)

        # Write JSON output
        with open(self.output_path, mode="w", encoding="utf-8") as f:
            json.dump(export_records, f, indent=2, ensure_ascii=False)

        return len(export_records)