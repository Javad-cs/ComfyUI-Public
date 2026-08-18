#!/usr/bin/env python3
import os
import json
import mimetypes
import shutil
import random
from typing import List, Optional
from cog import BasePredictor, Input, Path
from comfyui import ComfyUI

OUTPUT_DIR = "/tmp/outputs"
INPUT_DIR = "/tmp/inputs"

mimetypes.add_type("image/webp", ".webp")

class Predictor(BasePredictor):
    def setup(self):
        import shutil
        import subprocess
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/src/ComfyUI"], check=True)
        print("Installing custom nodes...")
        subprocess.run(["bash", "-c", "yes | python scripts/install_custom_nodes.py"], check=True)

        self.patch_depth_anything()

        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)

    def patch_depth_anything(self):
        """Patch DepthAnything to fix device mismatch"""
        import fileinput
        import sys
        
        file_path = "/src/ComfyUI/custom_nodes/comfyui_controlnet_aux/src/custom_controlnet_aux/depth_anything/transformers.py"
        
        with open(file_path, 'r') as file:
            content = file.read()
        
        old_init = '''def __init__(self, model_name="LiheYoung/depth-anything-large-hf"):
            """Initialize DepthAnything with specified model."""
            self.pipe = pipeline(task="depth-estimation", model=model_name)
            self.device = "cpu"'''
        
        new_init = '''def __init__(self, model_name="LiheYoung/depth-anything-large-hf"):
            """Initialize DepthAnything with specified model."""
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.pipe = pipeline(task="depth-estimation", model=model_name, device=device)
            self.device = device'''
        
        content = content.replace(old_init, new_init)
        
        with open(file_path, 'w') as file:
            file.write(content)
        
        print("✅ Patched DepthAnything device issue")

    def get_workflow_file(self, mode):
        """Get the appropriate workflow file for the given mode"""
        workflow_files = {
            "upload": "interior_transfer_style_API.json",
            "generate": "interior_generate_style_API.json"
        }
        return workflow_files.get(mode, "interior_transfer_style_API.json")

    def update_workflow_upload_mode(self, workflow, **kwargs):
        """Update the workflow for upload mode (user provides style reference image)"""
        if "interior_image" in kwargs and kwargs["interior_image"]:
            workflow["100"]["inputs"]["image"] = kwargs["interior_image"]
 
        if "style_reference_image" in kwargs and kwargs["style_reference_image"]:
            workflow["159"]["inputs"]["image"] = kwargs["style_reference_image"]

        transfer_seed = kwargs.get("transfer_seed", -1)
        if transfer_seed == -1:
            transfer_seed = random.randint(0, 2**32 - 1)
        workflow["160"]["inputs"]["seed"] = transfer_seed

        return workflow

    def update_workflow_generate_mode(self, workflow, **kwargs):
        """Update the workflow for generate mode (generate style reference from prompt)"""
        if "interior_image" in kwargs and kwargs["interior_image"]:
            workflow["100"]["inputs"]["image"] = kwargs["interior_image"]

        if "style_prompt" in kwargs:
            workflow["86"]["inputs"]["text"] = kwargs["style_prompt"]

        generation_seed = kwargs.get("generation_seed", -1)
        if generation_seed == -1:
            generation_seed = random.randint(0, 2**32 - 1)
        workflow["83"]["inputs"]["seed"] = generation_seed

        transfer_seed = kwargs.get("transfer_seed", -1)
        if transfer_seed == -1:
            transfer_seed = random.randint(0, 2**32 - 1)
        workflow["95"]["inputs"]["seed"] = transfer_seed

        return workflow

    def predict(
        self,
        mode: str = Input(
            description="Choose mode: upload your own style reference image or generate from prompt",
            choices=["upload", "generate"],
            default="upload"
        ),
        interior_image: Path = Input(
            description="Interior image to transform (required for both modes)"
        ),
        style_reference_image: Path = Input(
            description="Style reference image (required only for upload mode)",
            default=None
        ),
        style_prompt: str = Input(
            description="Prompt to generate style reference (required only for generate mode)",
            default=""
        ),
        generation_seed: int = Input(
            description="Seed for initial image generation (-1 for random, only for generate mode)",
            default=-1
        ),
        transfer_seed: int = Input(
            description="Seed for style transfer stage (-1 for random)",
            default=-1
        ),
    ) -> List[Path]:
        """Run interior style transfer workflow"""
        
        if mode == "upload" and not style_reference_image:
            raise ValueError("Style reference image is required when mode is 'upload'")
        
        if mode == "generate" and not style_prompt.strip():
            raise ValueError("Style prompt is required when mode is 'generate'")

        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        interior_filename = "interior.jpeg"
        shutil.copy(interior_image, os.path.join(INPUT_DIR, interior_filename))

        if mode == "upload" and style_reference_image:
            style_filename = "interior1.jpg"  
            shutil.copy(style_reference_image, os.path.join(INPUT_DIR, style_filename))

        workflow_file = self.get_workflow_file(mode)
        
        with open(workflow_file, "r") as f:
            workflow = json.load(f)

        if mode == "upload":
            workflow = self.update_workflow_upload_mode(
                workflow,
                interior_image=interior_filename,
                style_reference_image=style_filename if style_reference_image else None,
                transfer_seed=transfer_seed
            )
        else:
            workflow = self.update_workflow_generate_mode(
                workflow,
                interior_image=interior_filename,
                style_prompt=style_prompt,
                generation_seed=generation_seed,
                transfer_seed=transfer_seed
            )

        wf = self.comfyUI.load_workflow(workflow)
        self.comfyUI.connect()
        self.comfyUI.run_workflow(wf)

        output_files = []
        output_locations = [OUTPUT_DIR]

        for location in output_locations:
            if os.path.exists(location):
                print(f"Checking location: {location}")
                for file in os.listdir(location):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        print(f"Found file: {file}")
                        src_path = os.path.join(location, file)
                        dst_path = os.path.join(OUTPUT_DIR, file)

                        if os.path.abspath(src_path) != os.path.abspath(dst_path):
                            shutil.copy(src_path, dst_path)

                        output_files.append(Path(dst_path))

        if not output_files:
            print("No output files found. Checking all directories:")
            for location in output_locations:
                if os.path.exists(location):
                    print(f"{location}: {os.listdir(location)}")
            raise Exception("No output files were generated. Check your workflow and inputs.")

        return output_files