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
        """Update the comics workflow with user inputs"""
        
        if "reference_image" in kwargs and kwargs["reference_image"]:
            workflow["43"]["inputs"]["image"] = kwargs["reference_image"]
        
        if "positive_prompt" in kwargs:
            workflow["6"]["inputs"]["text"] = kwargs["positive_prompt"]
        
        if "negative_prompt" in kwargs:
            workflow["33"]["inputs"]["text"] = kwargs["negative_prompt"]
        
        panel_prompt_mappings = {
            "panel_1_prompt": "89",
            "panel_2_prompt": "112", 
            "panel_3_prompt": "114",
            "panel_4_prompt": "137",
            "panel_5_prompt": "142",
            "panel_6_prompt": "151"
        }
        
        for param_name, node_id in panel_prompt_mappings.items():
            if param_name in kwargs and kwargs[param_name]:
                workflow[node_id]["inputs"]["text"] = kwargs[param_name]
        
        seed_mappings = {
            "main_seed": "31",  
            "panel_1_seed": "92",  
            "panel_2_seed": "108",
            "panel_3_seed": "118", 
            "panel_4_seed": "136",
            "panel_5_seed": "143",
            "panel_6_seed": "150"
        }
        
        for param_name, node_id in seed_mappings.items():
            if param_name in kwargs and kwargs[param_name] is not None:
                workflow[node_id]["widgets_values"][0] = kwargs[param_name]
        
        return workflow

    def predict(
        self,
        reference_image: Path = Input(
            description="Reference image for character consistency across all panels"
        ),
        positive_prompt: str = Input(
            description="Main character description used as base for all panels",
            default=""
        ),
        negative_prompt: str = Input(
            description="Elements to avoid in generation",
            default=""
        ),
        panel_1_prompt: str = Input(
            description="Scene description for Panel 1 (Morning wake-up scene)"
        ),
        panel_2_prompt: str = Input(
            description="Scene description for Panel 2 (Subway commute scene)"
        ),
        panel_3_prompt: str = Input(
            description="Scene description for Panel 3 (Office work scene)"
        ),
        panel_4_prompt: str = Input(
            description="Scene description for Panel 4 (Shooting range scene)"
        ),
        panel_5_prompt: str = Input(
            description="Scene description for Panel 5 (Evening relaxation scene)"
        ),
        panel_6_prompt: str = Input(
            description="Scene description for Panel 6 (Night sleep scene)"
        ),
        main_seed: int = Input(
            description="Seed for main character generation",
            default=-1
        ),
        panel_1_seed: int = Input(
            description="Seed for Panel 1 generation",
            default=-1
        ),
        panel_2_seed: int = Input(
            description="Seed for Panel 2 generation", 
            default=-1
        ),
        panel_3_seed: int = Input(
            description="Seed for Panel 3 generation",
            default=-1
        ),
        panel_4_seed: int = Input(
            description="Seed for Panel 4 generation",
            default=-1
        ),
        panel_5_seed: int = Input(
            description="Seed for Panel 5 generation",
            default=-1
        ),
        panel_6_seed: int = Input(
            description="Seed for Panel 6 generation",
            default=-1
        ),
    ) -> List[Path]:
        """Run Comics generation workflow"""
        
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        reference_image_filename = f"reference_image{os.path.splitext(reference_image)[1]}"
        shutil.copy(reference_image, os.path.join(INPUT_DIR, reference_image_filename))

        with open("Comics_API.json", "r") as f:
            workflow = json.load(f)

        workflow = self.update_workflow(
            workflow,
            reference_image=reference_image_filename,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            panel_1_prompt=panel_1_prompt,
            panel_2_prompt=panel_2_prompt,
            panel_3_prompt=panel_3_prompt,
            panel_4_prompt=panel_4_prompt,
            panel_5_prompt=panel_5_prompt,
            panel_6_prompt=panel_6_prompt,
            main_seed=main_seed,
            panel_1_seed=panel_1_seed,
            panel_2_seed=panel_2_seed,
            panel_3_seed=panel_3_seed,
            panel_4_seed=panel_4_seed,
            panel_5_seed=panel_5_seed,
            panel_6_seed=panel_6_seed
        )

        # Run the workflow
        wf = self.comfyUI.load_workflow(workflow)
        self.comfyUI.connect()
        self.comfyUI.run_workflow(wf)

        # Collect output files
        output_files = []
        
        # Check both OUTPUT_DIR and ComfyUI temp directory
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