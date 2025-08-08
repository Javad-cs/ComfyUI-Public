<p float="left">
 <img src="example/before.jpg" width="45%" />
 <img src="example/after.png" width="45%" />
</p>

&nbsp;

# Key Parameters

- `--image`: Input image containing text to be changed (**required**)
- `--original_text`: The text currently visible in the image that you want to replace (**required**)
- `--new_text`: The new text you want to appear in place of the original text (**required**)
- `--steps`: Number of inference steps  
_(default: `20`)_
- `--cfg`: Classifier-free guidance scale  
_(default: `1.0`)_
- `--guidance`: Flux guidance scale  
_(default: `2.5`)_
- `--seed`: Seed for reproducible generation  
_(default: `-1` for random)_

---

# Usage Example

```bash
cog predict \
-i image=@input_image.jpg \
-i original_text="BOOM!" \
-i new_text="ComfyUI" \
-i steps=20 \
-i cfg=1.0 \
-i guidance=2.5 \
-i seed=12345
```
---

# Notes
This workflow uses model that are not supported by default in `cog-comfyui`:
- `flux1-dev-kontext_fp8_scaled.safetensors` (stored under `diffusion_models`)