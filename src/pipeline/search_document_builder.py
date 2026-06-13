"""Search Document Builder Module.

Responsible for composing the final searchable text document
from the generated description and Wikipedia enrichment.
"""

from src.models.animal_document import AnimalDocument


class SearchDocumentBuilder:
    """Builds composite search documents for semantic search indexing.

    Combines the generated description with the Wikipedia summary
    (if available) into a unified search_document field.
    """

    def __init__(self) -> None:
        """Initialize SearchDocumentBuilder."""
        pass

    def build_search_document(self, document: AnimalDocument) -> str:
        """Build a search document for a single AnimalDocument.

        Combines description + Wikipedia summary if available.
        Format:
            {description}

            Wikipedia Summary:
            {wikipedia_summary}

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

        # Start with description
        search_doc = document.description

        # Append Wikipedia summary if available
        if document.wikipedia_summary and document.wikipedia_summary.strip():
            search_doc += "\n\nWikipedia Summary:\n" + document.wikipedia_summary

        return search_doc

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