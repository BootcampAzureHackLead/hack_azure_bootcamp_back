import logging
import os

from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from flask import Flask, render_template


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)

STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "mensajes")
BLOB_NAME = os.getenv("BLOB_NAME", "mensaje.txt")


def read_promotion_message() -> str:
    """Read the promotion managed by the administrator in Blob Storage."""
    if not STORAGE_ACCOUNT_NAME:
        raise RuntimeError("STORAGE_ACCOUNT_NAME is not configured")

    account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    credential = DefaultAzureCredential()
    blob_client = BlobServiceClient(
        account_url=account_url, credential=credential
    ).get_blob_client(container=BLOB_CONTAINER_NAME, blob=BLOB_NAME)
    return blob_client.download_blob().readall().decode("utf-8").strip()


@app.get("/")
def home():
    try:
        promotion = read_promotion_message()
    except (AzureError, UnicodeDecodeError, RuntimeError):
        logger.exception("Unable to read the promotion from Blob Storage")
        return render_template(
            "index.html",
            promotion="Promoción no disponible",
            storage_error=True,
        ), 503

    return render_template("index.html", promotion=promotion, storage_error=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
