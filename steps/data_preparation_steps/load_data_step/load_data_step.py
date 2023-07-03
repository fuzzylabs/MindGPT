"""Load data step (data prep pipeline)."""

import pandas as pd
from zenml import step
from zenml.logger import get_logger
from zenml.post_execution import PipelineView, get_pipeline
from zenml.post_execution.artifact import ArtifactView
from zenml.steps import Output

logger = get_logger(__name__)


def get_output_from_step(pipeline: PipelineView, step_name: str) -> ArtifactView:
    """Fetch output from a step with last completed run in a pipeline.

    Args:
        pipeline (PipelineView): Post-execution pipeline class object.
        step_name (str): Name of step to fetch output from.

    Returns:
        ArtifactView: Artifact data

    Raises:
        KeyError: If no step found with given name
        ValueError: If no output found for step
    """
    # Get the step with the given name from the last run
    try:
        # Get last completed run of the pipeline
        fetch_last_completed_run = pipeline.runs[0]

        logger.info(f"Run used: {fetch_last_completed_run}")

        # Get the output of the step from last completed run
        fetch_step = fetch_last_completed_run.get_step(step_name)

        logger.info(f"Step used: {fetch_step}")
    except KeyError as e:
        logger.error(f"No step found with name '{step_name}': {e}")
        raise e

    # Get the model artifacts from the step
    output = fetch_step.outputs.get("output")
    if output is None:
        raise ValueError(f"No output found for step '{step_name}'")

    return output


def get_df_from_step(pipeline: PipelineView, fetch_df_step_name: str) -> pd.DataFrame:
    """Fetch DataFrame from specified ZenML pipeline and step name.

    Args:
        pipeline (PipelineView): Post-execution pipeline class object.
        fetch_df_step_name (str): Name of step to fetch DataFrame from.

    Returns:
        pd.DataFrame: DataFrame from ZenML artifact store.

    Raises:
        TypeError: if the specified step output is not of type pd.DataFrame
    """
    # Get the output from the step
    output = get_output_from_step(pipeline, fetch_df_step_name)

    # Read the DataFrame artifact from the output
    df = output.read()

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"Artifact for '{pipeline}' pipeline and step '{fetch_df_step_name}' is not a pandas DataFrame"
        )

    return df


@step
def load_data(pipeline_name: str) -> Output(mind_df=pd.DataFrame, nhs_df=pd.DataFrame):  # type: ignore
    """Loads the data from the output of the last run of the data_scraping_pipeline.

    Args:
        pipeline_name (str): Name of pipeline to get raw scraped data from

    Returns:
        mind_data (pd.DataFrame): Raw scraped data from the Mind website
        nhs_data (pd.DataFrame): Raw scraped data from the NHS website
    """
    # Fetch pipeline by name
    pipeline: PipelineView = get_pipeline(pipeline_name)

    if pipeline is None:
        raise ValueError(f"Pipeline '{pipeline_name}' does not exist")

    logger.info(f"Pipeline: {pipeline}")

    # Fetch the data artifacts from the pipeline
    mind_df = get_df_from_step(pipeline, "scrape_mind_data")
    nhs_df = get_df_from_step(pipeline, "scrape_nhs_data")

    return mind_df, nhs_df
