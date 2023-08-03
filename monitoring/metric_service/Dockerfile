FROM python:3.10-slim-buster

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV DB_NAME=postgres
ENV DB_HOST=localhost
ENV DB_USER=postgres
ENV DB_PORT=5432
ENV DB_PASSWORD=postgres

COPY monitoring/metric_service/requirements.txt .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install \
    --upgrade pip \
    -r requirements.txt

COPY monitoring/metric_service/ .
COPY utils/metric_database.py utils/metric_database.py

CMD ["python", "-m", "flask", "--app", "monitoring/app.py", "run", "--host=0.0.0.0"]
