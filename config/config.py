"""Configuration options for MindGPT."""

import os

PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(PROJECT_ROOT_DIR, "data/")

VALIDATED_FILE_NAME_POSTFIX = "_data_validated.csv"
