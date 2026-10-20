# ComfyUI Upstream Sync Validation

## Result

The sync branch is based on official `Comfy-Org/ComfyUI` `master` at `b1a247c9cf9dbfda4b2c0a0c1d50950667eeaa0c`. The local customization baseline remains available at `backup/pre-upstream-sync-20261020`.

## Restored custom behavior

- Asynchronous SDK and LoRA prompt helper.
- SDK and n8n example scripts.
- Stability API schemas and nodes.
- Sora API node.
- Two workflows that are absent from the official tree.

The LoRA helper was corrected so the generated first LoRA node keeps its original model/CLIP inputs instead of being rewritten to reference itself.

## Validation commands

| Command | Result |
| --- | --- |
| `uv run --python 3.12 --with aiohttp --with pydantic --with pytest python -m pytest tests-unit/comfy_api_test/sdk_test.py tests-unit/comfy_api_nodes_test/custom_api_nodes_test.py -q` | 3 passed, 1 skipped |
| `python3 -m compileall -q comfy_api script_examples comfy_api_nodes` | Passed |
| `uv run --python 3.12 --with ruff ruff check ...` | Passed with `T201` ignored for executable examples |
| `uv run --python 3.12 --with pydantic --with pydantic-settings --with aiohttp python main.py --help` | Passed |
| `python3 -m json.tool` on both restored blueprints | Passed |

The Sora schema test is skipped when Torch is unavailable. The current machine has no Torch installation, so full model, API-node runtime, official unit, execution, and inference suites were not run.

## Asset subsystem decision

The official `master` has replaced the local `AssetReference`/`bulk_ingest` model with the `AssetContent`/`Asset` record model and the scanner/records services. Official migrations `0007_record_content_split.py`, `0008_drop_asset_meta.py`, and `0009_created_at_from_mtime.py` make the old local query modules incompatible with the current schema. Those dead modules were not restored. The official scanner, metadata, tag, preview, and batch-seeding paths remain in place and are covered by the official asset test suite.

## Remaining verification

Run the full dependency-backed checks in an environment with the project requirements installed:

```bash
pytest tests-unit -q
pytest tests/execution -q
ruff check .
alembic upgrade head
```
