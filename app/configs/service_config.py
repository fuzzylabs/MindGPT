"""Config variables for the 3 services."""
# Setup for chroma vector store
CHROMA_SERVER_HOST_NAME = "chroma-service.default"
CHROMA_SERVER_PORT = "8000"
DEFAULT_EMBED_MODEL = "base"  # ["base", "large", "xl"]
N_CLOSEST_MATCHES = 3
EMBED_MODEL_MAP = {
    "xl": "hkunlp/instructor-xl",
    "large": "hkunlp/instructor-large",
    "base": "hkunlp/instructor-base",
}
COLLECTION_NAME_MAP = {"mind_data": "Mind", "nhs_data": "NHS"}

# Seldon configuration
SELDON_SERVICE_NAME = "llm-default-transformer"
SELDON_NAMESPACE = "matcha-seldon-workloads"
SELDON_PORT = 9000

# Metric service configuration
METRIC_SERVICE_NAME = "monitoring-service"
METRIC_SERVICE_NAMESPACE = "default"
METRIC_SERVICE_PORT = "5000"
