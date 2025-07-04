import tritonclient.http as httpclient
import numpy as np

# Triton 서버 주소 (HTTP)
TRITON_URL = "localhost:1234"  # 기본 HTTP 포트


# 입력 이미지 로드 및 변환
def load_image(path: str) -> np.ndarray:
    with open(path, "rb") as f:
        image_bytes = f.read()
    return np.array([image_bytes], dtype=object)


# Triton HTTP client 생성
client = httpclient.InferenceServerClient(url=TRITON_URL, verbose=False, network_timeout=180.0)

# 이미지 준비
image_np = load_image("assets/pikachu.png")

# 입력 텐서 생성
input_tensor = httpclient.InferInput(name="image", shape=image_np.shape, datatype="BYTES")
input_tensor.set_data_from_numpy(image_np)

# 추론 요청
response = client.infer(
    model_name="hunyuan3d", inputs=[input_tensor], timeout=180000000
)  # Triton 모델 이름 (디렉토리 이름)

# 출력 받기
output = response.as_numpy("mesh")
if output is None:
    raise RuntimeError("Failed to get mesh output from Triton server")
glb_bytes = output[0]

# 결과 저장
with open("output_mesh.glb", "wb") as f:
    f.write(glb_bytes)

print("GLB 파일 저장 완료: output_mesh.glb")
