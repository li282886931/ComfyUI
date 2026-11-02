import json
from pathlib import Path


WORKFLOW = Path(__file__).parents[2] / "blueprints" / "Image to Image (DWPose + Depth ControlNet).json"


def test_dwpose_depth_workflow_has_two_serial_controlnet_stages():
    workflow = json.loads(WORKFLOW.read_text())
    nodes = {node["id"]: node for node in workflow["nodes"]}
    links = {link[0]: link for link in workflow["links"]}

    assert workflow["definitions"]["subgraphs"]
    assert any(node["title"] == "Image to Pose Map (SDPose Multi-Person)" for node in nodes.values())
    assert any(node["title"] == "Image to Depth Map (Lotus)" for node in nodes.values())

    applications = [node for node in nodes.values() if node["type"] == "ControlNetApplyAdvanced"]
    assert len(applications) == 2

    first, second = sorted(applications, key=lambda node: node["id"])
    assert first["inputs"][0]["link"] in links
    assert first["inputs"][1]["link"] in links
    assert second["inputs"][0]["link"] == first["outputs"][0]["links"][0]
    assert second["inputs"][1]["link"] == first["outputs"][1]["links"][0]

    sampler = next(node for node in nodes.values() if node["type"] == "KSampler")
    decoder = next(node for node in nodes.values() if node["type"] == "VAEDecode")
    saver = next(node for node in nodes.values() if node["type"] == "SaveImage")
    assert sampler["inputs"][1]["link"] == second["outputs"][0]["links"][0]
    assert sampler["inputs"][2]["link"] == second["outputs"][1]["links"][0]
    assert decoder["inputs"][0]["link"] == sampler["outputs"][0]["links"][0]
    assert saver["inputs"][0]["link"] == decoder["outputs"][0]["links"][0]
