import asyncio

from comfy_api.lora_helper import apply_loras_to_prompt
from comfy_api.sdk import ComfyUIClient


class FakeResponse:
    status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    async def json(self):
        return {"prompt_id": "prompt-1"}

    async def text(self):
        return ""


class FakeSession:
    def __init__(self):
        self.post_calls = []

    def post(self, url, json):
        self.post_calls.append((url, json))
        return FakeResponse()


def test_apply_loras_keeps_base_reference_on_first_lora_node():
    prompt = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {},
        },
        "6": {
            "class_type": "CLIPLoader",
            "inputs": {},
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {"model": ["4", 0], "positive": ["6", 0]},
        },
    }

    result = apply_loras_to_prompt(
        prompt,
        [{"name": "style.safetensors", "strength_model": 0.8}],
        model_node_id="4",
        clip_node_id="6",
    )

    assert result["100"]["inputs"]["model"] == ["4", 0]
    assert result["5"]["inputs"]["model"] == ["100", 0]
    assert result["5"]["inputs"]["positive"] == ["100", 1]


def test_sdk_queue_prompt_sends_prompt_and_client_id():
    async def run():
        client = ComfyUIClient(server_address="localhost:8188", client_id="client-1")
        client.session = FakeSession()

        prompt_id = await client.queue_prompt({"4": {"class_type": "EmptyLatentImage"}})

        assert prompt_id == "prompt-1"
        assert client.session.post_calls == [
            (
                "http://localhost:8188/prompt",
                {
                    "prompt": {"4": {"class_type": "EmptyLatentImage"}},
                    "client_id": "client-1",
                },
            )
        ]

    asyncio.run(run())
