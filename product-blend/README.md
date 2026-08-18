<p float="left">
 <img src="example/before.png" width="45%" />
 <img src="example/after.png" width="45%" />
</p>

&nbsp;

## Key Parameters

- `--input_image`: Path to image to blend into background (**required**)
- `--prompt`: Description of how to blend the image    
 _(default: `"Fuse this image into background, remove white background"`)_
- `--megapixels`: Output image resolution in megapixels    
 _(default: `1.0`, range: 0.5-4.0)_
- `--seed`: Seed for reproducible generation    
 _(default: `-1` for random)_

---

# Usage Example

```bash
cog predict \
 -i input_image=@product_bottle.png \
 -i prompt="Seamlessly blend this product into the kitchen scene, natural lighting" \
 -i megapixels=2.0 \
 -i seed=12345
 ```
---

# Notes
This workflow uses model that are not supported by default in `cog-comfyui`:
- `flux1-dev-kontext_fp8_scaled.safetensors` (stored under `diffusion_models`)
- `WVVtJFD90b8SsU6EzeGkO_adapter_model_comfy_converted.safetensors` (stored under `loras`)