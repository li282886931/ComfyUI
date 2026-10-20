import asyncio
import json
import uuid
import aiohttp
import logging
from typing import Dict, Any, List, Optional

class ComfyUIClient:
    """
    A high-level asynchronous SDK for interacting with ComfyUI.
    """
    def __init__(self, server_address: str = "127.0.0.1:8188", client_id: Optional[str] = None):
        self.server_address = server_address
        self.client_id = client_id or str(uuid.uuid4())
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.logger = logging.getLogger("ComfyUIClient")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        """Establishes HTTP session and WebSocket connection."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        ws_url = f"ws://{self.server_address}/ws?clientId={self.client_id}"
        self.ws = await self.session.ws_connect(ws_url)
        self.logger.info(f"Connected to ComfyUI at {self.server_address}")

    async def close(self):
        """Closes connections."""
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()

    async def queue_prompt(self, prompt: Dict[str, Any]) -> str:
        """Queues a prompt and returns the prompt_id."""
        url = f"http://{self.server_address}/prompt"
        payload = {"prompt": prompt, "client_id": self.client_id}
        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"Failed to queue prompt: {text}")
            result = await response.json()
            return result['prompt_id']

    async def get_image(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """Downloads an image from ComfyUI."""
        url = f"http://{self.server_address}/view"
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"Failed to get image: {await response.text()}")
            return await response.read()

    async def get_history(self, prompt_id: str) -> Dict[str, Any]:
        """Gets execution history for a specific prompt_id."""
        url = f"http://{self.server_address}/history/{prompt_id}"
        async with self.session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to get history: {await response.text()}")
            result = await response.json()
            return result.get(prompt_id, {})

    async def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> Dict[str, List[bytes]]:
        """
        Wait for a prompt to complete via WebSocket and return the generated images.
        """
        self.logger.info(f"Waiting for prompt {prompt_id} to complete...")

        start_time = asyncio.get_event_loop().time()
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Prompt {prompt_id} timed out after {timeout} seconds")

            msg = await self.ws.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if data['type'] == 'executing':
                    exec_data = data['data']
                    if exec_data['node'] is None and exec_data['prompt_id'] == prompt_id:
                        break # Execution finished
            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                raise Exception("WebSocket connection closed or error occurred")

        # Fetch history to get output details
        history = await self.get_history(prompt_id)
        outputs = history.get('outputs', {})

        result_images = {}
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                images_data = []
                for img_info in node_output['images']:
                    img_bytes = await self.get_image(
                        img_info['filename'],
                        img_info['subfolder'],
                        img_info['type']
                    )
                    images_data.append(img_bytes)
                result_images[node_id] = images_data

        return result_images

    async def run_workflow(self, prompt: Dict[str, Any], timeout: int = 300) -> Dict[str, List[bytes]]:
        """
        High-level helper to queue a prompt and wait for results in one call.
        """
        prompt_id = await self.queue_prompt(prompt)
        return await self.wait_for_completion(prompt_id, timeout=timeout)
