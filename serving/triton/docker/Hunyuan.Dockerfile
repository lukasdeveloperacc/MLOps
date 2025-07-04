FROM nvcr.io/nvidia/tritonserver:25.06-py3

RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*
    
RUN pip install --upgrade pip && pip install ...
