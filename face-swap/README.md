<p float="left">
  <img src="example/before1.jpg" width="45%" />
  <img src="example/after1.png" width="45%" />
</p>

<p float="left">
  <img src="example/before2.jpg" width="45%" />
  <img src="example/after2.png" width="45%" />
</p>

&nbsp;

## Key Parameters

- `--original_image`: Path to original image with face mask (use mask editor to mark the face to replace) (**required**)
- `--face_image`: Path to new face image to swap in (**required**)
- `--prompt`: Instructions for face retention/modification (e.g., 'Retain face. Retain curly hair and hair color.')  
 _(default: `"Retain face. Keep natural skin tone and facial features."`)_
- `--seed`: Seed for reproducible generation  
 _(default: `-1` for random)_

 ---
 
## Usage Example

```bash
cog predict \
 -i original_image=@person_with_mask.jpg \
 -i face_image=@new_face.jpg \
 -i prompt="Retain face. Keep natural hair color and style." \
 -i seed=12345
 ```
 ---

# Notes
This workflow uses models that are not supported by default in `cog-comfyui`:

- `comfyui_portrait_lora64.safetensors` (stored under `loras`)
- `FLUX.1-Turbo-Alpha.safetensors` (stored under `loras`)

---

Looks like Replicate’s model list has an issue. It mentions flux1-Fill-Dev_FP8.safetensors, but that file doesn’t actually exist on their system. :)

---

There’s also a compatibility issue between comfyui_portrait_lora64.safetensors and FLUX.1-Turbo-Alpha.safetensors: one is based on FLUX.1-Fill-dev while the other uses FLUX.1-dev. I prioritized comfyui_portrait_lora64.safetensors instead. The results still look pretty good without FLUX.1-Turbo-Alpha.safetensors, as you can see.