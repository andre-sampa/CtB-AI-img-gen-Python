# img_gen.py
import sys
import os
import random
from huggingface_hub import InferenceClient
from datetime import datetime
from config.config import models, prompts, api_token  # Direct import

def generate(prompt_alias, team, model_alias, custom_prompt, height=360, width=640, num_inference_steps=20, guidance_scale=2.0, seed=-1):
    try:
        # Generate the image
        image_path, message = generate_image(prompt_alias, team, model_alias, custom_prompt, height, width, num_inference_steps, guidance_scale, seed)
        return image_path, message
    except Exception as e:
        return None, f"An error occurred: {e}"


def generate_image(prompt_alias, team, model_alias, custom_prompt, height=360, width=640, num_inference_steps=20, guidance_scale=2.0, seed=-1):
    # Find the selected prompt and model
    try:
        prompt = next(p for p in prompts if p["alias"] == prompt_alias)["text"]
        model_name = next(m for m in models if m["alias"] == model_alias)["name"]
    except StopIteration:
        return None, "ERROR: Invalid prompt or model selected."

    # Determine the enemy color
    enemy_color = "blue" if team.lower() == "red" else "red"
    prompt = prompt.format(enemy_color=enemy_color)

    if team.lower() == "red":
        prompt += " The winning army is dressed in red armor and banners."
    elif team.lower() == "blue":
        prompt += " The winning army is dressed in blue armor and banners."

    # Append the custom prompt (if provided)
    if custom_prompt and len(custom_prompt.strip()) > 0:
        prompt += " " + custom_prompt.strip()

    # Randomize the seed if needed
    if seed == -1:
        seed = random.randint(0, 1000000)

    # Initialize the InferenceClient
    try:
        client = InferenceClient(model_name, token=api_token)
    except Exception as e:
        return None, f"ERROR: Failed to initialize InferenceClient. Details: {e}"

     #Generate the image
    try:
        image = client.text_to_image(
            prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            width=width,
            height=height,
            seed=seed
        )
    except Exception as e:
        return None, f"ERROR: Failed to generate image. Details: {e}"

    # Save the image with a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{timestamp}_{model_alias.replace(' ', '_').lower()}_{prompt_alias.replace(' ', '_').lower()}_{team.lower()}.png"
    try:
        image.save(output_filename)
    except Exception as e:
        return None, f"ERROR: Failed to save image. Details: {e}"

    return output_filename, "Image generated successfully!"