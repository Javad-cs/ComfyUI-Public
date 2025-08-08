<p float="left">
  <img src="example/before.jpg" width="45%" />
  <img src="example/after.png" width="45%" />
</p>

&nbsp;

# Key Parameters

- `--image`: Path to input image (**required**)
- `--prompt`: Description of what’s in the image to help with detail preservation  
  _(default: `"a high quality photograph"`)_
- `--negative_prompt`: Features to avoid in the result (e.g., `"freckles, acne"`)  
  _(default: `"freckles, skin spots, blemishes, mole, acne"`)_
- `--resolution`: Output resolution (choices: `2K`, `4K`, `8K`)  
  _(default: `"4K"`)_
- `--seed`: Seed for reproducible results (`-1` for random)  
  _(default: `-1`)_

---

# Usage Example

```bash
cog predict \
  -i image=@your_input_image.jpg \
  -i prompt="a detailed portrait of a person wearing traditional clothing" \
  -i negative_prompt="freckles, acne, blemishes, skin spots" \
  -i seed=12345 \
  -i resolution="8K"
  ```
---

# Notes

This workflow uses models that are not supported by default in `cog-comfyui`:

- `STOIQONewrealityFLUXSD_F1DAlpha.safetensors` (stored under `checkpoints`)
- `ViT-L-14-BEST-smooth-GmP-TE-only-HF-format.safetensors` (stored under `clip`)
- `diffusion_pytorch_model.safetensors` (stored under `controlnet`)

