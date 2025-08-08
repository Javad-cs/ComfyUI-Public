<p float="left">
  <img src="example/before1.webp" width="30%" />
  <img src="example/before2.png" width="30%" />
  <img src="example/after.png" width="30%" />
</p>

&nbsp;

## Key Parameters

- `--model_image`: Path to background/scene image where product will be replaced (**required**)
- `--product_image`: Path to new product image to insert (**required**)
- `--mask_prompt`: What to replace (e.g., 'product', 'bottle', 'phone')  
 _(default: `"product"`)_
- `--seed`: Seed for reproducible generation  
 _(default: `-1` for random)_

 ---

 # Usage Example

 ```bash
cog predict \
 -i model_image=@kitchen_scene.jpg \
 -i product_image=@new_bottle.png \
 -i mask_prompt="bottle" \
 -i seed=12345
   ```
---

# Notes
This workflow uses models that are not supported by default in `cog-comfyui`:

- `comfyui_subject_lora16.safetensors` (stored under `loras`)
- `deepseek-ai/Janus-Pro-1B` (stored under `Janus-Pro`)
- `ViT-L-14-BEST-smooth-GmP-TE-only-HF-format.safetensors` (stored under `text_encoders`)

---

 Modern Janus-Pro model uses tokenizer.json format, but the ComfyUI node expects legacy SentencePiece tokenizer.model. To solve issue, I created missing tokenizer.model by downloading compatible file from Llama-2 model.

---

Had to manually install t5xxl_fp8_e4m3fn.safetensors in cog.yaml even though it exists in the list casue it was taking very long time to load. 

---

Also manually clone and install requirements of ""https://github.com/deepseek-ai/Janus" and "https://github.com/CY-CHENYUE/ComfyUI-Janus-Pro", they don't have init.py that's why cog gets confused.