#!/usr/bin/env python3
import os
import json
import mimetypes
import shutil
import subprocess
import random
from typing import List
from cog import BasePredictor, Input, Path
from comfyui import ComfyUI

OUTPUT_DIR = "/tmp/outputs"
INPUT_DIR = "/tmp/inputs"
COMFYUI_TEMP_OUTPUT_DIR = "ComfyUI/temp"

mimetypes.add_type("image/webp", ".webp")

class Predictor(BasePredictor):
    def setup(self):
        import shutil
        
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/src/ComfyUI"], check=True)
        
        print("Installing custom nodes...")
        subprocess.run(["bash", "-c", "yes | python scripts/install_custom_nodes.py"], check=True)
        
        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)

    def update_workflow(self, workflow, **kwargs):
        """Update the text change workflow with user inputs"""
        
        if "original_text" in kwargs:
            workflow["210"]["inputs"]["value"] = kwargs["original_text"]
        
        if "new_text" in kwargs:
            workflow["212"]["inputs"]["value"] = kwargs["new_text"]
        
        if "seed" in kwargs and kwargs["seed"] is not None:
            seed_value = kwargs["seed"]
            if seed_value == -1:
                seed_value = random.randint(0, 2**32 - 1)
            workflow["31"]["inputs"]["seed"] = seed_value
        
        if "steps" in kwargs:
            workflow["31"]["inputs"]["steps"] = kwargs["steps"]
        
        if "cfg" in kwargs:
            workflow["31"]["inputs"]["cfg"] = kwargs["cfg"]
        
        if "guidance" in kwargs:
            workflow["35"]["inputs"]["guidance"] = kwargs["guidance"]
        
        return workflow

    def predict(
        self,
        image: Path = Input(
            description="Input image containing text to be changed"
        ),
        original_text: str = Input(
            description="The text currently visible in the image that you want to replace"
        ),
        new_text: str = Input(
            description="The new text you want to appear in place of the original text"
        ),
        steps: int = Input(
            description="Number of inference steps",
            default=20,
            ge=1,
            le=100
        ),
        cfg: float = Input(
            description="Classifier-free guidance scale",
            default=1.0,
            ge=0.1,
            le=20.0
        ),
        guidance: float = Input(
            description="Flux guidance scale",
            default=2.5,
            ge=0.1,
            le=10.0
        ),
        seed: int = Input(
            description="Seed for reproducible generation (-1 for random)",
            default=-1
        ),
    ) -> List[Path]:
        """Run Text Change Kontext workflow"""
        
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        input_image_path = os.path.join(INPUT_DIR, "input_image.jpg")
        shutil.copy(str(image), input_image_path)
        
        with open("Text Change Kontext_API.json", "r") as f:
            workflow = json.load(f)
        
        workflow["194"]["inputs"]["image"] = "input_image.jpg"

        workflow = self.update_workflow(
            workflow,
            original_text=original_text,
            new_text=new_text,
            steps=steps,
            cfg=cfg,
            guidance=guidance,
            seed=seed
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