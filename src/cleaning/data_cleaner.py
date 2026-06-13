"""Data Cleaner Module.

Responsible for normalizing, validating, and cleaning raw animal records
before further processing in the pipeline.
"""

from src.models.animal_document import AnimalDocument


class DataCleaner:
    """Cleans and normalizes raw AnimalDocument instances.

    Performs data quality operations including:
    - Field normalization (whitespace trimming, case normalization)
    - Null/empty value handling
    - Basic validation (required fields)
    - Deduplication by animal name
    """

    def __init__(self) -> None:
        """Initialize DataCleaner."""
        self._cleaned_count: int = 0
        self._dropped_count: int = 0

    @property
    def cleaned_count(self) -> int:
        """Number of records successfully cleaned."""
        return self._cleaned_count

    @property
    def dropped_count(self) -> int:
        """Number of records dropped during cleaning."""
        return self._dropped_count

    def clean_all(self, documents: list[AnimalDocument]) -> list[AnimalDocument]:
        """Apply all cleaning operations to a list of documents.

        Pipeline: normalize → validate → deduplicate

        Args:
            documents: List of raw AnimalDocument instances.

        Returns:
            List of cleaned and validated AnimalDocument instances.
        """
        self._cleaned_count = 0
        self._dropped_count = 0

        # Step 1: Normalize all fields
        normalized = [self.normalize_fields(doc) for doc in documents]

        # Step 2: Validate and filter
        validated: list[AnimalDocument] = []
        for doc in normalized:
            if self.validate(doc):
                validated.append(doc)
                self._cleaned_count += 1
            else:
                self._dropped_count += 1

        # Step 3: Deduplicate
        deduplicated = self.deduplicate(validated)
        self._dropped_count += len(validated) - len(deduplicated)

        return deduplicated

    def normalize_fields(self, document: AnimalDocument) -> AnimalDocument:
        """Normalize field values for a single document.

        Applies:
        - Whitespace stripping on all string fields
        - Replaces empty strings with None
        - Title-cases the animal name
        - Strips whitespace from list items

        Args:
            document: Raw AnimalDocument instance.

        Returns:
            AnimalDocument with normalized field values.
        """
        document.name = self._clean_string(document.name, title_case=True)
        document.height = self._clean_string(document.height)
        document.weight = self._clean_string(document.weight)
        document.color = self._clean_string(document.color)
        document.lifespan = self._clean_string(document.lifespan)
        document.diet = self._clean_string(document.diet)
        document.habitat = self._clean_string(document.habitat)
        document.average_speed = self._clean_string(document.average_speed)

        # Additional fields
        document.conservation_status = self._clean_string(document.conservation_status)
        document.family = self._clean_string(document.family)
        document.gestation_period = self._clean_string(document.gestation_period)
        document.top_speed = self._clean_string(document.top_speed)
        document.social_structure = self._clean_string(document.social_structure)
        document.offspring_per_birth = self._clean_string(document.offspring_per_birth)

        # Clean list fields
        document.predators = self._clean_list(document.predators)
        document.countries_found = self._clean_list(document.countries_found)

        return document

    def validate(self, document: AnimalDocument) -> bool:
        """Validate that a document meets minimum quality requirements.

        A document is valid if:
        - name is not None and not empty

        Args:
            document: AnimalDocument to validate.

        Returns:
            True if document passes validation, False otherwise.
        """
        if document.name is None or document.name.strip() == "":
            return False

        return True

    def deduplicate(self, documents: list[AnimalDocument]) -> list[AnimalDocument]:
        """Remove duplicate documents by animal name (case-insensitive).

        Keeps the first occurrence when duplicates are found.

        Args:
            documents: List of AnimalDocument instances.

        Returns:
            Deduplicated list of AnimalDocument instances.
        """
        seen_names: set[str] = set()
        unique_documents: list[AnimalDocument] = []

        for doc in documents:
            if doc.name is None:
                continue

            name_key = doc.name.strip().lower()
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_documents.append(doc)

        return unique_documents

    def _clean_string(self, value: str | None, title_case: bool = False) -> str | None:
        """Clean a single string value.

        Strips whitespace and converts empty strings to None.

        Args:
            value: String value to clean.
            title_case: If True, apply title case to the result.

        Returns:
            Cleaned string or None if empty.
        """
        if value is None:
            return None

        cleaned = value.strip()

        if cleaned == "" or cleaned.lower() in ("nan", "none", "null", "n/a", "-"):
            return None

        if title_case:
            cleaned = cleaned.title()

        return cleaned

    def _clean_list(self, values: list[str]) -> list[str]:
        """Clean a list of string values.

        Strips whitespace from each item and removes empty entries.

        Args:
            values: List of strings to clean.

        Returns:
            Cleaned list with empty values removed.
        """
        cleaned: list[str] = []
        for item in values:
            stripped = item.strip()
            if stripped and stripped.lower() not in ("nan", "none", "null", "n/a", "-"):
                cleaned.append(stripped)
        return cleaned