import torch
import numpy as np
from PIL import Image
import requests
import json
import base64
import time
import os
import io

# --------------------------------------------------------------------------------
# 辅助函数区域 (无变化)
# --------------------------------------------------------------------------------

def encode_image_to_base64(image_tensor):
    """将ComfyUI的Tensor格式图片编码为API要求的Base64字符串。"""
    try:
        i = 255. * image_tensor.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()
        base64_bytes = base64.b64encode(byte_arr)
        base64_string = base64_bytes.decode('utf-8')
        return f"data:image/png;base64,{base64_string}"
    except Exception as e:
        print(f"ERROR: Image encoding to Base64 failed: {e}")
        return None

def process_image_to_tensor(image_bytes):
    """将二进制图片数据转换为ComfyUI的Tensor格式。"""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        np_image = np.array(img).astype(np.float32) / 255.0
        return torch.from_numpy(np_image)[None,]
    except Exception as e:
        print(f"ERROR: Failed to process image bytes into tensor: {e}")
        return None

def decode_base64_to_tensor(base64_string):
    """将API返回的Base64字符串解码为ComfyUI的Tensor格式图片。"""
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]
        img_data = base64.b64decode(base64_string)
        return process_image_to_tensor(img_data)
    except Exception as e:
        print(f"ERROR: Image decoding from Base64 failed: {e}")
        return None

def download_image_to_tensor(url):
    """从URL下载图片并将其转换为ComfyUI的Tensor格式。"""
    try:
        print(f"Downloading image from URL: {url[:80]}...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return process_image_to_tensor(response.content)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to download image from URL {url}: {e}")
        return None

# --------------------------------------------------------------------------------
# ComfyUI 节点核心类
# --------------------------------------------------------------------------------

class VolcanoEngineAPINode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "api_url": ("STRING", {
                    "multiline": False,
                    "default": "https://ark.cn-beijing.volces.com/api/v3/images/generations"
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": os.getenv("ARK_API_KEY", "在此输入你的火山引擎API Key")
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "在这里输入prompt"
                }),
                # --- 根据官方文档进行最终修正 ---
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
                "model": (["doubao-seedream-4-0-250828"],),
                "strength": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05
                }),
                "size": (["auto", "1K", "2K", "4K"],),
                "watermark": ("BOOLEAN", {"default": False}),
                "sequential_image_generation": (["disabled", "auto"],),
                "max_images": ("INT", {"default": 1, "min": 1, "max": 15, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"
    CATEGORY = "Volcano Engine API"

    def generate_image(self, image, api_url, api_key, prompt, seed, model, strength, size, watermark, sequential_image_generation, max_images):

        if not api_url:
            print("ERROR: API URL is empty.")
            return (image,) 

        if not api_key or "在此输入" in api_key:
            print("ERROR: Volcano Engine API Key is missing.")
            return (image,)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        base64_images = []
        print(f"Processing a batch of {len(image)} images for a single API call...")
        for img_tensor in image:
            single_image_batch = img_tensor.unsqueeze(0)
            base64_data = encode_image_to_base64(single_image_batch)
            if base64_data:
                base64_images.append(base64_data)

        if not base64_images:
            print("ERROR: Failed to encode any images from the input batch.")
            return (image,)

        payload = {
            "model": model,
            "prompt": prompt,
            "image": base64_images,
            "strength": strength,
            "seed": seed,
            "response_format": "b64_json",
            "watermark": watermark
        }

        if size != "auto":
            payload['size'] = size

        if sequential_image_generation == "auto":
            payload['sequential_image_generation'] = "auto"
            payload['sequential_image_generation_options'] = {
                "max_images": max_images
            }

        result_images = []
        payload_for_log = {k: v for k, v in payload.items() if k != 'image'}
        payload_for_log['image_count'] = len(payload.get('image', []))
        print(f"Sending single request to {api_url} with payload: {json.dumps(payload_for_log, indent=2)}")
        
        try:
            start_time = time.time()
            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=180)
            end_time = time.time()
            
            print(f"API Response Status Code: {response.status_code}. Time taken: {end_time - start_time:.2f} seconds.")
            response.raise_for_status()
            
            result_json = response.json()

            if "data" in result_json and result_json["data"]:
                print(f"API returned {len(result_json['data'])} images.")
                for item in result_json["data"]:
                    processed_image = None
                    if item.get("b64_json"):
                        processed_image = decode_base64_to_tensor(item["b64_json"])
                    elif item.get("url"):
                        processed_image = download_image_to_tensor(item["url"])
                    
                    if processed_image is not None:
                        result_images.append(processed_image)
                    else:
                        print(f"Warning: Could not process API response item: {item}")
            else:
                print("Error: No 'data' found in API response.")
                print("Full API Response:", json.dumps(result_json, indent=2, ensure_ascii=False))

        except requests.exceptions.RequestException as e:
            print(f"ERROR: API request failed.")
            if e.response is not None:
                print(f"Error status code: {e.response.status_code}")
                try: 
                    print(f"--- API SERVER ERROR DETAILS ---")
                    print(json.dumps(e.response.json(), indent=2, ensure_ascii=False))
                    print(f"--------------------------------")
                except json.JSONDecodeError: 
                    print(f"Error response content: {e.response.text}")
            return (image,)

        if not result_images:
            print("ERROR: No images were generated. Returning the original input images.")
            return (image,)
            
        final_batch = torch.cat(result_images, dim=0)
        return (final_batch,)

# --------------------------------------------------------------------------------
# 节点注册
# --------------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "VolcanoEngineAPINode": VolcanoEngineAPINode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "VolcanoEngineAPINode": "火山引擎(Volcano API)"
}