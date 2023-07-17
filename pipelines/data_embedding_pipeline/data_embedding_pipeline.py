"""Data embedding pipeline."""
from steps.data_embedding_steps import embed_data, fetch_data
from zenml import pipeline
from zenml.logger import get_logger

logger = get_logger(__name__)


@pipeline
def data_embedding_pipeline() -> None:
    """The data embedding pipeline.

    Steps:
        fetch_data: A ZenML step which loads the data from a specified DVC data version.
        embed_data: A ZenML step which embeds the text data into vectors and pushes to the vector database.
    """
    mind_df, nhs_df = fetch_data()

    mind_df = embed_data(mind_df)
    nhs_df = embed_data(nhs_df)
