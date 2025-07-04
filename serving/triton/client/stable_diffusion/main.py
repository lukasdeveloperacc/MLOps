from socket import timeout
from tritonclient.http import InferenceServerClient, InferInput
import numpy as np

# Connect to Triton via HTTP
client = InferenceServerClient(url="localhost:1234", connection_timeout=120)

# Batch of prompts
prompts = ["a cat on the moon", "a robot in Tokyo", "a fireman in Korea", "Hansome an American"]
batch_size = len(prompts)

# Create input tensor
input_tensor = InferInput(name="prompt", shape=[batch_size, 1], datatype="BYTES")
input_tensor.set_data_from_numpy(np.array(prompts, dtype=object).reshape(batch_size, 1))

# Send inference request
response = client.infer(model_name="stable_diffusion", inputs=[input_tensor], timeout=120 * 10 ^ 6)

# Extract output
output = response.as_numpy("image")  # Should be shape: (batch_size, variable_length)
for i, img_bytes in enumerate(output):
    with open(f"output_{i}.png", "wb") as f:
        f.write(img_bytes)
