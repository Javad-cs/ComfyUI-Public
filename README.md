# ComfyUI Workflows for Cog Deployment

This repository showcases modular ComfyUI workflows that I developed during my internship at SmoreTalk. They are optimized for deployment using Cog and are included here for portfolio and demonstration purposes.
Each workflow is self-contained inside its own folder, including all the files necessary to build, run, and test locally or remotely.

Workflows are primarily tested on Lambda Labs due to Docker permission issues in NHN Cloud.  
Each workflow folder includes all required components to quickly restore the environment.

---

## How to Use Any Workflow

To use a specific workflow from this repository:

1. Start by cloning the `cog-comfyui` base repository.

2. Choose a workflow folder from this repository. Inside that folder, you will find configuration files such as `predict.py`, `cog.yaml`, `requirements.txt`, `custom_nodes.json`, `weights.json`, and workflow API JSON file(s). Replace the corresponding files in your cloned `cog-comfyui` directory with the ones from your selected workflow folder.

3. Install the required Python dependencies listed in the workflow’s `requirements.txt` file.

4. Remove the existing `ComfyUI` folder in the cloned repository if it exists.

5. Clone the official ComfyUI repository into the same directory and install its requirements.

6. Run cog predict. (See in workflows folder on how to do it)

7. Then open the `predict.py` file and remove or comment out any lines related to `custom_nodes`.

8. Build your Cog project using the Cog CLI.

---

## Workflow-Specific Instructions

Each workflow folder includes:
- All files needed for Cog deployment
- A dedicated `README.md` with detailed usage instructions, input descriptions, output examples, and visual results

