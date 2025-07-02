FROM ghcr.io/mlflow/mlflow:v3.1.1

RUN apt-get update && pip install --upgrade pip && pip install uv

RUN uv pip install --system boto3
