#!/bin/bash
echo "Installing zenml integration..."
{
    zenml integration install huggingface pytorch seldon -y
} >> setup_out.log

if [[ ! -f .matcha/infrastructure/matcha.state ]]
then
    echo "Error: The file .matcha/infrastructure/matcha.state does not exist!"
    echo "Ensure that you have run 'matcha provision' in this directory and all cloud resources have been provisioned."
    exit 1
fi

function get_state_value() {
    resource_name=$1
    property=$2
    json_string=$(matcha get "$resource_name" "$property" --output json --show-sensitive)
    value=$(echo "$json_string" | sed -n 's/.*"'$property'": "\(.*\)".*/\1/p')
    echo "$value"
}

mlflow_tracking_url=$(get_state_value experiment-tracker tracking-url)
zenml_storage_path=$(get_state_value pipeline storage-path)
zenml_connection_string=$(get_state_value pipeline connection-string)
k8s_context=$(get_state_value orchestrator k8s-context)
acr_registry_uri=$(get_state_value container-registry registry-url)
acr_registry_name=$(get_state_value container-registry registry-name)
zenserver_url=$(get_state_value pipeline server-url)
zenserver_username=$(get_state_value pipeline server-username)
zenserver_password=$(get_state_value pipeline server-password)

echo "Setting up ZenML..."
{
    export AUTO_OPEN_DASHBOARD=false
    az acr login --name="$acr_registry_name"

    zenml init

    # Disconnect from previous server if exists to prevent errors when a new Zen server is being used
    zenml disconnect

    zenml connect --url="$zenserver_url" --username="$zenserver_username" --password="$zenserver_password" --no-verify-ssl

    zenml secret create mgpt_az_secret --connection_string="$zenml_connection_string"
    zenml container-registry register mgpt_acr_registry -f azure --uri="$acr_registry_uri"
    zenml artifact-store register mgpt_az_store -f azure --path="$zenml_storage_path" --authentication_secret=mgpt_az_secret
    zenml orchestrator register mgpt_k8s_orchestrator -f kubernetes --kubernetes_context="$k8s_context" --kubernetes_namespace=zenml --synchronous=True
    zenml image-builder register mgpt_docker_builder --flavor=local

    zenml stack register mindgpt_cloud_stack -i mgpt_docker_builder -c mgpt_acr_registry -a mgpt_az_store -o mgpt_k8s_orchestrator --set
} >> setup_out.log
