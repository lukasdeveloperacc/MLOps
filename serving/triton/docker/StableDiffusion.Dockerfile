FROM nvcr.io/nvidia/tritonserver:25.06-py3

RUN apt-get update && pip install --upgrade pip && pip install uv

RUN mkdir build && \
    cd build && \
    cmake -DTRITON_ENABLE_GPU=ON -DTRITON_BACKEND_REPO_TAG=r25.06 -DTRITON_COMMON_REPO_TAG=r25.06 -DTRITON_CORE_REPO_TAG=r25.06 -DCMAKE_INSTALL_PREFIX:PATH=`pwd`/install .. && \
    make install
RUN pip install --no-cahce-dir diffusers["torch"] transformers
