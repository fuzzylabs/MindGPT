# Derived from ZenML example custom code deployment; source : https://github.com/zenml-io/zenml/blob/release/0.40.3/examples/custom_code_deployment/seldon_pytorch/steps/deployer.py
"""Deploy LLM model server using seldon."""
from steps.deployment_steps.deploy_model_step.seldon_llm_custom_deployer_step import (
    seldon_llm_model_deployer_step,
)
from zenml.integrations.seldon.seldon_client import SeldonResourceRequirements
from zenml.integrations.seldon.services.seldon_deployment import (
    SeldonDeploymentConfig,
)

seldon_llm_custom_deployment = seldon_llm_model_deployer_step.with_options(
    parameters={
        "predict_function": "steps.deployment_steps.deploy_model_step.llm_custom_predict.custom_predict",
        "service_config": SeldonDeploymentConfig(
            model_name="seldon-llm-custom-model",
            replicas=1,
            implementation="custom",
            resources=SeldonResourceRequirements(
                limits={"cpu": "500m", "memory": "900Mi"}
            ),
        ),
        "timeout": 300,
    }
)
