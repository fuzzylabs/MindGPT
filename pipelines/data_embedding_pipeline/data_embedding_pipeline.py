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
        compute_embedding_drift: A ZenML step which computes the embedding drift between the current and reference data versions.
    """
    current_data_version, reference_data_version, mind_df, nhs_df = load_data()

    embed_data(
        mind_df,
        embed_model_type="base",
        data_version=current_data_version,
        collection_name="mind_data",
        chunk_size=780,
        chunk_overlap=50,
    )

    embed_data(
        nhs_df,
        embed_model_type="base",
        data_version=current_data_version,
        collection_name="nhs_data",
        chunk_size=2000,
        chunk_overlap=50,
    )

    _ = compute_embedding_drift(
        after="embed_data",
        collection_name="mind_data",
        reference_data_version=reference_data_version,
        current_data_version=current_data_version,
    )

    _ = compute_embedding_drift(
        after="embed_data",
        collection_name="nhs_data",
        reference_data_version=reference_data_version,
        current_data_version=current_data_version,
    )
