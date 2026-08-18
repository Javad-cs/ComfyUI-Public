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
        workflow_files = {
            "1344": "Change clothes_1344_API.json",
            "1536": "Change clothes_API.json",
            "1920": "Change clothes_1920_API.json",
            "2048": "Change clothes_API_2048.json"
        }
        return workflow_files.get(resolution, "Change clothes_API.json")

    def update_workflow(self, workflow, **kwargs):
        """Update the clothes change workflow with user inputs"""
        if "model_image" in kwargs and kwargs["model_image"]:
            workflow["405"]["inputs"]["image"] = kwargs["model_image"]

        if "clothes_image" in kwargs and kwargs["clothes_image"]:
            workflow["368"]["inputs"]["image"] = kwargs["clothes_image"]

        if "mask_prompt" in kwargs:
            workflow["578"]["inputs"]["text"] = kwargs["mask_prompt"]

        if "description" in kwargs:
            workflow["197"]["inputs"]["text"] = kwargs["description"]

        if "539" in workflow and "inputs" in workflow["539"]:
            workflow["539"]["inputs"]["any_01"] = ["534", 0]

        if "lora_cloth_weight" in kwargs and "580" in workflow:
            workflow["580"]["inputs"]["strength_model"] = kwargs["lora_cloth_weight"]

        if "lora_subject_weight" in kwargs and "582" in workflow:
            workflow["582"]["inputs"]["strength_model"] = kwargs["lora_subject_weight"]

        if "seed" in kwargs and kwargs["seed"] > 0:
            if "560" in workflow:
                workflow["560"]["inputs"]["seed"] = kwargs["seed"]
            if "234" in workflow:
                workflow["234"]["inputs"]["seed"] = kwargs["seed"]

        return workflow

    def predict(
        self,
        model_image: Path = Input(description="Input model/person image"),
        clothes_image: Path = Input(description="Input clothes/costume image"),
        mask_prompt: str = Input(
            description="Mask prompt for automatic segmentation (leave empty for manual mask)",
            default="clothes"
        ),
        description: str = Input(
            description="Additional description for better results",
            default="32K UHD, ultra-high resolution, extremely sharp, intricate details, masterpiece, realistic, Clothes wrinkle naturally"
        ),
        resolution: str = Input(
            description="Output resolution",
            choices=["1344", "1536", "1920", "2048"],
            default="1536"
        ),
        lora_cloth_weight: float = Input(
            description="LoRA weight for clothes migration (0.0-1.0)",
            default=0.0,
            ge=0.0,
            le=1.0
        ),
        lora_subject_weight: float = Input(
            description="LoRA weight for subject (0.0-1.0)",
            default=1.0,
            ge=0.0,
            le=1.0
        ),
        seed: int = Input(
            description="Seed for generation (-1 for random)",
            default=-1
        ),
    ) -> List[Path]:
        """Run clothes change workflow"""
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        model_filename = f"model_image{os.path.splitext(model_image)[1]}"
        clothes_filename = f"clothes_image{os.path.splitext(clothes_image)[1]}"

        shutil.copy(model_image, os.path.join(INPUT_DIR, model_filename))
        shutil.copy(clothes_image, os.path.join(INPUT_DIR, clothes_filename))

        workflow_file = self.get_workflow_file(resolution)

        with open(workflow_file, "r") as f:
            workflow = json.load(f)

        workflow = self.update_workflow(
            workflow,
            model_image=model_filename,
            clothes_image=clothes_filename,
            mask_prompt=mask_prompt,
            description=description,
            lora_cloth_weight=lora_cloth_weight,
            lora_subject_weight=lora_subject_weight,
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
