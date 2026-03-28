import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()

def get_blob_service_client():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING is missing")

    return BlobServiceClient.from_connection_string(connection_string)


def upload_audio_file(file_obj, filename: str) -> str:
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "episodes")

    blob_service_client = get_blob_service_client()
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=filename
    )

    blob_client.upload_blob(file_obj, overwrite=True)

    return blob_client.url