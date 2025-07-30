from PIL import Image
import warnings

warnings.filterwarnings("ignore")
import os
import trimesh
from step1x3d_texture.pipelines.step1x_3d_texture_synthesis_pipeline import (
    Step1X3DTexturePipeline,
)

from step1x3d_geometry.models.pipelines.pipeline_utils import reduce_face, remove_degenerate_face
from step1x3d_geometry.models.pipelines.pipeline import Step1X3DGeometryPipeline
import torch

import numpy as np
import io, logging, time, uuid

logging.basicConfig(level=logging.INFO)

try:
    import triton_python_backend_utils as pb_utils
except ImportError:

    class DummyOutput:
        def as_numpy(self) -> np.ndarray:
            return np.ndarray((-1))

    class pb_utils:
        @staticmethod
        def get_input_tensor_by_name(request, name: str) -> DummyOutput:
            return DummyOutput()

        class InferenceResponse:
            def __call__(self, *args, **kwds):
                pass

        class Tensor:
            def __call__(self, *args, **kwds):
                pass


class TritonPythonModel:
    def initialize(self, args):
        self._geo_pipeline = Step1X3DGeometryPipeline.from_pretrained(
            "stepfun-ai/Step1X-3D", subfolder="Step1X-3D-Geometry-1300m"
        ).to("cuda")
        self._texture_pipeline = Step1X3DTexturePipeline.from_pretrained(
            "stepfun-ai/Step1X-3D", subfolder="Step1X-3D-Texture"
        )

    def execute(self, requests):
        try:
            start = time.time()
            responses = []

            for request in requests:
                # 1. Get input tensor
                input_tensor = pb_utils.get_input_tensor_by_name(request, "image")
                image_bytes = input_tensor.as_numpy().squeeze()  # np.object_ 배열
                logging.info(f"image_bytes type: {type(image_bytes)}")
                image = Image.open(io.BytesIO(image_bytes.item())).convert("RGBA")
                filename = f"{uuid.uuid4()}.png"
                image.save(filename)

                generator = torch.Generator(device=self._geo_pipeline.device)
                generator.manual_seed(2025)
                out = self._geo_pipeline(filename, guidance_scale=7.5, num_inference_steps=50, generator=generator)
                glb_filename = f"{filename.split('.')[0]}.glb"
                out.mesh[0].export(glb_filename)

                mesh = trimesh.load(glb_filename)
                mesh = remove_degenerate_face(mesh)
                mesh = reduce_face(mesh)

                textured_mesh = self._texture_pipeline(filename, mesh, seed=2025)
                textured_mesh.export(glb_filename)

                with open(glb_filename, "rb") as f:
                    glb_bytes = f.read()
                    mesh_tensor = pb_utils.Tensor("mesh", np.array([glb_bytes], dtype=object))
                    inference_response = pb_utils.InferenceResponse(output_tensors=[mesh_tensor])
                    responses.append(inference_response)

            logging.info(f"Latency : {time.time() - start} sec")
            return responses

        finally:
            os.remove(filename)
            os.remove(glb_filename)
