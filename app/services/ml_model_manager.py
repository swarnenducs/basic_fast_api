"""Loads / evaluates the ML model from blob using the version in env."""

from app.core.config import settings
from app.services.blob_download import BlobDownload


class MLModelManagerFromBlob:
    def __init__(self):
        self.blob_download = BlobDownload()
        self.model_version = settings.ml_model_version

    def check_and_evaluate_ml_model(self):
        """Implement your code"""
        self.blob_download.download_blob(
            container=settings.blob_container_name,
            blob_name=settings.blob_model_path,
        )
        return self.model_version
