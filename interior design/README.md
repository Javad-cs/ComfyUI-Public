<p float="left">
  <img src="example/before1.png" width="30%" />
  <img src="example/input.png" width="30%" />
  <img src="example/after1.png" width="30%" />
</p>

<p float="left">
  <img src="example/before2.png" width="30%" />
  <img src="example/generated_input.png" width="30%" />
  <img src="example/after2.png" width="30%" />
</p>

&nbsp;

## Key Parameters

- `--mode`: Choose between "upload" (use your style image) or "generate" (create from prompt) (**required**) _[Only aviable when predict_both_modes.py used]_
- `--interior_image`: Path to interior image to transform (**required**)
- `--style_reference_image`: Path to style reference image (**required for upload mode**)
- `--style_prompt`: Text prompt to generate style reference (**required for generate mode**)
- `--generation_seed`: Seed for initial image generation (generate mode only)  
 _(default: `-1` for random)_
- `--transfer_seed`: Seed for style transfer stage  
 _(default: `-1` for random)_

---

# Usage Examples when predict_both_modes.py used

## Upload Mode (Use Your Style Image) 
```bash
cog predict \
 -i mode="upload" \
 -i interior_image=@living_room.jpg \
 -i style_reference_image=@art_style.jpg \
 -i transfer_seed=12345
 ```

## Generate Mode (Create Style from Prompt)
```bash
cog predict \
  -i mode="generate" \
  -i interior_image=@living_room.jpg \
  -i style_prompt="modern minimalist scandinavian design, white walls, natural wood" \
  -i generation_seed=67890 \
  -i transfer_seed=12345
 ```

# Usage Examples when predict.py used
```bash
cog predict \
 -i interior_image=@living_room.jpg \
 -i style_reference_image=@art_style.jpg \
 -i transfer_seed=12345
 ```


# Notes
This workflow uses models that are not supported by default in `cog-comfyui`:

- `depth_anything_vitl14.pth` (stored under `depthanything`)

---

Setup() part of predict.py was written in a way that it automatically patches comfyui_controlnet_aux to resolve GPU device mismatch issues with the DepthAnything depth preprocessor. This ensures proper CUDA device initialization and prevents RuntimeError: Input type (torch.FloatTensor) and weight type (torch.cuda.FloatTensor) should be the same errors during workflow execution.

---

Due to memory limitationa and NFSW issue of generation modeld used, the cog container only with predict.py file was deployed which omits generation stage.

---

When using this workflow, try inputting high quality images. 

