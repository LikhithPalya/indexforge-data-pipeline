"""Search Document Builder Module.

Responsible for composing the final searchable text document
from the generated description and other enrichment sources.
"""

from src.models.animal_document import AnimalDocument


class SearchDocumentBuilder:
    """Builds composite search documents for semantic search indexing.

    For V1, the search_document is set directly from the generated description.
    In future versions, this will combine description + wikipedia_summary
    and potentially other enrichment sources.
    """

    def __init__(self) -> None:
        """Initialize SearchDocumentBuilder."""
        pass

    def build_search_document(self, document: AnimalDocument) -> str:
        """Build a search document for a single AnimalDocument.

        For V1, the search_document equals the description field.

        Args:
            document: AnimalDocument with populated description field.

        Returns:
            Composite search document text.

        Raises:
            ValueError: If description is None or empty.
        """
        if not document.description:
            raise ValueError(
                f"Cannot build search document for '{document.name}': description is empty."
            )

        # V1: search_document = description
        # Future: combine description + wikipedia_summary + additional metadata
        return document.description

    def build_search_documents(self, documents: list[AnimalDocument]) -> list[AnimalDocument]:
        """Build search documents for a batch of AnimalDocuments.

        Updates each document's `search_document` field in place.

        Args:
            documents: List of AnimalDocument instances with populated description fields.

        Returns:
            List of AnimalDocument instances with populated search_document fields.
        """
        for doc in documents:
            try:
                doc.search_document = self.build_search_document(doc)
            except ValueError:
                # Skip documents without descriptions
                doc.search_document = None

        return documents