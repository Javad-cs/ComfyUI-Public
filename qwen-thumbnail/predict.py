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
        # import shutil
        
        # subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/src/ComfyUI"], check=True)
        
        # print("Installing custom nodes...")
        # subprocess.run(["bash", "-c", "yes | python scripts/install_custom_nodes.py"], check=True)
        
        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)

    def update_workflow(self, workflow, **kwargs):
        """Update the Qwen thumbnail workflow with user inputs"""
        
        if "prompt" in kwargs:
            workflow["63"]["inputs"]["string_b"] = kwargs["prompt"]
        
        if "negative_prompt" in kwargs:
            workflow["31"]["inputs"]["text"] = kwargs["negative_prompt"]
        
        if "seed" in kwargs and kwargs["seed"] is not None:
            seed_value = kwargs["seed"]
            if seed_value == -1:
                seed_value = random.randint(0, 2**32 - 1)
            workflow["30"]["inputs"]["seed"] = seed_value
        
        if "width" in kwargs:
            workflow["40"]["inputs"]["width"] = kwargs["width"]
        
        if "height" in kwargs:
            workflow["40"]["inputs"]["height"] = kwargs["height"]
        
        return workflow

    def predict(
        self,
        prompt: str = Input(
            description="Main description for the thumbnail image",
            default="In a split scene, a caveman on the left and a futuristic humanoid robot on the right sit across from each other in a tense moment of silent understanding. The caveman is hunched and thoughtful inside a stone-walled cave, while the robot, sleek and glowing, sits in a clean sci-fi lab. Between them, a horizontal glowing text bar floats at table level with the word EVOLUTION clearly spelled in futuristic font. Blue light softly separates the two environments. The robot holds out a small glowing device, while the caveman looks at it curiously, symbolizing the passing of knowledge across time."
        ),
        style_prefix: str = Input(
            description="Style prefix for the image generation",
            default="Thumbnail style."
        ),
        negative_prompt: str = Input(
            description="Elements to avoid in generation",
            default="low quality, missing digits, extra digits, extra letters, missing letters"
        ),
        width: int = Input(
            description="Width of the generated image",
            default=1280,
            ge=256,
            le=2048
        ),
        height: int = Input(
            description="Height of the generated image", 
            default=720,
            ge=256,
            le=2048
        ),
        steps: int = Input(
            description="Number of denoising steps",
            default=20,
            ge=1,
            le=100
        ),
        cfg: float = Input(
            description="Classifier-free guidance scale",
            default=2.5,
            ge=1.0,
            le=20.0
        ),
        sampler_name: str = Input(
            description="Sampling method",
            default="euler",
            choices=["euler", "euler_ancestral", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "ddim", "uni_pc", "uni_pc_bh2"]
        ),
        scheduler: str = Input(
            description="Scheduler type",
            default="simple",
            choices=["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]
        ),
        shift: float = Input(
            description="Model sampling shift parameter",
            default=2.5,
            ge=0.1,
            le=10.0
        ),
        seed: int = Input(
            description="Seed for reproducible generation (-1 for random)",
            default=-1
        ),
    ) -> List[Path]:
        """Run Qwen Thumbnail generation workflow"""
        
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if os.path.exists(INPUT_DIR):
            shutil.rmtree(INPUT_DIR)
        os.makedirs(INPUT_DIR, exist_ok=True)

        with open("qwen_thumbnail_API.json", "r") as f:
            workflow = json.load(f)

        workflow = self.update_workflow(
            workflow,
            prompt=prompt,
            style_prefix=style_prefix,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg=cfg,
            sampler_name=sampler_name,
            scheduler=scheduler,
            shift=shift,
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