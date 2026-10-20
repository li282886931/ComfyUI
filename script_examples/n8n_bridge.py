import asyncio
import base64
import sys
import os
from aiohttp import web

# Add parent directory to path to import comfy_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comfy_api.sdk import ComfyUIClient, apply_loras_to_prompt

# 默认 ComfyUI 地址
COMFY_SERVER = os.environ.get("COMFY_SERVER", "127.0.0.1:8188")

async def handle_generate(request):
    """
    接收 n8n 的 POST 请求，运行工作流并返回结果。
    支持在请求中动态添加 LoRA。
    """
    try:
        data = await request.json()
        prompt = data.get("prompt")
        loras = data.get("loras", []) # 新增：支持从 n8n 传入 LoRA 列表
        
        if not prompt:
            return web.json_response({"error": "Missing 'prompt' in request body"}, status=400)

        # 如果传入了 LoRA，自动注入到工作流中
        if loras:
            prompt = apply_loras_to_prompt(prompt, loras)

        async with ComfyUIClient(server_address=COMFY_SERVER) as client:
            # 运行工作流并等待结果
            results = await client.run_workflow(prompt)
            
            # 将结果转换为 base64，方便 n8n 处理
            output_data = []
            for node_id, images in results.items():
                for img_bytes in images:
                    output_data.append({
                        "node_id": node_id,
                        "image_base64": base64.b64encode(img_bytes).decode('utf-8')
                    })
            
            return web.json_response({
                "status": "success",
                "images": output_data
            })

    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def init_app():
    app = web.Application()
    app.router.add_post('/generate', handle_generate)
    return app

if __name__ == "__main__":
    print(f"Starting n8n bridge server on http://0.0.0.0:8000")
    print(f"Connecting to ComfyUI at {COMFY_SERVER}")
    web.run_app(init_app(), host='0.0.0.0', port=8000)
