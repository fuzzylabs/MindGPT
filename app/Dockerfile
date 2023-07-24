FROM python:3.10-slim

# Create a non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

# Install dependencies
RUN pip3 install --no-cache-dir --upgrade \
    pip \
    virtualenv

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    procps && rm -rf /var/lib/apt/lists/*

USER appuser
WORKDIR /home/appuser

# Create a requirements caching layer
COPY app/requirements.txt /home/appuser/app/requirements.txt

ENV VIRTUAL_ENV=/home/appuser/venv
RUN virtualenv ${VIRTUAL_ENV}
RUN . ${VIRTUAL_ENV}/bin/activate && pip install -r app/requirements.txt

# Copy the application code
COPY app /home/appuser/app
COPY utils/chroma_store.py /home/appuser/utils/chroma_store.py
COPY app/run.sh /home/appuser

EXPOSE 8501

ENTRYPOINT ["./run.sh"]
