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
        return "Pixar 3d Profile_API.json"

    def update_workflow(self, workflow, **kwargs):
        """Update the Pixar 3D workflow with user inputs"""
        
        if "input_image" in kwargs and kwargs["input_image"]:
            workflow["54"]["inputs"]["image"] = kwargs["input_image"]
        
        if "character_description" in kwargs:
            workflow["79"]["inputs"]["string_a"] = kwargs["character_description"]
            workflow["79"]["inputs"]["string_b"] = "Pixar style, breathtaking 3D cartoon rendering with cinematic lighting. Skin"
        
        if "width" in kwargs and "height" in kwargs:
            workflow["27"]["inputs"]["width"] = kwargs["width"]
            workflow["27"]["inputs"]["height"] = kwargs["height"]
        
        if "seed" in kwargs and kwargs["seed"] > 0:
            workflow["25"]["inputs"]["noise_seed"] = kwargs["seed"]
        
        if "face_restore_visibility" in kwargs:
            workflow["75"]["inputs"]["face_restore_visibility"] = kwargs["face_restore_visibility"]
        
        if "codeformer_weight" in kwargs:
            workflow["75"]["inputs"]["codeformer_weight"] = kwargs["codeformer_weight"]
        
        if "detect_gender_source" in kwargs:
            workflow["75"]["inputs"]["detect_gender_source"] = kwargs["detect_gender_source"]
        
        return workflow

    def predict(
        self,
        input_image: Path = Input(description="Input face image for reference (will be used for face swap)"),
        character_description: str = Input(
            description="Description of the character (appearance, clothing, pose, etc.)",
            default="A casually dressed man in his mid-20s. He wears a plain, fitted crewneck t-shirt in soft gray and a pair of straight-cut blue jeans. The jeans are slightly worn at the knees, giving a natural, everyday look. On his feet are clean white sneakers. He has an average build — not muscular, not skinny — and stands in a relaxed posture with his arms at his sides. His hair is short and slightly messy, and he carries no visible accessories or gear."
        ),
        width: int = Input(
            description="Output image width",
            default=1504,
            ge=512,
            le=2048
        ),
        height: int = Input(
            description="Output image height", 
            default=1504,
            ge=512,
            le=2048
        ),
        seed: int = Input(
            description="Seed for generation (-1 for random)",
            default=-1
        ),
        face_restore_visibility: float = Input(
            description="Face restore visibility (0.0 to 1.0)",
            default=1.0,
            ge=0.0,
            le=1.0
        ),
        codeformer_weight: float = Input(
            description="CodeFormer weight for face restoration (0.0 to 1.0)",
            default=0.5,
            ge=0.0,
            le=1.0
        ),
        detect_gender_source: str = Input(
            description="Detect gender source for face swapping",
            default="male",
            choices=["no", "male", "female"]
        ),
    ) -> List[Path]:
        """Run Pixar 3D profile generation workflow"""
        
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
            character_description=character_description,
            width=width,
            height=height,
            seed=seed,
            face_restore_visibility=face_restore_visibility,
            codeformer_weight=codeformer_weight,
            detect_gender_source=detect_gender_source
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