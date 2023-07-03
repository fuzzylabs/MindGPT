"""Run all pipelines."""
import click
from pipelines.data_preparation_pipeline.data_preparation_pipeline import (
    data_preparation_pipeline,
)
from pipelines.data_scraping_pipeline.data_scraping_pipeline import (
    data_scraping_pipeline,
)
from pipelines.deployment_pipeline.deployment_pipeline import deployment_pipeline
from zenml.logger import get_logger

logger = get_logger(__name__)


def run_data_scrapping_pipeline() -> None:
    """Run all steps in the data scrapping pipeline."""
    pipeline = data_scraping_pipeline.with_options(
        config_path="pipelines/data_scraping_pipeline/config_data_scraping_pipeline.yaml"
    )
    pipeline()


def run_data_preparation_pipeline() -> None:
    """Run all steps in the data preparation pipeline."""
    pipeline = data_preparation_pipeline.with_options(
        config_path="pipelines/data_preparation_pipeline/config_data_preparation_pipeline.yaml"
    )
    pipeline()


def run_deployment_pipeline() -> None:
    """Run all the steps in the deployment pipeline."""
    pipeline = deployment_pipeline
    pipeline()


@click.command()
@click.option("--scrape", "-s", is_flag=True, help="Run data scraping pipeline.")
@click.option(
    "--prepare", "-p", is_flag=True, help="Run the data preparation pipeline."
)
@click.option("--deploy", "-d", is_flag=True, help="Run the deployment pipeline.")
def main(scrape: bool, prepare: bool, deploy: bool) -> None:
    """Run all pipelines.

    Args:
        scrape (bool): run the data scraping pipeline when True.
        prepare (bool): run the data preparation pipeline when True.
        deploy (bool): run the deployment pipeline when True.
    """
    if scrape:
        logger.info("Running data scraping pipeline.")
        run_data_scrapping_pipeline()

    if prepare:
        logger.info("Running the data preparation pipeline.")
        run_data_preparation_pipeline()

    if deploy:
        logger.info("Running the deployment pipeline.")
        run_deployment_pipeline()


if __name__ == "__main__":
    """Main."""
    main()
