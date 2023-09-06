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

# OpenLLM configuration
OPENLLM_SERVICE_NAME = "openllm-mindgpt-svc"
OPENLLM_NAMESPACE = "default"
OPENLLM_PORT = 3000

# Metric service configuration
METRIC_SERVICE_NAME = "monitoring-service"
METRIC_SERVICE_NAMESPACE = "default"
METRIC_SERVICE_PORT = "5000"
