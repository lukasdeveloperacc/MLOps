FROM nvcr.io/nvidia/tritonserver:25.06-py3

RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 git && \
    rm -rf /var/lib/apt/lists/*

RUN pip uninstall torch torchvision torchaudio && \
    pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu129
    
ENV TORCH_CUDA_ARCH_LIST="8.0"
RUN git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git && \
    cd Hunyuan3D-2 && \
    pip install -r requirements.txt && \
    pip install -e . && \
    cd hy3dgen/texgen/custom_rasterizer && \
    python3 setup.py install && \
    cd ../../.. && \
    cd hy3dgen/texgen/differentiable_renderer && \
    python3 setup.py install

CMD ["tritonserver", "--model-repository=/models"]
