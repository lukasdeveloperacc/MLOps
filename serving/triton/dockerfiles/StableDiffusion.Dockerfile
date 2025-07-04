FROM nvcr.io/nvidia/tritonserver:25.06-py3

RUN pip install --no-cache-dir diffusers["torch"] transformers

CMD ["tritonserver", "--model-repository=/models"]
