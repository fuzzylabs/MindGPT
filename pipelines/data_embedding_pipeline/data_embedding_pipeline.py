"""Data embedding pipeline."""
from steps.data_embedding_steps import compute_embedding_drift, embed_data
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
    data_version = "data/second_version"  # should manually update this each time when dataset is collected.

    mind_df, nhs_df = load_data()

    embed_data(
        df=mind_df,
        collection_name="mind_data",
        data_version=data_version,
        embed_model_type="base",
        chunk_size=1000,
        chunk_overlap=200,
    )
    embed_data(
        df=nhs_df,
        collection_name="nhs_data",
        data_version=data_version,
        embed_model_type="base",
        chunk_size=1000,
        chunk_overlap=200,
    )

    _ = compute_embedding_drift(
        after="embed_data",
        collection_name="mind_data",
        reference_data_version="data/first_version",
        current_data_version=data_version,
    )
    _ = compute_embedding_drift(
        after="embed_data",
        collection_name="nhs_data",
        reference_data_version="data/first_version",
        current_data_version=data_version,
    )
