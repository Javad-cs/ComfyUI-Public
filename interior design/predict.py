#!/usr/bin/env python3
import os
import json
import mimetypes
import shutil
import random
from typing import List
from cog import BasePredictor, Input, Path
from comfyui import ComfyUI

OUTPUT_DIR = "/tmp/outputs"
INPUT_DIR = "/tmp/inputs"

mimetypes.add_type("image/webp", ".webp")

class Predictor(BasePredictor):
    def setup(self):
        import subprocess
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/src/ComfyUI"], check=True)
        print("Installing custom nodes...")
        subprocess.run(["bash", "-c", "yes | python scripts/install_custom_nodes.py"], check=True)

        self.patch_depth_anything()

        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)

    def patch_depth_anything(self):
        """Patch DepthAnything to fix device mismatch"""
        file_path = "/src/ComfyUI/custom_nodes/comfyui_controlnet_aux/src/custom_controlnet_aux/depth_anything/transformers.py"
        
        try:
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
            
            if old_init in content:
                content = content.replace(old_init, new_init)
                
                with open(file_path, 'w') as file:
                    file.write(content)
                
                print("✅ Patched DepthAnything device issue")
            else:
                print("DepthAnything patch not needed or already applied")
        except Exception as e:
            print(f"Could not patch DepthAnything: {e}")

    def predict(
        self,
        interior_image: Path = Input(
            description="Interior image to transform"
        ),
        style_reference_image: Path = Input(
            description="Style reference image to apply to the interior"
        ),
        transfer_seed: int = Input(
            description="Seed for style transfer (-1 for random)",
            default=-1
        ),
    ) -> List[Path]:
        """Run interior style transfer workflow with uploaded style reference image"""
        
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        interior_filename = "interior.jpeg"
        style_filename = "interior1.jpg"
        
        shutil.copy(interior_image, os.path.join(INPUT_DIR, interior_filename))
        shutil.copy(style_reference_image, os.path.join(INPUT_DIR, style_filename))

        with open("interior_transfer_style_API.json", "r") as f:
            workflow = json.load(f)

        workflow["100"]["inputs"]["image"] = interior_filename
        workflow["159"]["inputs"]["image"] = style_filename

        if transfer_seed == -1:
            transfer_seed = random.randint(0, 2**32 - 1)
        workflow["160"]["inputs"]["seed"] = transfer_seed

        wf = self.comfyUI.load_workflow(workflow)
        self.comfyUI.connect()
        self.comfyUI.run_workflow(wf)

        output_files = []
        
        if os.path.exists(OUTPUT_DIR):
            print(f"Checking location: {OUTPUT_DIR}")
            for file in os.listdir(OUTPUT_DIR):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    print(f"Found file: {file}")
                    file_path = os.path.join(OUTPUT_DIR, file)
                    
                    file_path = str(os.path.abspath(file_path))
                    output_files.append(Path(file_path))

        if not output_files:
            print("No output files found. Checking all directories:")
            if os.path.exists(OUTPUT_DIR):
                print(f"{OUTPUT_DIR}: {os.listdir(OUTPUT_DIR)}")
            raise Exception("No output files were generated. Check your workflow and inputs.")

        return output_files