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
        return "Replace product_API.json"

    def update_workflow(self, workflow, **kwargs):
        """Update the product replacement workflow with user inputs"""
        if "model_image" in kwargs and kwargs["model_image"]:
            workflow["758"]["inputs"]["image"] = kwargs["model_image"]
 
        if "product_image" in kwargs and kwargs["product_image"]:
            workflow["743"]["inputs"]["image"] = kwargs["product_image"]

        if "mask_prompt" in kwargs:
            workflow["791"]["inputs"]["text"] = kwargs["mask_prompt"]

        if "seed" in kwargs and kwargs["seed"] > 0:
            if "692" in workflow:
                workflow["692"]["inputs"]["seed"] = kwargs["seed"]

        return workflow

    def predict(
        self,
        model_image: Path = Input(description="Input model/background image where product will be replaced"),
        product_image: Path = Input(description="Input product image to replace with"),
        mask_prompt: str = Input(
            description="What to replace (e.g., 'product', 'bottle', 'phone')",
            default="product"
        ),
        seed: int = Input(
            description="Seed for generation (-1 for random)",
            default=-1
        ),
    ) -> List[Path]:
        """Run product replacement workflow"""
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        model_filename = f"model_image{os.path.splitext(model_image)[1]}"
        product_filename = f"product_image{os.path.splitext(product_image)[1]}"

        shutil.copy(model_image, os.path.join(INPUT_DIR, model_filename))
        shutil.copy(product_image, os.path.join(INPUT_DIR, product_filename))

        workflow_file = self.get_workflow_file("default")

        with open(workflow_file, "r") as f:
            workflow = json.load(f)

        workflow = self.update_workflow(
            workflow,
            model_image=model_filename,
            product_image=product_filename,
            mask_prompt=mask_prompt,
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