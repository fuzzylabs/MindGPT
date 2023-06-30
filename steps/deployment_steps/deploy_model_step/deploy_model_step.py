"""Deploy the fetched model using Seldon."""
from zenml import step


@step
def deploy_model() -> None:
    """Deploys the fetched model using Seldon."""
    ...
