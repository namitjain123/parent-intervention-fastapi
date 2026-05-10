import os
import uuid
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings

load_dotenv()


def get_blob_service_client():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING is missing")

    return BlobServiceClient.from_connection_string(connection_string)


def upload_file_to_blob(file_obj, filename: str, content_type: str = None) -> str:
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "episodes")

    unique_filename = f"{uuid.uuid4()}-{filename}"

    blob_service_client = get_blob_service_client()

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
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