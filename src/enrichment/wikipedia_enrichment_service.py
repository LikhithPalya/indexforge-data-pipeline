"""Wikipedia Enrichment Service Module.

Responsible for enriching animal documents with summary information
fetched from the Wikipedia REST API.
"""

import json
import logging
import re
import time
import urllib.parse
import urllib.request

from src.models.animal_document import AnimalDocument

logger = logging.getLogger(__name__)

WIKIPEDIA_API_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary"
MAX_SUMMARY_LENGTH = 500
REQUEST_DELAY = 0.3  # 300ms between requests to avoid rate limiting
MAX_RETRIES = 2
RETRY_BACKOFF = 1.0  # seconds to wait on 429 before retrying


class WikipediaEnrichmentService:
    """Fetches and attaches Wikipedia summaries to animal documents.

    Queries the Wikipedia REST API to retrieve article summaries
    for each animal. Handles rate limiting, retries, and errors gracefully.
    """

    def __init__(
        self,
        base_url: str = WIKIPEDIA_API_BASE,
        delay: float = REQUEST_DELAY,
        max_summary_length: int = MAX_SUMMARY_LENGTH,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        """Initialize WikipediaEnrichmentService.

        Args:
            base_url: Wikipedia REST API base URL for page summaries.
            delay: Delay between API requests in seconds.
            max_summary_length: Maximum character length for summaries.
            max_retries: Maximum number of retries on rate-limit (429) errors.
        """
        self.base_url = base_url
        self.delay = delay
        self.max_summary_length = max_summary_length
        self.max_retries = max_retries
        self._enriched_count = 0
        self._failed_count = 0

    @property
    def enriched_count(self) -> int:
        """Number of animals successfully enriched."""
        return self._enriched_count

    @property
    def failed_count(self) -> int:
        """Number of animals that failed enrichment."""
        return self._failed_count

    def enrich(self, animal: AnimalDocument) -> AnimalDocument:
        """Enrich a single document with its Wikipedia summary.

        Tries multiple title variations to maximize lookup success.

        Args:
            animal: AnimalDocument to enrich.

        Returns:
            AnimalDocument with populated wikipedia_summary field (or None on failure).
        """
        if not animal.name:
            return animal

        # Try Wikipedia API with multiple title variations
        titles_to_try = self._generate_title_variations(animal.name)
        for title in titles_to_try:
            summary = self._fetch_summary(title)
            if summary:
                animal.wikipedia_summary = self._truncate_summary(summary)
                return animal

        return animal

    def enrich_batch(self, animals: list[AnimalDocument]) -> list[AnimalDocument]:
        """Enrich a batch of documents with Wikipedia summaries.

        Args:
            animals: List of AnimalDocument instances.

        Returns:
            List of AnimalDocument instances with populated wikipedia_summary fields.
        """
        self._enriched_count = 0
        self._failed_count = 0
        total = len(animals)

        logger.info(f"Starting Wikipedia enrichment for {total} animals...")

        for i, animal in enumerate(animals, start=1):
            self.enrich(animal)

            if animal.wikipedia_summary:
                self._enriched_count += 1
            else:
                self._failed_count += 1

            # Log progress every 25 animals
            if i % 25 == 0:
                logger.info(f"  Progress: {i}/{total} processed ({self._enriched_count} enriched)")

            # Polite delay between requests
            if i < total:
                time.sleep(self.delay)

        logger.info(
            f"Wikipedia enrichment complete. "
            f"Enriched: {self._enriched_count}, Failed: {self._failed_count}"
        )

        return animals

    def _generate_title_variations(self, name: str) -> list[str]:
        """Generate multiple title variations to try for Wikipedia lookup.

        Handles common issues:
        - Title case apostrophe issues (e.g., "Baird'S Tapir" -> "Baird's tapir")
        - Parenthetical text removal

        Args:
            name: Original animal name.

        Returns:
            List of title strings to attempt, in priority order.
        """
        variations: list[str] = []

        # 1. Original name as-is
        variations.append(name)

        # 2. Fix apostrophe casing issue (Title Case makes 's -> 'S)
        fixed_apostrophe = re.sub(r"'S\b", "'s", name)
        if fixed_apostrophe != name:
            variations.append(fixed_apostrophe)

        # 3. Remove parenthetical text
        no_parens = re.sub(r"\s*\([^)]*\)", "", name).strip()
        if no_parens != name:
            variations.append(no_parens)

        # 4. Try lowercase except first word (more natural Wikipedia title)
        words = name.split()
        if len(words) > 1:
            natural_title = words[0] + " " + " ".join(w.lower() for w in words[1:])
            natural_title = re.sub(r"'s\b", "'s", natural_title)
            if natural_title not in variations:
                variations.append(natural_title)

        return variations

    def _fetch_summary(self, title: str) -> str | None:
        """Fetch the Wikipedia summary for a given title with retry on 429.

        Args:
            title: Title to search for on Wikipedia.

        Returns:
            Summary extract text if found, None otherwise.
        """
        encoded_title = urllib.parse.quote(title.replace(" ", "_"), safe="")
        url = f"{self.base_url}/{encoded_title}"

        for attempt in range(self.max_retries + 1):
            try:
                request = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "IndexForge-DataPipeline/1.0 (educational project)",
                        "Accept": "application/json",
                    },
                )
                with urllib.request.urlopen(request, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode("utf-8"))
                        extract = data.get("extract")
                        if extract:
                            return extract
                        return None
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    logger.debug(f"Wikipedia article not found: {title}")
                    return None
                elif e.code == 429:
                    if attempt < self.max_retries:
                        wait_time = RETRY_BACKOFF * (attempt + 1)
                        logger.debug(f"Rate limited for '{title}', waiting {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"Rate limited for '{title}' after {self.max_retries} retries")
                        return None
                else:
                    logger.warning(f"Wikipedia HTTP error for '{title}': {e.code}")
                    return None
            except urllib.error.URLError as e:
                logger.warning(f"Wikipedia network error for '{title}': {e.reason}")
                return None
            except Exception as e:
                logger.warning(f"Wikipedia unexpected error for '{title}': {e}")
                return None

        return None

    def _truncate_summary(self, summary: str) -> str:
        """Truncate summary to approximately 2-3 sentences or max_summary_length chars.

        Args:
            summary: Full summary text.

        Returns:
            Truncated summary text.
        """
        if len(summary) <= self.max_summary_length:
            return summary

        truncated = summary[:self.max_summary_length]
        last_period = truncated.rfind(".")
        if last_period > self.max_summary_length * 0.5:
            return truncated[:last_period + 1]

        return truncated + "..."