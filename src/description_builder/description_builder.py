"""Description Builder Module.

Responsible for generating natural language descriptions
from structured animal data fields.
"""

from src.models.animal_document import AnimalDocument


class DescriptionBuilder:
    """Generates human-readable natural language descriptions for animals.

    Takes structured data fields (name, diet, habitat, weight, top_speed,
    predators, countries_found, conservation_status, family, social_structure)
    and composes a coherent, descriptive paragraph suitable for
    semantic search indexing.
    """

    def __init__(self) -> None:
        """Initialize DescriptionBuilder."""
        pass

    def build_description(self, document: AnimalDocument) -> str:
        """Generate a natural language description for a single animal.

        Composes sentences from available structured fields, skipping
        any fields that are None or empty.

        Args:
            document: AnimalDocument with populated base fields.

        Returns:
            A natural language description string.
        """
        sentences: list[str] = []

        # Opening sentence with name and family
        sentences.append(self._build_identity_sentence(document))

        # Diet and habitat
        diet_habitat = self._build_diet_habitat_sentence(document)
        if diet_habitat:
            sentences.append(diet_habitat)

        # Physical attributes (weight, top speed)
        physical = self._build_physical_sentence(document)
        if physical:
            sentences.append(physical)

        # Social structure
        social = self._build_social_sentence(document)
        if social:
            sentences.append(social)

        # Predators
        predators = self._build_predators_sentence(document)
        if predators:
            sentences.append(predators)

        # Geographic range
        geography = self._build_geography_sentence(document)
        if geography:
            sentences.append(geography)

        # Conservation status
        conservation = self._build_conservation_sentence(document)
        if conservation:
            sentences.append(conservation)

        return " ".join(sentences)

    def build_descriptions(self, documents: list[AnimalDocument]) -> list[AnimalDocument]:
        """Generate descriptions for a batch of animal documents.

        Updates each document's `description` field in place.

        Args:
            documents: List of AnimalDocument instances.

        Returns:
            List of AnimalDocument instances with populated description field.
        """
        for doc in documents:
            doc.description = self.build_description(doc)
        return documents

    def _build_identity_sentence(self, document: AnimalDocument) -> str:
        """Build the opening identity sentence.

        Example: "The African Elephant belongs to the Elephantidae family."
        or: "The African Elephant is an animal."

        Args:
            document: AnimalDocument instance.

        Returns:
            Opening sentence string.
        """
        name = document.name or "Unknown animal"

        if document.family:
            return f"The {name} belongs to the {document.family} family."
        else:
            return f"The {name} is an animal."

    def _build_diet_habitat_sentence(self, document: AnimalDocument) -> str | None:
        """Build sentence about diet and habitat.

        Example: "It is a herbivore that lives in Savannah, Forest habitats."

        Args:
            document: AnimalDocument instance.

        Returns:
            Sentence string or None if no data available.
        """
        parts: list[str] = []

        if document.diet:
            article = self._get_article(document.diet.lower())
            parts.append(f"It is {article} {document.diet.lower()}")

        if document.habitat:
            if parts:
                parts.append(f"that lives in {document.habitat} habitats.")
            else:
                parts.append(f"It lives in {document.habitat} habitats.")
        elif parts:
            parts[0] += "."

        if not parts:
            return None

        return " ".join(parts)

    def _build_physical_sentence(self, document: AnimalDocument) -> str | None:
        """Build sentence about physical attributes (weight, top speed).

        Example: "It weighs approximately 2700-6000 kg and can reach a top speed of 40 km/h."

        Args:
            document: AnimalDocument instance.

        Returns:
            Sentence string or None if no data available.
        """
        parts: list[str] = []

        if document.weight:
            parts.append(f"weighs approximately {document.weight} kg")

        if document.top_speed:
            parts.append(f"can reach a top speed of {document.top_speed} km/h")

        if not parts:
            return None

        return "It " + " and ".join(parts) + "."

    def _build_social_sentence(self, document: AnimalDocument) -> str | None:
        """Build sentence about social structure.

        Example: "It has a herd-based social structure."

        Args:
            document: AnimalDocument instance.

        Returns:
            Sentence string or None if no data available.
        """
        if not document.social_structure:
            return None

        return f"It has a {document.social_structure.lower()} social structure."

    def _build_predators_sentence(self, document: AnimalDocument) -> str | None:
        """Build sentence about predators.

        Example: "Its natural predators include Lions and Hyenas."

        Args:
            document: AnimalDocument instance.

        Returns:
            Sentence string or None if no data available.
        """
        if not document.predators:
            return None

        if len(document.predators) == 1:
            return f"Its natural predator is the {document.predators[0]}."
        elif len(document.predators) == 2:
            predator_str = f"{document.predators[0]} and {document.predators[1]}"
        else:
            predator_str = ", ".join(document.predators[:-1]) + f", and {document.predators[-1]}"

        return f"Its natural predators include {predator_str}."

    def _build_geography_sentence(self, document: AnimalDocument) -> str | None:
        """Build sentence about geographic range.

        Example: "It is found in Africa."

        Args:
            document: AnimalDocument instance.

        Returns:
            Sentence string or None if no data available.
        """
        if not document.countries_found:
            return None

        if len(document.countries_found) == 1:
            return f"It is found in {document.countries_found[0]}."
        elif len(document.countries_found) == 2:
            location_str = f"{document.countries_found[0]} and {document.countries_found[1]}"
        else:
            location_str = ", ".join(document.countries_found[:-1]) + f", and {document.countries_found[-1]}"

        return f"It is found in {location_str}."

    def _build_conservation_sentence(self, document: AnimalDocument) -> str | None:
        """Build sentence about conservation status.

        Example: "Its conservation status is Vulnerable."

        Args:
            document: AnimalDocument instance.

        Returns:
            Sentence string or None if no data available.
        """
        if not document.conservation_status:
            return None

        return f"Its conservation status is {document.conservation_status}."

    def _get_article(self, word: str) -> str:
        """Get the correct indefinite article ('a' or 'an') for a word.

        Args:
            word: The word that follows the article.

        Returns:
            'an' if word starts with a vowel sound, 'a' otherwise.
        """
        if not word:
            return "a"

        vowels = ("a", "e", "i", "o", "u")
        return "an" if word[0].lower() in vowels else "a"