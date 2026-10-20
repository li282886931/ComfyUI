from comfy_api_nodes.apis.stability import (
    StabilityAspectRatio,
    StabilityStableUltraRequest,
)


def test_stability_schema_accepts_required_generation_fields():
    request = StabilityStableUltraRequest(
        prompt="a studio portrait",
        aspect_ratio=StabilityAspectRatio.ratio_1_1,
    )

    assert request.prompt == "a studio portrait"
    assert request.aspect_ratio == StabilityAspectRatio.ratio_1_1


def test_sora_schema_rejects_missing_required_fields():
    import pytest

    pytest.importorskip("torch")
    from pydantic import ValidationError

    from comfy_api_nodes.nodes_sora import Sora2GenerationRequest

    try:
        Sora2GenerationRequest(prompt="a film")
    except ValidationError as error:
        missing_fields = {entry["loc"][0] for entry in error.errors()}
        assert {"model", "seconds", "size"} <= missing_fields
    else:
        raise AssertionError("Sora request unexpectedly accepted missing fields")
