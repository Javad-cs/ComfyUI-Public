# create_tokenizer_model.py
from transformers import AutoTokenizer
import sentencepiece as spm
import os
import json

model_path = "/generic/path/ComfyUI/models/Janus-Pro/Janus-Pro-1B"

print("Attempting to create tokenizer.model...")

try:
    print("Downloading compatible tokenizer.model...")
    import urllib.request
    
    url = "https://huggingface.co/NousResearch/Llama-2-7b-hf/resolve/main/tokenizer.model"
    target_path = os.path.join(model_path, "tokenizer.model")
    
    urllib.request.urlretrieve(url, target_path)
    
    if os.path.exists(target_path):
        print(f"Downloaded tokenizer.model: {os.path.getsize(target_path)} bytes")
    else:
        print("Download failed")
        
except Exception as e:
    print(f"Download method failed: {e}")
    
    try:
        print("Trying to copy from existing ComfyUI tokenizer...")
        source_path = "/generic/path/ComfyUI/comfy/text_encoders/llama_tokenizer/tokenizer.model"
        target_path = os.path.join(model_path, "tokenizer.model")
        
        if os.path.exists(source_path):
            import shutil
            shutil.copy2(source_path, target_path)
            print(f"Copied tokenizer.model: {os.path.getsize(target_path)} bytes")
        else:
            print("Source tokenizer.model not found")
    except Exception as e2:
        print(f"Copy method also failed: {e2}")