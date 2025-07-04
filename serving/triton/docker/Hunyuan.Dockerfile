FROM nvcr.io/nvidia/tritonserver:25.06-py3

RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /git_repo

RUN git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git

RUN pip install -r requirements.txt && \
    pip install -e . && \
    cd hy3dgen/texgen/custom_rasterizer && \
    python3 setup.py install && \
    cd ../../.. && \
    cd hy3dgen/texgen/differentiable_renderer && \
    python3 setup.py install

WORKDIR /
