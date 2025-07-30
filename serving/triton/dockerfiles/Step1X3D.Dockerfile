FROM nvcr.io/nvidia/tritonserver:24.04-py3

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME='/usr/local/cuda'
ARG TORCH_CUDA_ARCH_LIST="8.0"
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=all
ENV PYTHONPATH=${PYTHONPATH}:/root
ENV FORCE_CUDA=1

RUN apt-get update && apt-get install -y \
    git \
    wget \
    libgl1 \
    libglib2.0-0 \
    libmagic1 \
    build-essential \
    cmake \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

RUN pip install --no-cache-dir torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124

RUN git clone --depth 1 --branch main https://github.com/stepfun-ai/Step1X-3D.git
WORKDIR /root/Step1X-3D

RUN pip install --no-cache-dir --ignore-installed -r requirements.txt \
    && pip install --no-cache-dir torch-cluster -f https://data.pyg.org/whl/torch-2.5.1+cu124.html \
    && pip uninstall -y pytorch3d \
    && pip install "git+https://github.com/facebookresearch/pytorch3d.git@stable" \
    && pip install --no-cache-dir kaolin==0.17.0 -f https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.5.1_cu124.html \
    && cd step1x3d_texture/custom_rasterizer && python3 setup.py install && cd .. \
    && cd differentiable_renderer && python3 setup.py install \
    && pip install --no-cache-dir python-magic

COPY ./model_repository/step1x-3d /models/step1x-3d
ARG MODEL_VERSION=1
RUN ln -s /root/Step1X-3D /models/step1x-3d/${MODEL_VERSION}/Step1X-3D

CMD ["tritonserver", "--model-repository=/models"]
