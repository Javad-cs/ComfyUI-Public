<p float="left">
  <img src="example/before.jpg" width="45%" />
  <img src="example/after.png" width="45%" />
</p>

&nbsp;

# Key Parameters

- `--image`: Path to input image (**required**)
- `--prompt`: Main restoration prompt (**required**)
- `--prompt_prefix`: Prompt prefix  
  _(default: `"a realistic colored photograph of"`)_
- `--prompt_suffix`: Prompt suffix  
  _(default: `", professional photography, bright natural ambient light, realistic texture"`)_
- `--likeness_level`: Restoration strength/likeness level (range: `0.0`–`1.0`)  
  _(default: `0.6`)_
- `--blur_level`: Blur level applied to source image  
  _(default: `2.0`)_

---

# Usage Example

```bash
cog predict \
  -i image=@old_p.jpeg \
  -i prompt="elderly Azerbaijani woman from 1890s with traditional clothing" \
  -i prompt_prefix="a high quality restored photograph of" \
  -i prompt_suffix=", professional restoration, enhanced details, natural lighting, photorealistic" \
  -i likeness_level=0.7 \
  -i blur_level=1.5
  ```
---

# Notes

This workflow uses models that are not supported by default in `cog-comfyui`:

- `RealVisXL_V5.0_Lightning_fp16.safetensors` (stored under `checkpoints`)
- `xinsir-controlnet-union-sdxl-1.0-promax.safetensors` (stored under `controlnet`)

---

# Optional Cleanup (Reduce Disk Usage)

To save space and avoid unnecessary loading of unused models, you can safely delete the following depth checkpoint files:

```bash
rm -rf ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Giant
rm -rf ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Metric-VKITTI-Large
rm -rf ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Metric-Hypersim-Large
rm -rf ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Base
rm -rf ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/depth-anything/Depth-Anything-V2-Small
```
Only `Depth-Anything-V2-ViT-Large (vitl)` is used in this workflow.

---

# Code Cleanup (ControlNet Aux Helper)

To avoid loading unused depth models, open custom_node_helpers/ComfyUI_controlnet_Aux.py, and delete lines 111–115 that lists multiple depth model filenames. Keep only "depth_anything_v2_vitl.pth". This is the only depth model used in this workflow.
Removing the others avoids unnecessary file loading and speeds up initialization.
