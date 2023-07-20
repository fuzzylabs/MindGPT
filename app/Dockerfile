FROM python:3.8-slim

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

RUN pip3 install --no-cache-dir --upgrade \
    pip \
    virtualenv

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git

USER appuser
WORKDIR /home/appuser

COPY app /home/appuser/app
COPY utils/chroma_store.py /home/appuser/utils/chroma_store.py

ENV VIRTUAL_ENV=/home/appuser/venv
RUN virtualenv ${VIRTUAL_ENV}
RUN . ${VIRTUAL_ENV}/bin/activate && pip install -r app/requirements.txt

ENV SELDON_INGRESS=20.68.109.147
EXPOSE 8501

COPY app/run.sh /home/appuser
ENTRYPOINT ["./run.sh"]
