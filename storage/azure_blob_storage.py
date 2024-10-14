from azure.storage.blob import BlobClient
from config.azure_config import ADLSG2_ACCOUNT_URL, ADLSG2_CONTAINER_NAME, ADLSG2_SAS_TOKEN
from datetime import datetime

class AzureBlobStorage:
    def __init__(self):
        """Initialize the BlobClient for ADLS Gen2 using the SAS token."""
        # Combine the account URL and container name
        self.base_url = f"{ADLSG2_ACCOUNT_URL}/{ADLSG2_CONTAINER_NAME}"

    def get_blob_client(self, blob_name):
        """Create a BlobClient for a specific blob using the SAS token."""
        # Ensure the SAS token has a leading '?' if it's missing
        sas_token = f"?{ADLSG2_SAS_TOKEN}" if not ADLSG2_SAS_TOKEN.startswith("?") else ADLSG2_SAS_TOKEN
        blob_url = f"{self.base_url}/{blob_name}{sas_token}"
        return BlobClient.from_blob_url(blob_url)

    def get_time_stamped_path(self):
        """Generate a time-stamped file path based on the current date and time."""
        # Get current date and time
        now = datetime.now()
        # Format as Year/Month/Day/HH:MM:ss
        timestamp = now.strftime("%Y/%m/%d/%H%M%S")
        # Return the timestamp part of the path
        return f"{timestamp}.json"

    def upload_data(self, store_name, data):
        """Upload data to the blob using a store-specific, time-stamped path."""
        # Generate the time-stamped path (without the store name)
        timestamped_path = self.get_time_stamped_path()
        # Combine the store name with the timestamped path
        file_name = f"{store_name}/{timestamped_path}"

        # Create the blob client for the generated file path
        blob_client = self.get_blob_client(file_name)

        try:
            # Upload the blob data
            blob_client.upload_blob(data, overwrite=True)
            print(f"Successfully uploaded {file_name} to ADLS Gen2.")
        except Exception as e:
            print(f"Failed to upload {file_name} to ADLS Gen2: {e}")

# Usage Example
# storage = AzureBlobStorage()
# storage.upload_data('migros', json_data)
