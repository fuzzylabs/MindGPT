"""Configuration options for MindGPT."""

import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(ROOT_DIR, "data/")

VALIDATED_FILE_NAME_POSTFIX = "_data_validated.csv"
