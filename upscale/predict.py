#!/usr/bin/env python3
import os
import json
import mimetypes
import shutil
import subprocess
from typing import List
from cog import BasePredictor, Input, Path
from comfyui import ComfyUI

OUTPUT_DIR = "/tmp/outputs"
INPUT_DIR = "/tmp/inputs"
COMFYUI_TEMP_OUTPUT_DIR = "ComfyUI/temp"

mimetypes.add_type("image/webp", ".webp")

class Predictor(BasePredictor):
    def setup(self):
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/src/ComfyUI"], check=True)
        
        print("Installing custom nodes...")
        subprocess.run(["bash", "-c", "yes | python scripts/install_custom_nodes.py"], check=True)
        
        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)

    def update_workflow(self, workflow, **kwargs):
        """Update the Real Upscale 8k workflow with user inputs"""
        
        if "image" in kwargs and kwargs["image"]:
            workflow["17"]["inputs"]["image"] = kwargs["image"]
        
        if "prompt" in kwargs:
            workflow["179"]["inputs"]["text"] = kwargs["prompt"]
        if "negative_prompt" in kwargs:
            workflow["199"]["inputs"]["text"] = kwargs["negative_prompt"]
        
        workflow["190"]["inputs"]["guidance"] = 3.5
        workflow["151:4"]["inputs"]["guidance"] = 3.5
        workflow["186:2"]["inputs"]["strength"] = 0.7
        workflow["142:1"]["inputs"]["strength"] = 0.8
        workflow["151:1"]["inputs"]["steps"] = 20
        workflow["109"]["inputs"]["steps"] = 8
        workflow["141:1"]["inputs"]["steps"] = 8
        workflow["109"]["inputs"]["denoise"] = 0.25
        
        if "seed" in kwargs:
            seed = kwargs["seed"]
            if seed == -1:
                import random
                seed = random.randint(0, 2**32 - 1)
        else:
            import random
            seed = random.randint(0, 2**32 - 1)
            
        workflow["151:2"]["inputs"]["noise_seed"] = seed
        workflow["141:1"]["inputs"]["seed"] = seed
        workflow["109"]["inputs"]["seed"] = seed
        
        workflow["136:0"]["inputs"]["max_width"] = 1024
        workflow["136:0"]["inputs"]["max_height"] = 1024
        workflow["143:2"]["inputs"]["max_width"] = 1536
        workflow["143:2"]["inputs"]["max_height"] = 1536
        
        if "resolution" in kwargs:
            resolution = kwargs["resolution"]
            if resolution == "2K":
                max_size = 2048
            elif resolution == "4K":
                max_size = 4096
            elif resolution == "8K":
                max_size = 8192
            else:
                max_size = 4096
                
            workflow["152:1"]["inputs"]["max_width"] = max_size
            workflow["152:1"]["inputs"]["max_height"] = max_size
            
        return workflow

    def predict(
        self,
        image: Path = Input(description="Image to upscale"),
        prompt: str = Input(
            description="What's in this image? (helps preserve details)",
            default="a high quality photograph"
        ),
        seed: int = Input(
            description="Seed for reproducible results (-1 for random)",
            default=-1
        ),
        resolution: str = Input(
            description="Output resolution",
            choices=["2K", "4K", "8K"],
            default="4K"
        ),
        negative_prompt: str = Input(
            description="Text prompt for features to avoid in the result (e.g., 'freckles, acne')",
            default="freckles, skin spots, blemishes, mole, acne"
        ),
    ) -> List[Path]:
        """Upscale your image to high resolution with AI"""
        
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        image_filename = f"input_image{os.path.splitext(image)[1]}"
        shutil.copy(image, os.path.join(INPUT_DIR, image_filename))

        with open("Real Upscale 8k.json", "r") as f:
            workflow = json.load(f)

        workflow = self.update_workflow(
            workflow,
            image=image_filename,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            resolution=resolution
        )

        wf = self.comfyUI.load_workflow(workflow)
        self.comfyUI.connect()
        self.comfyUI.run_workflow(wf)

        output_files = []
        
        output_locations = [OUTPUT_DIR, COMFYUI_TEMP_OUTPUT_DIR]
        
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