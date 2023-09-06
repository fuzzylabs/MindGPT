FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

ENV BENTOML_HOME="/model_store/"
ENV CUDA_VISIBLE_DEVICES=0

RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install "openllm[flan-t5]"
EXPOSE 3000

ENTRYPOINT [ "openllm", "start" ]
CMD [ "flan-t5", "--model-id", "lmsys/fastchat-t5-3b-v1.0", "--device", "0", "-p", "3000", "--verbose"]