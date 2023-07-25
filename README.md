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

Next, we apply Kubernetes manifests to deploy Chroma server on AKS using following commands

```bash
cd infrastructure/chroma_server_k8s
kubectl apply -f .
```

Port-forward the chroma server service to localhost using the following command. This will ensure we can access the server from localhost.

```bash
kubectl port-forward service/server 8000:8000
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
kubectl apply -f infrastructure/llm/seldondeployment.yaml
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
cd infrastructure/streamlit_app_k8s
kubectl apply -f .
```

Finally, we verify the streamlit application. The command below should provide an IP address for the streamlit application.

```bash
kubectl get service streamlit-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

If you visit that URL in browser, you should be able to interact with the deployed streamlit application.

# &#129309; Acknowledgements

This project wouldn't be possible without the exceptional content on both the Mind and NHS Mental Health websites.

# &#128220; License

This project is released under the Apache License. See [LICENSE](LICENSE).
