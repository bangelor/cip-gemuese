# storage/azure_blob_storage.py
from azure.storage.blob import BlobServiceClient
from config.azure_config import AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME

class AzureBlobStorage:
    def __init__(self):
        # Load the connection string and container name from the config
        self.blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        self.container_client = self.blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

    def upload_data(self, file_name, data):
        """Upload data to Azure Blob Storage"""
        blob_client = self.container_client.get_blob_client(file_name)
        blob_client.upload_blob(data, overwrite=True)

# Usage example:
# storage = AzureBlobStorage()
# storage.upload_data('migros_data.json', json_data)
