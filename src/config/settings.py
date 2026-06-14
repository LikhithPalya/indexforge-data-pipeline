"""Settings Module.

Centralized application configuration loaded from environment variables.
Uses python-dotenv for .env file support.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# Load .env file from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")


class Settings:
    """Application configuration settings.

    Loads configuration from environment variables with sensible defaults.
    All pipeline components should receive their configuration from this class.
    """

    def __init__(self) -> None:
        """Initialize Settings by loading from environment variables."""
        pass

    # --- Database Configuration ---

    @property
    def database_host(self) -> str:
        """PostgreSQL host."""
        return os.getenv("DATABASE_HOST", "localhost")

    @property
    def database_port(self) -> int:
        """PostgreSQL port."""
        return int(os.getenv("DATABASE_PORT", "5432"))

    @property
    def database_name(self) -> str:
        """PostgreSQL database name."""
        return os.getenv("DATABASE_NAME", "indexforge")

    @property
    def database_user(self) -> str:
        """PostgreSQL user."""
        return os.getenv("DATABASE_USER", "postgres")

    @property
    def database_password(self) -> str:
        """PostgreSQL password."""
        return os.getenv("DATABASE_PASSWORD", "postgres")

    @property
    def database_url(self) -> str:
        """PostgreSQL connection string."""
        return os.getenv(
            "DATABASE_URL",
            f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}",
        )

    @property
    def database_pool_size(self) -> int:
        """Database connection pool size."""
        return int(os.getenv("DATABASE_POOL_SIZE", "5"))

    # --- Wikipedia Enrichment Configuration ---

    @property
    def wikipedia_api_base_url(self) -> str:
        """Wikipedia REST API base URL."""
        return os.getenv("WIKIPEDIA_API_BASE_URL", "https://en.wikipedia.org/api/rest_v1")

    @property
    def wikipedia_request_timeout(self) -> int:
        """HTTP request timeout for Wikipedia API calls in seconds."""
        return int(os.getenv("WIKIPEDIA_REQUEST_TIMEOUT", "30"))

    @property
    def wikipedia_rate_limit_delay(self) -> float:
        """Delay between Wikipedia API requests in seconds."""
        return float(os.getenv("WIKIPEDIA_RATE_LIMIT_DELAY", "1.0"))

    # --- Embedding Configuration ---

    @property
    def embedding_model_name(self) -> str:
        """Sentence-transformer model name."""
        return os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    @property
    def embedding_batch_size(self) -> int:
        """Batch size for embedding generation."""
        return int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

    # --- Pipeline Configuration ---

    @property
    def pipeline_batch_size(self) -> int:
        """Batch size for pipeline processing."""
        return int(os.getenv("PIPELINE_BATCH_SIZE", "100"))

    @property
    def pipeline_max_retries(self) -> int:
        """Maximum retry attempts for failed pipeline stages."""
        return int(os.getenv("PIPELINE_MAX_RETRIES", "3"))

    # --- Data Path Configuration ---

    @property
    def raw_data_dir(self) -> str:
        """Path to raw data directory."""
        return os.getenv("RAW_DATA_DIR", "data/raw")

    @property
    def processed_data_dir(self) -> str:
        """Path to processed data directory."""
        return os.getenv("PROCESSED_DATA_DIR", "data/processed")

    @property
    def enriched_data_dir(self) -> str:
        """Path to enriched data directory."""
        return os.getenv("ENRICHED_DATA_DIR", "data/enriched")

    # --- Logging Configuration ---

    @property
    def log_level(self) -> str:
        """Logging level."""
        return os.getenv("LOG_LEVEL", "INFO")