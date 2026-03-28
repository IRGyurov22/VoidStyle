import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    weaviate_url: str
    weaviate_api_key: str
    inference_provider_api_key: str
    google_studio_api_key: str
    reset_collections: bool


def _to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_settings() -> Settings:
    load_dotenv()

    weaviate_url = os.getenv("WEAVIATE_URL", "").strip()
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY", "").strip()
    inference_provider_api_key = os.getenv("INFERENCE_PROVIDER_API_KEY", "").strip()
    google_studio_api_key = os.getenv("GOOGLE_STUDIO_API_KEY", "").strip()
    reset_collections = _to_bool(os.getenv("RESET_COLLECTIONS", "false"))
    missing = [
        name
        for name, value in [
            ("WEAVIATE_URL", weaviate_url),
            ("WEAVIATE_API_KEY", weaviate_api_key),
            ("INFERENCE_PROVIDER_API_KEY", inference_provider_api_key),
        ]
        if not value
    ]
    if missing:
        raise ValueError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return Settings(
        weaviate_url=weaviate_url,
        weaviate_api_key=weaviate_api_key,
        inference_provider_api_key=inference_provider_api_key,
        google_studio_api_key=google_studio_api_key,
        reset_collections=reset_collections,
    )
