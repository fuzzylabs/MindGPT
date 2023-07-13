#!/bin/bash
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

echo "Extracting resource names and assigning it to a variable..."
zenml_storage_path=$(get_state_value pipeline storage-path)
zenml_connection_string=$(get_state_value pipeline connection-string)
k8s_context=$(get_state_value orchestrator k8s-context)
acr_registry_uri=$(get_state_value container-registry registry-url)
acr_registry_name=$(get_state_value container-registry registry-name)
seldon_workload_namespace=$(get_state_value model-deployer workloads-namespace)
seldon_ingress_host=$(get_state_value model-deployer base-url)


echo "Setting up ZenML..."
{
    export AUTO_OPEN_DASHBOARD=false

    zenml integration install huggingface pytorch azure kubernetes seldon -y

    az acr login --name="$acr_registry_name"

    zenml init

    # Disconnect from previous server if exists to prevent errors when a new Zen server is being used
    zenml disconnect

    zenml secret create az_secret --connection_string="$zenml_connection_string"
    zenml container-registry register acr_registry -f azure --uri="$acr_registry_uri"
    zenml artifact-store register az_store -f azure --path="$zenml_storage_path" --authentication_secret=az_secret
    zenml image-builder register docker_builder --flavor=local
    zenml model-deployer register seldon_deployer --flavor=seldon \
            --kubernetes_context=$k8s_context \
            --kubernetes_namespace=$seldon_workload_namespace \
            --base_url=http://$seldon_ingress_host  \

    zenml stack register llm_test_stack -i docker_builder -a az_store -o default -c acr_registry --model_deployer=seldon_deployer --set
} >> setup_out.log

echo "ZenML set-up complete."
