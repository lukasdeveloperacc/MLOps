from PIL import Image
from hy3dgen.rembg import BackgroundRemover
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline, FaceReducer, FloaterRemover, DegenerateFaceRemover
from hy3dgen.texgen import Hunyuan3DPaintPipeline

import numpy as np
import io, logging, time

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
        # Load Shape Generator
        self.pipeline_shapegen: Hunyuan3DDiTFlowMatchingPipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            "tencent/Hunyuan3D-2mini", subfolder="hunyuan3d-dit-v2-mini", use_safetensors=False
        )
        self.pipeline_shapegen.enable_flashvdm(topk_mode="merge")

        # Load Texture Synthesizer
        self.pipeline_texgen: Hunyuan3DPaintPipeline = Hunyuan3DPaintPipeline.from_pretrained("tencent/Hunyuan3D-2")

        # Load Background Remover
        self.rembg = BackgroundRemover()

    def execute(self, requests):
        start = time.time()
        responses = []

        for request in requests:
            # 1. Get input tensor
            input_tensor = pb_utils.get_input_tensor_by_name(request, "image")
            image_bytes = input_tensor.as_numpy().squeeze()  # np.object_ 배열
            logging.info(f"image_bytes type: {type(image_bytes)}")
            image = Image.open(io.BytesIO(image_bytes.item())).convert("RGBA")

            # 2. Remove background
            image = self.rembg(image)

            # 3. Shape Generation
            mesh = self.pipeline_shapegen(image=image, octree_resolution=320)[0]

            # 4. Clean Mesh
            for cleaner in [FloaterRemover(), DegenerateFaceRemover()]:
                mesh = cleaner(mesh)
            mesh = FaceReducer()(mesh)

            # 5. Texture Synthesis
            mesh = self.pipeline_texgen(mesh, image=image)

            # 6. Export textured mesh to GLB
            glb_bytes = mesh.export(file_type="glb")

            # 7. Output tensor
            mesh_tensor = pb_utils.Tensor("mesh", np.array([glb_bytes], dtype=object))
            inference_response = pb_utils.InferenceResponse(output_tensors=[mesh_tensor])
            responses.append(inference_response)

        logging.info(f"Latency : {time.time() - start} sec")
        return responses
