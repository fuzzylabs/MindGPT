<h1 align="center">
    MindGPT &#129504;
</h1>

<p align="center">
    <a href="https://github.com/fuzzylabs/MindGPT/actions/workflows/ci.yml">
        <img alt="Build" src="https://img.shields.io/github/actions/workflow/status/fuzzylabs/MindGPT/ci.yml">
    </a>
    <a href="https://github.com/fuzzylabs/MindGPT/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/github/license/fuzzylabs/MindGPT?color=blue">
    </a>
</p>

MindGPT is a conversational system where users can ask mental health-orientated questions and receive answers which summarises content from two leading mental health websites: [Mind](https://www.mind.org.uk/) and [NHS Mental Health](https://www.nhs.uk/mental-health/).

**It's not a digital counsellor or therapist and the output from the system should not be treated as such**, MindGPT is purely focused on acting as a gateway to vital information sources, summarising two authoritative perspectives and providing pointers to the original content.

In building this, we've drawn on our expertise in MLOps and prior experience in fine-tuning open-source LLMs for various tasks (see [here](https://github.com/fuzzylabs/matcha-examples/tree/main/llm) for an example of one tuned to summarise legal text). If you're interested in how MindGPT works under the hood and what technologies and data we've used, then take a look [here](docs/inside-mindgpt.md).

# &#8265; Why?

Mental health problems are something that everyone struggles with at various points in their life and finding the right type of help and information can be hard, even a blocker. [Mind](https://www.mind.org.uk/), one of the main mental health charities in the UK, puts this best: _when you're living with a mental health problem, or support someone who is, having access to the right information is vital_.

MindGPT sets out to increase ease of access to this information.

# &#128064; Follow along

This project is in active development at Fuzzy Labs and you can follow along!

The repository for this project is one method where you can monitor progress - we're always raising pull requests to move the project forward. Another way you can do this is to follow our blog. We'll be posting periodic updates as we tick off sections of the project. If you're new to the project, the best place to start is our [project introduction](https://www.fuzzylabs.ai/blog-post/mindgpt-an-introduction).

# &#127939; How do I get started?

## Data Scraping pipeline

Before running the data scraping pipeline, an additional setup for creating a storage container on Azure is required to store the data. We use the [DVC](https://dvc.org/doc/user-guide/data-management/remote-storage/azure-blob-storage) tool for data versioning and data management. Data version [documentation](docs/data-version-control.md) guides you through the process of setting up a storage container on Azure and configuring DVC.

In this pipeline, there are two steps:

* Scrape data from Mind and NHS Mental Health websites
* Store and version the scraped data in a storage container on Azure using DVC

Now that you're all setup, let's run the data scraping pipeline.

```bash
python run.py --scrape
```

## Data Preparation pipeline

Now that we have data scraped, we're ready to prepare that data for the model. We've created a separate pipeline for this, where we clean, validate, and version the data.

We run the data preparation pipeline using the following command.

```bash
python run.py --prepare
```

## Data Embedding pipeline

To run the embedding pipeline, Azure Kubernetes Service (AKS) needs to be provisioned. We use AKS to run the Chroma (vector database) service.

`matcha` tool can help you in provisioning these resources. Install `matcha-ml` library and provision resources using `matcha provision` command.

```bash
pip install matcha-ml
matcha provision
```

After the provisioning completes, we will have on hand these resources:

* Kubernetes cluster on Azure
* Seldon Core installed on this cluster
* Istio ingress installed on this cluster

### Chroma

Next, we apply Kubernetes manifests to deploy Chroma server on AKS using following commands

```bash
kubectl apply -f infrastructure/chroma_server_k8s
```

Port-forward the chroma server service to localhost using the following command. This will ensure we can access the server from localhost.

```bash
kubectl port-forward service/chroma-service 8000:8000
```

### Monitoring

To run the monitoring service on k8s, `matcha provision` must be run beforehand. We will need to build and push the metric service application to ACR. This image will be used by Kubernetes deployment. Before that, we need to set two bash variables, one for ACR registry URI and another for ACR registry name. We will use matcha get command to do this.

```bash
acr_registry_uri=$(matcha get container-registry registry-url --output json | sed -n 's/.*"registry-url": "\(.*\)".*/\1/p')
acr_registry_name=$(matcha get container-registry registry-name --output json | sed -n 's/.*"registry-name": "\(.*\)".*/\1/p')
```

Now we're ready to login into ACR, build and push the image to the ACR.

```bash
az acr login --name $acr_registry_name
docker build -t $acr_registry_uri/monitoring:latest -f monitoring/metric_service/Dockerfile .
docker push $acr_registry_uri/monitoring:latest
```

Line number 39 in [monitoring-deployment.yaml](./infrastructure/monitoring/monitoring-deployment.yaml#L39) should be updated to match the Docker image name which we've just pushed to the ACR, and it will need to be in the following format: `<name-of-acr-registry>.azurecr.io/monitoring`.

Next, we apply the Kubernetes manifest to deploy the metric service and the metric database on AKS.

```bash
kubectl apply -f infrastructure/monitoring
```

Once `kubectl` has finished applying the manifest, we should verify that the monitoring service is running. Running the commands below will give you an IP address for the service, which we can then `curl` for a response:

```bash
kubectl get pods # Checking whether the monitoring pod is running

# Expected output (Note the name of pod will be different)
NAME                                    READY   STATUS    RESTARTS   AGE
monitoring-service-588f644c49-ldjhf     2/2     Running   0          3d1h
```

```bash
kubectl get svc monitoring-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

We should be able to curl the external IP returned running the above command at port 5000.

```bash
curl {external-ip:5000}

# The response should be:
Hello world from the metric service.
```

Now we know that everything is up and running, we need to use port-forwarding so the embedding pipeline (which is running locally) can communicate with the service hosted on Kubernetes:

```bash
kubectl port-forward service/monitoring-service 5000:5000
```

In data embedding pipeline, we take the validated dataset from data preparation pipeline and use Chroma vector database to store the embedding of the text data. This pipelines uses both the Mind and NHS data.

Finally, in a separate terminal we can run the data embedding pipeline.

```bash
python run.py --embed
```

> Note: This pipelines might take somewhere between 5-10 mins to run.

## Provision pre-trained LLM

### Preparation

To deploy a pre-trained LLM model, we first need a Kubernetes cluster with [Seldon Core](https://docs.seldon.io/projects/seldon-core/en/latest/nav/getting-started.html). `matcha` tool can help you in provisioning the required resources. See the section above on how to set this up.

### Deploy model

Apply the prepared kubernetes manifest to deploy the model:

```bash
kubectl apply -f infrastructure/llm_k8s/seldon-deployment.yaml
```

This will create a Seldon deployment, which consists of:

* Pod, that loads the pipeline and the model for inference
* Service and ingress routing, for accessing it from the outside

### Query model

You can get ingress IP with matcha:

```bash
matcha get model-deployer base-url
```

Full URL to query the model:

```bash
http://<INGRESS_IP>/seldon/matcha-seldon-workloads/llm/v2/models/transformer/infer
```

The expected payload structure is as follows:

```json
{
    "inputs": [
        {
            "name": "array_inputs",
            "shape": [-1],
            "datatype": "string",
            "data": "Some prompt text"
        }
    ]
}
```

## Monitoring

### Running locally

To run the monitoring service on your local machine, we'll utilise docker-compose. This will initialise two services - the metric service interface, which listens for POST and GET requests, and the metric database service.

To run docker-compose:

```
docker-compose -f monitoring/docker-compose.yml up
```

Once the two containers has started, we can curl our metric service from the outside.

```
curl localhost:5000/
# This should return a default message saying "Hello world from the metric service."

curl -X POST localhost:5000/readability -H "Content-Type: application/json" -d '{"response": "test_response"}'
# This should compute a readability score and insert the score into the "Readability" relation. We should also expect the following response message:
"{"message":"Readability data has been successfully inserted.","score":36.62,"status_code":200}

curl -X POST localhost:5000/embedding_drift -H "Content-Type: application/json" -d '{"reference_dataset": "1.1", "current_dataset": "1.2", "distance": 0.1, "drifted": true}'
# This should insert the embedding drift data to our "EmbeddingDrift" relation. If success, we should see the following response message:
"{"message":"Validation error: 'reference_dataset is not found in the data dictionary.'","status_code":400}"

# We can also query our database with:
curl localhost:5000/query_readability
```

### Monitoring MindGPT 👀

We've created a [notebook](notebook/monitoring_notebook.ipynb) which accesses the monitoring service, fetches the metrics, and creates some simple plots showing the change over time.

This is a starting point for accessing the metrics, and we're planning to introduce a hosted dashboard version of these plots at some point in the future.

## Streamlit Application

To deploy the Streamlit application on AKS, we first need to build a Docker image and then push it to ACR.

> Note: Run the following command from the root of the project.

Verify that you are in the root of the project.

```bash
pwd

/home/username/MindGPT
```

We build and push the streamlit application to ACR. This image will be used by Kubernetes deployment. Before that, we need to set two bash variables, one for ACR registry URI and another for ACR registry name. We will use `matcha get` command to do this.

```bash
acr_registry_uri=$(matcha get container-registry registry-url --output json | sed -n 's/.*"registry-url": "\(.*\)".*/\1/p')
acr_registry_name=$(matcha get container-registry registry-name --output json | sed -n 's/.*"registry-name": "\(.*\)".*/\1/p')
```

Now we're ready to login into ACR, build and push the image to the ACR.

```bash
az acr login --name $acr_registry_name
docker build -t $acr_registry_uri/mindgpt:latest -f app/Dockerfile .
docker push $acr_registry_uri/mindgpt:latest
```

Line number 19 in [streamlit-deployment.yaml](./infrastructure/streamlit_k8s/streamlit-deployment.yaml#L19) should be updated to match the Docker image name which we've just pushed to the ACR, and it will need to be in the following format: `<name-of-acr-registry>.azurecr.io/mindgpt`.

Next, we apply the Kubernetes manifest to deploy the streamlit application on AKS.

```bash
kubectl apply -f infrastructure/streamlit_k8s
```

Finally, we verify the streamlit application. The command below should provide an IP address for the streamlit application.

```bash
kubectl get service streamlit-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

If you visit that URL in browser, you should be able to interact with the deployed streamlit application.

## Larger LLM models

In this section, we'll show how to deploy a larger LLM model on AKS. We will use [OpenLLM](https://github.com/bentoml/OpenLLM) project to deploy a `flan-t5-xl` model. `xl` variant contains 3B parameters and weighs about 11 GB in size.

### Deploying the model on AKS

For this approach, we will deploy 2 VMs, one VM will act as CPU pool and other VM will act as GPU pool. GPU pool will be used to run the model.

> Note: `Standard_NC4as_T4_v3` VM instance is not readily available. A quota request has to be submitted to Azure.

1. Create a new AKS cluster with the system node CPU pool using `Standard_DS2_v3` VM instance.

    ```bash
    az aks create --resource-group <existing-resource-group> --name largellm --node-count 1 --node-vm-size Standard_DS2_v3 --generate-ssh-keys
    ```

2. Create a GPU Node pool using `Standard_NC4as_T4_v3` VM instance. This VM instance contains 4 vCPU, 28 GB RAM and T4 GPU with 16 GB VRAM.

    ```bash
    az extension add --name aks-preview
    az extension update --name aks-preview
    az feature register --namespace "Microsoft.ContainerService" --name "GPUDedicatedVHDPreview"
    az provider register --namespace Microsoft.ContainerService
    ```

    ```bash
    az aks nodepool add \
    --resource-group <existing-resource-group> \
    --cluster-name largellm \
    --name gpunp \
    --node-count 1 \
    --node-vm-size Standard_NC4as_T4_v3 \
    --node-taints sku=gpu:NoSchedule \
    --aks-custom-headers UseGPUDedicatedVHD=true \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 1
    ```

    Verify both the nodes are provisioned.

    ```bash
    kubectl get nodes

    Expected Output (the names of node might be different)
    NAME                                STATUS   ROLES   AGE    VERSION
    aks-gpunp-42873702-vmss000000       Ready    agent   5h5m   v1.26.6
    aks-nodepool1-25311124-vmss000000   Ready    agent   5h9m   v1.26.6
    ```

3. Build and push docker image to ACR.

    > Note: This creates a docker image of size **12-13 GB** that should be pushed to the ACR.

    ```bash
    az acr login --name <acr-registry-name>
    docker build -t $acr_registry_uri/mindgpt/openllm:latest -f infrastructure/llm_k8s/Dockerfile .
    docker push $acr_registry_uri/mindgpt/openllm:latest
    ```

4. Allow AKS to pull the image from ACR.

    ```bash
    az aks update --resource-group <existing-resource-group> --name largellm --attach-acr <acr-registry-name>
    ```

5. Apply the Kubernetes manifest to deploy the model on AKS.

    ```bash
    kubectl apply -f infrastructure/llm_k8s/openllm-deployment.yaml
    ```

6. Verify the model is deployed.

    ```bash
    kubectl get pods

    Expected Output (the name of pod might be different)
    NAME                                          READY   STATUS    RESTARTS   AGE
    openllm-mindgpt-deployment-77985f86c9-4fj8b   1/1     Running   0          137m
    ```

# &#129309; Acknowledgements

This project wouldn't be possible without the exceptional content on both the Mind and NHS Mental Health websites.

# &#128220; License

This project is released under the Apache License. See [LICENSE](LICENSE).
