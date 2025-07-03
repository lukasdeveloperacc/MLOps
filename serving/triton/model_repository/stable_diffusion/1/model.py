import torch
from diffusers import DiffusionPipeline, ImagePipelineOutput
import numpy as np
import time

try:
    import triton_python_backend_utils as pb_utils
except ImportError:
    class DummyOutput:
        def as_numpy(self) -> np.ndarray:
            pass
        
    class pb_utils:
        @staticmethod
        def get_input_tensor_by_name(request, name: str) -> DummyOutput:
            pass
        
        class InferenceResponse:                
            def __call__(self, *args, **kwds):
                pass
            
        class Tensor:
            def __call__(self, *args, **kwds):
                pass
        
import io

class TritonPythonModel:
    def initialize(self, args):
        model_id = "stabilityai/stable-diffusion-2"
        self._pipeline = DiffusionPipeline.from_pretrained(
            model_id, torch_dtype=torch.float16
        )
        self._pipeline.to("cuda")
        self._generator = torch.Generator("cuda").manual_seed(0)

    def execute(self, requests):
        start = time.time()
        responses = []

        for request in requests:
            prompt_input = pb_utils.get_input_tensor_by_name(request, "prompt")
            prompt_array: np.ndarray = prompt_input.as_numpy().astype(object).squeeze(-1)
            prompts: list[str] = [p.decode("utf-8") for p in prompt_array if isinstance(p, bytes)]

            # Run diffusion pipeline
            output: ImagePipelineOutput = self._pipeline(prompts, generator=self._generator)
            images = output.images  # List of PIL.Image

            images_bytes_list = []
            for image in images:
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                image_bytes = np.frombuffer(buf.getvalue(), dtype=np.uint8)
                images_bytes_list.append(image_bytes)
                
            max_len = max(len(b) for b in images_bytes_list)
            padded_images = np.zeros((len(images_bytes_list), max_len), dtype=np.uint8)
            
            for i, b in enumerate(images_bytes_list):
                padded_images[i, :len(b)] = b

            print(padded_images.shape)
            out_tensor = pb_utils.Tensor("image", padded_images)
            inference_response = pb_utils.InferenceResponse(output_tensors=[out_tensor])
            responses.append(inference_response)

        print("latency : ", time.time() - start)
        return responses
