import logging
import os


from typing import Optional


def setup_logging(service_name: Optional[str] = None, cloud: Optional[bool] = None):
    """
    Sets up logging for both local and GCP environments.
    If running in GCP, attaches Cloud Logging handler.
    Otherwise, logs to console in structured format.
    """
    # Detect environment
    if cloud is None:
        cloud = bool(os.getenv("GOOGLE_CLOUD_PROJECT"))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove default handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)

    if cloud:
        try:
            import google.cloud.logging

            client = google.cloud.logging.Client()
            client.setup_logging()
        except ImportError:
            logging.basicConfig(
                format="%(asctime)s %(levelname)s %(name)s %(message)s",
                level=logging.INFO,
            )
            logging.warning("google-cloud-logging not installed, using basic logging.")
    else:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
            level=logging.INFO,
        )
        if service_name:
            logging.info(f"Service: {service_name}")
