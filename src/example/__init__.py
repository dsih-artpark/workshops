import logging
import os

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s: %(levelname)s: %(asctime)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Config file not found at {config_path}. Ensure you are in the root of the repository, you're not in a subdirectory, and the file is named {config_path}."
        )
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        logger.info(f"Loaded config from {config_path}")
    return config
