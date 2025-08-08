<p float="left">
 <img src="example/before.jpg" width="30%" />
 <img src="example/ref1.jpg" width="30%" />
 <img src="example/after1.png" width="30%" />
</p>

<p float="left">
 <img src="example/before.jpg" width="30%" />
 <img src="example/ref2.jpg" width="30%" />
 <img src="example/after2.png" width="30%" />
</p>

&nbsp;

## Key Parameters

- `--product_image`: Path to product image to change background for (**required**)
- `--reference_image`: Reference image showing desired place/style/background (**required**)
- `--positive_prompt`: Description of desired background and lighting    
 _(default: `"commercial photo, perfect lighting, product photo, photorealistic, super sharp, super noise reduction"`)_
- `--negative_prompt`: What to avoid in generation    
 _(default: `"(noise, blur, worst quality, low quality, error, cropped, bad anatomy, bad proportions, wrong hands)\n(NSFW, nude)"`)_
- `--width`: Output image width in pixels    
 _(default: `1024`, range: 512-2048)_
- `--height`: Output image height in pixels    
 _(default: `1024`, range: 512-2048)_
- `--seed`: Seed for reproducible generation    
 _(default: `-1` for random)_

---

# Usage Example

```bash
cog predict \
 -i product_image=@bottle.png \
 -i reference_image=@kitchen_scene.jpg \
 -i positive_prompt="modern kitchen environment, natural lighting, professional product photography" \
 -i negative_prompt="cluttered, dark, blurry, low quality" \
 -i width=1024 \
 -i height=1024 \
 -i seed=12345
 ```

 ---

 # Notes
This workflow uses model that are not supported by default in `cog-comfyui`:
- `RMBG-1.4` (stored under `rembg`)
- `iclight_sd15_fc.safetensors` (stored under `diffusion_models`)