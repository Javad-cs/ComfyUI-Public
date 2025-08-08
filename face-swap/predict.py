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

    def get_workflow_file(self):
        """Get the face swap workflow file"""
        return "FaceSwap_API.json"

    def update_workflow(self, workflow, **kwargs):
        """Update the face swap workflow with user inputs"""
        if "original_image" in kwargs and kwargs["original_image"]:
            workflow["239"]["inputs"]["image"] = kwargs["original_image"]

        if "face_image" in kwargs and kwargs["face_image"]:
            workflow["240"]["inputs"]["image"] = kwargs["face_image"]

        if "prompt" in kwargs:
            workflow["343"]["inputs"]["text"] = kwargs["prompt"]

        if "seed" in kwargs and kwargs["seed"] > 0:
            if "346" in workflow:
                workflow["346"]["inputs"]["seed"] = kwargs["seed"]

        return workflow

    def predict(
        self,
        original_image: Path = Input(description="Original image with face mask (use mask editor to mark the face to replace)"),
        face_image: Path = Input(description="New face image to swap in"),
        prompt: str = Input(
            description="Instructions for face retention/modification (e.g., 'Retain face. Retain curly hair and hair color.')",
            default="Retain face. Keep natural skin tone and facial features."
        ),
        seed: int = Input(
            description="Seed for generation (-1 for random)",
            default=-1
        ),
    ) -> List[Path]:
        """Run face swap workflow"""
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        original_filename = f"original_image{os.path.splitext(original_image)[1]}"
        face_filename = f"face_image{os.path.splitext(face_image)[1]}"

        shutil.copy(original_image, os.path.join(INPUT_DIR, original_filename))
        shutil.copy(face_image, os.path.join(INPUT_DIR, face_filename))

        workflow_file = self.get_workflow_file()

        with open(workflow_file, "r") as f:
            workflow = json.load(f)

        workflow = self.update_workflow(
            workflow,
            original_image=original_filename,
            face_image=face_filename,
            prompt=prompt,
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