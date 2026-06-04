"""
Week 5 assignment: containerised data pipeline.

Tasks:
- Task 1: confirm this script runs locally before touching the Dockerfile.
- Task 5: read all configuration from environment variables (no hardcoded values).

Replace every `raise NotImplementedError` below with a real implementation.
"""

import logging
import os
from pathlib import Path
DATA_DIR = Path("data")

from src.ingest import download_inputs, upload_outputs
from src.clean import load_and_explore, clean_sales
from src.transform import join_customers
from src.report import build_reports, write_outputs

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def get_config() -> dict:
    """
    Return configuration read from environment variables.

    Required variable: API_KEY
    Optional variable: OUTPUT_DIR (default "output")

    Raise RuntimeError with a clear message if a required variable is missing.
    """
    api_key = os.getenv("API_KEY")
    if api_key is None:
        raise RuntimeError("Missing required environment variable: API_KEY")
    output_dir = os.getenv("OUTPUT_DIR", "output")
    return {"api_key": api_key, "output_dir": output_dir}
  


def fetch_data(api_key: str) -> list[dict]:
    """
    Simulate fetching records from an external API.

    Return a list of at least one dict representing a record.
    In a real pipeline you would call requests.get(...) here.
    """
    mock_record = {
        "transaction_id": "12345",
        "customer_email": "h@gmail.com",
        "date": "2024-01-01",
        "region": "North",
        "category": "Widgets",
        "quantity": 10,
        "price": 9.99,
    }
    return [mock_record]
    


def save_results(records: list[dict], output_dir: Path) -> None:
    """
    Write each record as a line to output_dir/results.txt.

    Create output_dir if it does not exist.
    Log the number of records written.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "results.txt", "w") as f:
        for record in records:
            f.write(f"{record}\n")
    logger.info(f"Written {len(records)} records to {output_dir}/results.txt")


def run() -> None:
    config = get_config()
    logger.info("starting pipeline")
    records = fetch_data(config["api_key"])
    output_dir = Path(config["output_dir"])
    save_results(records, output_dir)
    logger.info("pipeline complete")

    download_inputs(DATA_DIR)
    sales_raw, customers_raw = load_and_explore(DATA_DIR)

    sales_clean = clean_sales(sales_raw)
    enriched = join_customers(sales_clean, customers_raw)

    reports = build_reports(enriched)
    write_outputs(reports, OUTPUT_DIR)

    upload_outputs(OUTPUT_DIR, GITHUB_USERNAME)

    logging.info("Pipeline complete.")


if __name__ == "__main__":
    run()



