"""Description Builder Module.

Responsible for generating natural language descriptions
from structured animal data fields.
"""

from src.models.animal_document import AnimalDocument


class DescriptionBuilder:
    """Generates human-readable natural language descriptions for animals.

    Takes structured data fields (height, weight, habitat, diet, etc.)
    and composes a coherent, descriptive paragraph suitable for
    semantic search indexing.
    """

    # TODO: Define description templates
    # TODO: Consider LLM-assisted generation as an alternative
    # TODO: Add configurable description length limits

    def __init__(self) -> None:
        """Initialize DescriptionBuilder with default templates."""
        # TODO: Load description templates
        # TODO: Configure max description length
        pass

    def build_description(self, document: AnimalDocument) -> str:
        """Generate a natural language description for a single animal.

        Args:
            document: AnimalDocument with populated base fields.

        Returns:
            A natural language description string.
        """
        # TODO: Compose description from structured fields
        # TODO: Handle missing fields gracefully
        # TODO: Ensure grammatically correct output
        raise NotImplementedError("DescriptionBuilder.build_description() not yet implemented")

    def build_descriptions(self, documents: list[AnimalDocument]) -> list[AnimalDocument]:
        """Generate descriptions for a batch of animal documents.

        Updates each document's `description` field in place.

        Args:
            documents: List of AnimalDocument instances.

        Returns:
            List of AnimalDocument instances with populated description field.
        """
        # TODO: Iterate over documents and build descriptions
        # TODO: Handle errors for individual documents without failing batch
        # TODO: Log progress for large batches
        raise NotImplementedError("DescriptionBuilder.build_descriptions() not yet implemented")

    def _format_physical_attributes(self, document: AnimalDocument) -> str:
        """Format physical attributes (height, weight, color, speed) into text.

        Args:
            document: AnimalDocument instance.

        Returns:
            Formatted string describing physical attributes.
        """
        # TODO: Build sentence fragments for available physical fields
        # TODO: Skip None/empty fields
        raise NotImplementedError("DescriptionBuilder._format_physical_attributes() not yet implemented")

    def _format_ecological_info(self, document: AnimalDocument) -> str:
        """Format ecological information (habitat, diet, predators) into text.

        Args:
            document: AnimalDocument instance.

        Returns:
            Formatted string describing ecological information.
        """
        # TODO: Build sentence fragments for habitat, diet, predators
        # TODO: Handle list fields (predators, countries_found)
        raise NotImplementedError("DescriptionBuilder._format_ecological_info() not yet implemented")