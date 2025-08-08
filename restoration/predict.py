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
        import shutil
        
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/src/ComfyUI"], check=True)
        
        controlnet_aux_path = "ComfyUI/custom_nodes/comfyui_controlnet_aux"
        if os.path.exists(controlnet_aux_path):
            print("Removing corrupted comfyui_controlnet_aux...")
            shutil.rmtree(controlnet_aux_path)
        
        print("Installing custom nodes...")
        subprocess.run(["bash", "-c", "yes | python scripts/install_custom_nodes.py"], check=True)
        
        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)

    def update_workflow(self, workflow, **kwargs):
        """Update the VNRestore workflow with user inputs"""
        
        if "image" in kwargs and kwargs["image"]:
            workflow["10"]["inputs"]["image"] = kwargs["image"]
        
        if "prompt_prefix" in kwargs:
            workflow["60"]["inputs"]["text_a"] = kwargs["prompt_prefix"]
        
        if "prompt" in kwargs:
            workflow["60"]["inputs"]["text_b"] = kwargs["prompt"]
            
        if "prompt_suffix" in kwargs:
            workflow["60"]["inputs"]["text_c"] = kwargs["prompt_suffix"]
        
        if "likeness_level" in kwargs:
            workflow["61"]["inputs"]["value"] = kwargs["likeness_level"]
            
        if "blur_level" in kwargs:
            workflow["26"]["inputs"]["blur"] = kwargs["blur_level"]
            
        return workflow

    def predict(
        self,
        image: Path = Input(description="Input image to restore"),
        prompt: str = Input(
            description="Description of what the restored image should look like",
            default="old photograph of a person"
        ),
        prompt_prefix: str = Input(
            description="Text to add before the main prompt",
            default="a realistic colored photograph of"
        ),
        prompt_suffix: str = Input(
            description="Text to add after the main prompt", 
            default=", professional photography, bright natural ambient light, realistic texture"
        ),
        likeness_level: float = Input(
            description="Restoration strength/likeliness level (0.0-1.0)",
            default=0.6,
            ge=0.0,
            le=1.0
        ),
        blur_level: float = Input(
            description="Blur level applied to source image",
            default=2.0,
            ge=0.0
        ),
    ) -> List[Path]:
        """Run VNRestore image restoration workflow"""
        
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        image_filename = f"input_image{os.path.splitext(image)[1]}"
        shutil.copy(image, os.path.join(INPUT_DIR, image_filename))

        with open("VNRestore_Texturizer_API.json", "r") as f:
            workflow = json.load(f)

        workflow = self.update_workflow(
            workflow,
            image=image_filename,
            prompt=prompt,
            prompt_prefix=prompt_prefix,
            prompt_suffix=prompt_suffix,
            strength=likeness_level,
            blur_level=blur_level
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