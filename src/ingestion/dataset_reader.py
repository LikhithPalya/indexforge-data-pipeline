"""Dataset Reader Module.

Responsible for reading and parsing raw animal dataset files
from CSV format into AnimalDocument instances.
"""

import csv
from pathlib import Path
from typing import Any

from src.models.animal_document import AnimalDocument


# Mapping of possible CSV column names to AnimalDocument field names
COLUMN_ALIASES: dict[str, str] = {
    "animal": "name",
    "name": "name",
    "height": "height",
    "height (cm)": "height",
    "height_cm": "height",
    "weight": "weight",
    "weight (kg)": "weight",
    "weight_kg": "weight",
    "color": "color",
    "colour": "color",
    "lifespan": "lifespan",
    "lifespan (years)": "lifespan",
    "lifespan_years": "lifespan",
    "diet": "diet",
    "habitat": "habitat",
    "predators": "predators",
    "average speed": "average_speed",
    "average speed (km/h)": "average_speed",
    "average_speed": "average_speed",
    "average_speed_kmh": "average_speed",
    "countries found": "countries_found",
    "countries_found": "countries_found",
    "conservation status": "conservation_status",
    "conservation_status": "conservation_status",
    "family": "family",
    "gestation period": "gestation_period",
    "gestation period (days)": "gestation_period",
    "gestation_period": "gestation_period",
    "top speed": "top_speed",
    "top speed (km/h)": "top_speed",
    "top_speed": "top_speed",
    "social structure": "social_structure",
    "social_structure": "social_structure",
    "offspring per birth": "offspring_per_birth",
    "offspring_per_birth": "offspring_per_birth",
}


class DatasetReader:
    """Reads raw animal data files and parses them into AnimalDocument instances.

    Supports CSV file format. Handles file discovery, parsing,
    and mapping of raw records to AnimalDocument objects.
    Automatically resolves common column name variations.
    """

    def __init__(self, data_dir: str | Path) -> None:
        """Initialize DatasetReader with the path to raw data directory.

        Args:
            data_dir: Path to the directory containing raw dataset files.

        Raises:
            FileNotFoundError: If the data directory does not exist.
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

    def read_all(self) -> list[AnimalDocument]:
        """Read all CSV dataset files from the data directory.

        Returns:
            List of AnimalDocument instances parsed from all CSV files.

        Raises:
            ValueError: If no CSV files are found in the directory.
        """
        csv_files = list(self.data_dir.glob("*.csv"))
        if not csv_files:
            raise ValueError(f"No CSV files found in: {self.data_dir}")

        documents: list[AnimalDocument] = []
        for file_path in csv_files:
            raw_records = self.read_csv(file_path)
            for record in raw_records:
                document = self._map_to_document(record)
                documents.append(document)

        return documents

    def read_csv(self, file_path: Path) -> list[dict[str, Any]]:
        """Read a single CSV file and return raw records.

        Args:
            file_path: Path to the CSV file.

        Returns:
            List of dictionaries representing raw records.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        records: list[dict[str, Any]] = []
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))

        return records

    def _map_to_document(self, raw_record: dict[str, Any]) -> AnimalDocument:
        """Map a raw dictionary record to an AnimalDocument instance.

        Handles column name resolution using COLUMN_ALIASES and
        parses list fields (predators, countries_found) from delimited strings.

        Args:
            raw_record: Dictionary containing raw field values from CSV.

        Returns:
            AnimalDocument with populated base fields.
        """
        # Resolve column names using aliases
        resolved: dict[str, Any] = {}
        for raw_key, value in raw_record.items():
            normalized_key = raw_key.strip().lower()
            mapped_field = COLUMN_ALIASES.get(normalized_key)
            if mapped_field:
                resolved[mapped_field] = value

        return AnimalDocument(
            name=resolved.get("name"),
            height=resolved.get("height"),
            weight=resolved.get("weight"),
            color=resolved.get("color"),
            lifespan=resolved.get("lifespan"),
            diet=resolved.get("diet"),
            habitat=resolved.get("habitat"),
            predators=self._parse_list_field(resolved.get("predators")),
            average_speed=resolved.get("average_speed"),
            countries_found=self._parse_list_field(resolved.get("countries_found")),
            conservation_status=resolved.get("conservation_status"),
            family=resolved.get("family"),
            gestation_period=resolved.get("gestation_period"),
            top_speed=resolved.get("top_speed"),
            social_structure=resolved.get("social_structure"),
            offspring_per_birth=resolved.get("offspring_per_birth"),
        )

    def _parse_list_field(self, value: Any) -> list[str]:
        """Parse a comma-separated string into a list of strings.

        Args:
            value: Raw field value, expected to be a comma-separated string.

        Returns:
            List of stripped, non-empty strings.
        """
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if not isinstance(value, str) or value.strip() == "":
            return []

        return [item.strip() for item in value.split(",") if item.strip()]