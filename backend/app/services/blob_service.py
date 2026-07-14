import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.core.config import settings


def get_blob_service_client():
    if not settings.AZURE_STORAGE_CONNECTION_STRING:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING is missing")

    return BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)


def upload_file_to_blob(file_obj, filename: str, content_type: str = None) -> str:
    unique_filename = f"{uuid.uuid4()}-{filename}"

    blob_service_client = get_blob_service_client()

    blob_client = blob_service_client.get_blob_client(
        container=settings.AZURE_STORAGE_CONTAINER_NAME,
        blob=unique_filename
    )

    blob_client.upload_blob(
        file_obj,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type)
        if content_type
        else None
    )

    return blob_client.url
