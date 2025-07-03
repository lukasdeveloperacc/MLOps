# import tritonclient.http as httpclient
# import numpy as np

# client = httpclient.InferenceServerClient(url="localhost:1234")

# prompt = "Make beautiful chairs in the style of a modern art gallery, high quality, detailed, 4k resolution"
# prompt_tensor = httpclient.InferInput("prompt", [1], "BYTES")
# prompt_tensor.set_data_from_numpy(np.array([prompt], dtype=object))

# response = client.infer(model_name="stable_diffusion", inputs=[prompt_tensor])
# image_bytes = response.as_numpy("image")[0]

# from PIL import Image
# from io import BytesIO

# image = Image.open(BytesIO(image_bytes))
# image.save("triton_output.png")


from tritonclient.http import InferenceServerClient, InferInput
import numpy as np

# Connect to Triton via HTTP
client = InferenceServerClient("localhost:1234")

# Batch of prompts
prompts = ["a cat on the moon", "a robot in Tokyo", "a fireman in Korea", "Hansome an American"]
batch_size = len(prompts)

# Create input tensor
input_tensor = InferInput(name="prompt", shape=[batch_size, 1], datatype="BYTES")
input_tensor.set_data_from_numpy(np.array(prompts, dtype=object).reshape(batch_size, 1))

# Send inference request
response = client.infer(model_name="stable_diffusion", inputs=[input_tensor])

# Extract output
output = response.as_numpy("image")  # Should be shape: (batch_size, variable_length)
for i, img_bytes in enumerate(output):
    with open(f"output_{i}.png", "wb") as f:
        f.write(img_bytes)
