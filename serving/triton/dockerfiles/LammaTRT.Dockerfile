FROM nvcr.io/nvidia/tritonserver:24.11-trtllm-python-py3
ENV TRTLLM_ORCHESTRATOR=1
ARG HF_TOKEN

# https://github.com/NVIDIA/TensorRT-LLM/tree/main/examples/models/core/llama
# https://github.com/NVIDIA/TensorRT-LLM/tree/main/examples/models/core/llama#llama-v3-updates
RUN apt-get update && git lfs install \
    huggingface-cli login --token ${HF_TOKEN} \
    git clone https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
# https://github.com/triton-inference-server/triton_cli
# RUN pip install /opt/tritonserver/python/triton*.whl

# WORKDIR /
# RUN git clone -b r24.11 https://github.com/triton-inference-server/server.git && pip install -r server/python/openai/requirements.txt

# WORKDIR /server/python/openai
# CMD [ "python3", "openai_frontend/main.py", "--model-repository", "/root/models", "--tokenizer", "meta-llama/Meta-Llama-3.1-8B-Instruct" ]
