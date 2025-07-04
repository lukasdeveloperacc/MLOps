from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("tencent/Hunyuan3D-2")
mesh = pipeline(image="test.png")[0]

from hy3dgen.texgen import Hunyuan3DPaintPipeline
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline


# let's generate a mesh first
pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("tencent/Hunyuan3D-2")
mesh = pipeline(image="test.png")[0]

pipeline = Hunyuan3DPaintPipeline.from_pretrained("tencent/Hunyuan3D-2")
mesh = pipeline(mesh, image="assets/demo.png")
