"""Task 1: Download inputs from Azure. Task 7: Upload outputs back to Azure."""
import io
import logging
import os
from dotenv import load_dotenv
from pathlib import Path

import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
 
load_dotenv()

ACCOUNT_URL = os.getenv("ACCOUNT_URL", "https://c55data.blob.core.windows.net")
SOURCE_CONTAINER = os.getenv("SOURCE_CONTAINER","week4-inputs")
FILES = ["messy_sales.csv", "messy_customers.csv"]


def download_inputs(data_dir: Path) -> None:
    """Task 1: Download input CSV files from Azure Blob Storage."""
    # TODO: Create a BlobServiceClient using DefaultAzureCredential and ACCOUNT_URL.
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=ACCOUNT_URL, credential=credential) 
    # TODO: Get a container client for SOURCE_CONTAINER.
    container_client = blob_service_client.get_container_client(SOURCE_CONTAINER)
    # TODO: For each filename in FILES, download the blob and write it to data_dir/<filename>.
    data_dir.mkdir(parents=True, exist_ok=True)
    
    for name in FILES:
        blob = container_client.get_blob_client(name)
        with open(f"{data_dir}/{name}", "wb") as f:
             f.write(blob.download_blob().readall())

    # TODO: Log a message for each downloaded file.
    for filename in FILES:
        logging.info("Downloaded %s", filename)


def upload_outputs(output_dir: Path, github_username: str) -> None:
    """Task 7 (extra credit): Upload Parquet outputs to Azure and verify the round-trip."""
    container_name = f"week4-{github_username}"

    # EXTRA CREDIT — implement this after Tasks 2–6 are working.
    # TODO: Create a BlobServiceClient using DefaultAzureCredential and ACCOUNT_URL.
    # TODO: Get (or create) the container named container_name.
    # TODO: Upload every .parquet file in output_dir to the container.
    # TODO: Download customer_summary.parquet back and assert its row count matches the local file.
    # TODO: Log the container name and number of files uploaded.
    account_url = ACCOUNT_URL
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()
    parquet_files = list(output_dir.glob("*.parquet"))
    for parquet_file in parquet_files:
        blob_client = container_client.get_blob_client(parquet_file.name)
        with open(parquet_file, "rb") as f:
            blob_client.upload_blob(f, overwrite=True)
    logging.info("Uploaded %d files to container %s", len(parquet_files), container_name)
    # Verify round-trip for customer_summary.parquet
    local_file = output_dir / "customer_summary.parquet"
    blob_client = container_client.get_blob_client(local_file.name)
    downloaded_data = blob_client.download_blob().readall()
    downloaded_df = pd.read_parquet(io.BytesIO(downloaded_data))
    local_df = pd.read_parquet(local_file)
    assert len(downloaded_df) == len(local_df), "Row count mismatch after round-trip"
    logging.info("Round-trip verification successful for customer_summary.parquet") 
    
