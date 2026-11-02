import json
from pathlib import Path


WORKFLOW = Path(__file__).parents[2] / "blueprints" / "Image to Image (DWPose + Depth ControlNet).json"


def test_dwpose_depth_workflow_has_two_serial_controlnet_stages():
    workflow = json.loads(WORKFLOW.read_text())
    assert len(workflow["nodes"]) == 1
    root_node = workflow["nodes"][0]
    root = next(subgraph for subgraph in workflow["definitions"]["subgraphs"] if subgraph["id"] == root_node["type"])
    nodes = {node["id"]: node for node in root["nodes"]}
    links = {link[0]: link for link in root["links"]}

    assert root["outputs"]
    assert root["outputs"][0]["linkIds"]
    assert root["outputs"][0]["linkIds"][0] in links
    assert len(workflow["definitions"]["subgraphs"]) == 3
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


def test_all_blueprints_have_existing_output_link_references():
    for workflow_path in sorted(WORKFLOW.parent.glob("*.json")):
        workflow = json.loads(workflow_path.read_text())
        for subgraph in workflow["definitions"]["subgraphs"]:
            link_ids = {
                link["id"] if isinstance(link, dict) else link[0]
                for link in subgraph["links"]
            }
            for node in subgraph["nodes"]:
                for output in node.get("outputs") or []:
                    missing = set(output.get("links") or []) - link_ids
                    assert not missing, (
                        f"{workflow_path.name}: node {node['id']} "
                        f"references missing output links {sorted(missing)}"
                    )
