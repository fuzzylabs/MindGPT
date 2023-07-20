"""Data embedding pipeline."""
from steps.data_embedding_steps import embed_data
from steps.generic_steps import load_data
from zenml import pipeline
from zenml.logger import get_logger

logger = get_logger(__name__)


@pipeline
def data_embedding_pipeline() -> None:
    """The data embedding pipeline.

    Steps:
        load_data: A ZenML step which loads the data from a specified DVC data version.
        embed_data: A ZenML step which embeds the text data into vectors and pushes to the vector database.
    """
    mind_df, nhs_df = load_data()

    embed_data(mind_df, collection_name="mind_data")
    embed_data(nhs_df, collection_name="nhs_data")
