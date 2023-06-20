"""Data scraping pipeline."""
from zenml.logger import get_logger
from zenml.pipelines import pipeline

logger = get_logger(__name__)


@pipeline  # type: ignore
def data_scraping_pipeline(  # Okay! # For mypy to ignore arg type hint
    scrape_nhs_data,
    scrape_mind_data,
    save_data,
) -> None:
    """The data scraping pipeline.

    Args:
        scrape_nhs_data: This step should scrape data from NHS Mental health conditions page.
        scrape_mind_data: This step should scrape data from the Mind Types of mental health problems page.
        save_data: This step should save the scraped data as csv as push it to a storage bucket.
    """
    nhs_data = scrape_nhs_data()
    mind_data = scrape_mind_data()

    save_data(nhs_data, mind_data)
