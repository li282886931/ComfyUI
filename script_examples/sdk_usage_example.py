import asyncio
import sys
import os

# Add parent directory to path to import comfy_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comfy_api.sdk import ComfyUIClient

async def main():
    # 示例工作流 (简单的文本生成图片)
    # 注意：这里的节点 ID 和参数需要根据你实际的 ComfyUI 环境调整
    prompt = {
        "3": {
            "inputs": {
                "seed": 156680208700286,
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
        "4": {
            "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"},
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {"width": 512, "height": 512, "batch_size": 1},
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {"text": "a beautiful landscape, mountain, sunset", "clip": ["4", 1]},
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {"text": "bad quality, blurry", "clip": ["4", 1]},
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {"filename_prefix": "SDK_Output", "images": ["8", 0]},
            "class_type": "SaveImage"
        }
    }

    async with ComfyUIClient(server_address="127.0.0.1:8188") as client:
        print("Starting workflow...")
        try:
            results = await client.run_workflow(prompt)
            
            for node_id, images in results.items():
                print(f"Node {node_id} generated {len(images)} images.")
                for i, img_bytes in enumerate(images):
                    filename = f"output_{node_id}_{i}.png"
                    with open(filename, "wb") as f:
                        f.write(img_bytes)
                    print(f"Saved: {filename}")
                    
        except Exception as e:
            print(f"Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
