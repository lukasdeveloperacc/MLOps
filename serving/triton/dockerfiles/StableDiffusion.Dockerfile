FROM nvcr.io/nvidia/tritonserver:25.06-py3

RUN apt-get update && pip install --upgrade pip && pip install uv
RUN pip install --no-cahce-dir diffusers["torch"] transformers
