"""Run all pipeline."""
import click
from pipelines.data_scraping_pipeline.data_scraping_pipeline import (
    data_scraping_pipeline,
)
from steps.save_data.save_data_step import save_data
from steps.scrape_mind_data.scrape_mind_data_step import scrape_mind_data
from steps.scrape_nhs_data.scrape_nhs_data_step import scrape_nhs_data

from pipelines.data_preparation_pipeline.data_preparation_pipeline import (
    data_preparation_pipeline,
)
from steps.data_preparation_step.data_preparation_step import (
    load_data,
    clean_data,
    validate_data,
    version_data,
)
from zenml.logger import get_logger

logger = get_logger(__name__)


def run_data_scrapping_pipeline() -> None:
    """Run all steps in the data scrapping pipeline."""
    pipeline = data_scraping_pipeline(
        scrape_nhs_data(), scrape_mind_data(), save_data()
    )
    pipeline.run(
        config_path="pipelines/data_scraping_pipeline/config_data_scraping_pipeline.yaml"
    )


def run_data_preparation_pipeline() -> None:
    """Run all steps in the data preparation pipeline."""
    pipeline = data_preparation_pipeline(
        load_data(), clean_data(), validate_data(), version_data()
    )
    pipeline.run(
        config_path="pipelines/data_preparation_pipeline/config_data_preparation_pipeline.yaml"
    )


@click.command()
@click.option("--scrape", "-s", is_flag=True, help="Run data scraping pipeline.")
@click.option("--prepare", "-p", is_flag=True, help="Run the data preparation pipeline.")
def main(scrape: bool, prepare: bool) -> None:
    """Run all pipelines.

    Args:
        scrape (bool): run the data scraping pipeline when True.
        prepare (bool): run the data preparation pipeline when True.
    """
    if scrape:
        logger.info("Running data scraping pipeline.")
        run_data_scrapping_pipeline()

    if prepare:
        logger.info("Running the data preparation pipeline.")
        run_data_preparation_pipeline()


if __name__ == "__main__":
    """Main."""
    main()
