import weaviate
from weaviate.classes.init import Auth

from src.config import Settings


def connect(settings: Settings):
    google_key = settings.google_studio_api_key or settings.inference_provider_api_key
    headers = {
        "X-INFERENCE-PROVIDER-API-KEY": settings.inference_provider_api_key,
        "X-Goog-Studio-Api-Key": google_key,
    }

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=settings.weaviate_url,
        auth_credentials=Auth.api_key(settings.weaviate_api_key),
        headers=headers,
    )
    return client
