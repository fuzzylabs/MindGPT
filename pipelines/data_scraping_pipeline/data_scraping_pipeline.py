"""Data scraping pipeline."""
from zenml.logger import get_logger
from zenml.pipelines import pipeline
from zenml.steps import BaseStep

logger = get_logger(__name__)


@pipeline
def data_scraping_pipeline(
    scrape_nhs_data: BaseStep,
    scrape_mind_data: BaseStep,
) -> None:
    """The data scraping pipeline.

    Args:
        scrape_nhs_data: This step should scrape data from NHS Mental health conditions page.
        scrape_mind_data: This step should scrape data from the Mind Types of mental health problems page.
    """
    scrape_nhs_data()
    scrape_mind_data()
