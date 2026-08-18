<p float="left">
  <img src="example/after1.png" width="45%" />
  <img src="example/after2.png" width="45%" />
</p>

<p float="left">
  <img src="example/after3.png" width="45%" />
  <img src="example/after4.png" width="45%" />
</p>

&nbsp;

# Key Parameters

- `--prompt`: Main description for the image with text elements (**required**)
- `--negative_prompt`: Elements to avoid in generation  
_(default: `""`)_
- `--width`: Width of the generated image  
_(default: `1280`)_
- `--height`: Height of the generated image  
_(default: `720`)_
- `--seed`: Seed for reproducible generation  
_(default: `-1` for random)_

---

# Usage Example

```bash
cog predict \
-i prompt="A cartoonish professor with messy hair and round glasses stands in front of a chalkboard filled with doodles and math formulas. Bright, clear lighting and a shallow depth of field." \
-i negative_prompt="" \
-i width=1280 \
-i height=720 \
-i seed=755378908169739
```
---

# Notes
This workflow uses models that are not supported by default in `cog-comfyui`:
- `qwen_image_vae.safetensors` (stored under `vae`)
- `qwen_image_fp8_e4m3fn.safetensors` (stored under `diffusion_models`)
- `qwen_2.5_vl_7b_fp8_scaled.safetensors` (stored under `text_encoders`)