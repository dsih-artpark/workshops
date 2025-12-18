import glob
import logging
import os

from dataio import DataIOAPI

from example import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(asctime)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main(config_path="config.yaml", force_download=False, future=False):
    """
    Args:
        config_path: Path to the config file.
        force_download: Whether to force download the data. Future feature only, used when future set to True. Unstable.
        future: Whether to use the future feature architecture.
    """
    config = load_config(config_path)
    client = DataIOAPI()

    datasets = set()
    for experiment_name, experiment_config in config["experiments"].items():
        datasets.update([dataset for dataset in experiment_config["datasets"]])
    for dataset in datasets:
        if future:
            dataset_pattern = os.path.join(
                config["meta"]["directories"]["data"], f"{dataset}-*"
            )
            if force_download or not glob.glob(dataset_pattern):
                client.download_dataset(dataset)
                logger.info(f"Downloaded dataset {dataset}")
            else:
                logger.info(f"Dataset {dataset} already exists, skipping")
        else:
            client.download_dataset(dataset)
            logger.info(f"Downloaded dataset {dataset}")
