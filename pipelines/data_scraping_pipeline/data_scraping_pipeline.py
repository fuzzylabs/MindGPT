"""Data scraping pipeline."""
from steps.data_scraping_steps import scrape_mind_data, scrape_nhs_data
from steps.data_versioning_steps import version_data
from zenml import pipeline
from zenml.logger import get_logger

logger = get_logger(__name__)


@pipeline
def data_scraping_pipeline() -> None:
    """The data scraping pipeline.

    Args:
        scrape_nhs_data: This step should scrape data from NHS Mental health conditions page.
        scrape_mind_data: This step should scrape data from the Mind Types of mental health problems page.
    """
    nhs_data = scrape_nhs_data()  # NOQA
    mind_data = scrape_mind_data()  # NOQA
    version_data()
