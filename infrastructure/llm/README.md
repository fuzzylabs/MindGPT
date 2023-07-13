# LLM on Seldon Core

This document walks through how to deploy an LLM on Kubernetes using Seldon.

## Prerequisites
* Kubernetes cluster
* Seldon Core installed 
If the cluster and Seldon were provisioned with Matcha, kubectl already has correct context.

## Deploy LLM
```
kubectl apply -f seldondeployment.yaml
```

This K8s manifest is not parameterised. It hard-codes what model to pull from Huggingface Hub in pretrained_model parameter

## Query LLM
Go to `http://<seldon-ingress>/seldon/default/llm/api/v1.0/docs` to see OpenAPI specifications

## Destroy LLM
```
kubectl delete -f seldondeployment.yaml
```