#!/usr/bin/env python3
import os
import json
import mimetypes
import shutil
from typing import List
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

        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)

    def get_workflow_file(self, resolution):
        """Get the appropriate workflow file for the given resolution"""
        return "blend-product-API.json"

    def update_workflow(self, workflow, **kwargs):
        """Update the product blending workflow with user inputs"""
        
        if "input_image" in kwargs and kwargs["input_image"]:
            workflow["223"]["inputs"]["image"] = kwargs["input_image"]
        
        if "prompt" in kwargs:
            workflow["6"]["inputs"]["text"] = kwargs["prompt"]
        
        if "megapixels" in kwargs:
            workflow["193"]["inputs"]["megapixels"] = kwargs["megapixels"]
        
        if "seed" in kwargs and kwargs["seed"] != -1:
            workflow["31"]["inputs"]["seed"] = kwargs["seed"]
        


        return workflow

    def predict(
        self,
        input_image: Path = Input(description="Input image to blend into background"),
        prompt: str = Input(
            description="Prompt describing how to blend the image",
            default="Fuse this image into background, remove white background"
        ),
        megapixels: float = Input(
            description="Output image resolution in megapixels",
            default=1.0,
            ge=0.5,
            le=4.0
        ),

        seed: int = Input(
            description="Seed for generation (-1 for random)",
            default=-1
        ),
    ) -> List[Path]:
        """Run product blending workflow"""
        
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        input_filename = f"input_image{os.path.splitext(input_image)[1]}"
        shutil.copy(input_image, os.path.join(INPUT_DIR, input_filename))

        workflow_file = self.get_workflow_file("default")
        with open(workflow_file, "r") as f:
            workflow = json.load(f)

        if seed == -1:
            import random
            seed = random.randint(0, 2**32 - 1)

        workflow = self.update_workflow(
            workflow,
            input_image=input_filename,
            prompt=prompt,
            megapixels=megapixels,
            seed=seed
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