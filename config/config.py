"""Configuration options for MindGPT."""

import os

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/"
)

VALIDATED_FILE_NAME_POSTFIX = "_data_validated.csv"
