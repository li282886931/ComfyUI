import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comfy_api.sdk import ComfyUIClient, apply_loras_to_prompt

async def main():
    # 基础工作流 (未包含 LoRA)
    base_prompt = {
        "3": {
            "inputs": {
                "seed": 888,
                "steps": 20,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {"inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}, "class_type": "CheckpointLoaderSimple"},
        "5": {"inputs": {"width": 1024, "height": 1024, "batch_size": 1}, "class_type": "EmptyLatentImage"},
        "6": {"inputs": {"text": "a cybernetic cat, neon lights, highly detailed", "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "7": {"inputs": {"text": "low quality", "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
        "9": {"inputs": {"filename_prefix": "Lora_Test", "images": ["8", 0]}, "class_type": "SaveImage"}
    }

    # 定义要加载的 LoRA 列表
    loras = [
        {"name": "cyberpunk_style_v1.safetensors", "strength_model": 0.8, "strength_clip": 0.8},
        {"name": "more_details.safetensors", "strength_model": 0.5, "strength_clip": 0.5}
    ]

    # 使用助手函数自动注入 LoRA 节点并更新引用
    final_prompt = apply_loras_to_prompt(base_prompt, loras)

    async with ComfyUIClient() as client:
        print("Starting workflow with LoRAs...")
        try:
            results = await client.run_workflow(final_prompt)
            print(f"Generation complete. Results: {list(results.keys())}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
