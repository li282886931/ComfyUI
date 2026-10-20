# ComfyUI Upstream Sync Implementation Plan

> **For agentic workers:** Execute this plan task-by-task with review checkpoints.

**Goal:** 将官方最新 `Comfy-Org/ComfyUI` `master` 作为当前基线，同时恢复并验证当前仓库的定制功能。

**Architecture:** 先建立可回滚的当前版本基线，再以官方树创建同步分支。定制功能按独有文件、同名资产模块、API 节点注册和示例脚本分批迁移；同名核心文件以官方实现为主进行适配。

**Tech Stack:** Git, Python 3.10+, pytest, Ruff, Alembic, ComfyUI runtime, aiohttp, Pydantic.

---

### Task 1: Establish migration checkpoints

**Files:**
- Create: `docs/superpowers/specs/2026-10-20-comfyui-upstream-sync-design.md`
- Create: `docs/superpowers/plans/2026-10-20-comfyui-upstream-sync.md`

- [ ] **Step 1: Verify the worktree**

Run:

```bash
git status --short --branch
git show -s --format='%H %ci %s' HEAD
git show-ref refs/remotes/upstream/master
```

Expected: no user modifications are overwritten; `upstream/master` points to the fetched official revision.

- [ ] **Step 2: Create rollback and working branches**

Run:

```bash
git branch backup/pre-upstream-sync-20261020 HEAD
git switch -c sync/upstream-master-20261020
```

Expected: the current commit remains reachable through `backup/pre-upstream-sync-20261020`.

- [ ] **Step 3: Commit the design documents**

Run:

```bash
git add docs/superpowers/specs/2026-10-20-comfyui-upstream-sync-design.md docs/superpowers/plans/2026-10-20-comfyui-upstream-sync.md
git commit -m "docs: define ComfyUI upstream sync"
```

Expected: one documentation commit on the sync branch.

### Task 2: Create the official baseline

**Files:**
- Modify: repository tree from `upstream/master`

- [ ] **Step 1: Save the current custom file manifest**

Run:

```bash
comm -23 <(git ls-tree -r --name-only backup/pre-upstream-sync-20261020 | sort) <(git ls-tree -r --name-only upstream/master | sort) > /tmp/comfyui-custom-diff.txt
git ls-tree -r --name-only backup/pre-upstream-sync-20261020 > /tmp/comfyui-local-manifest.txt
```

Expected: manifests are available outside the repository for the migration session.

- [ ] **Step 2: Replace the tracked tree with the official tree**

Run:

```bash
git rm -r --cached .
git read-tree --reset -u upstream/master
git status --short
```

Expected: the worktree matches the official tree before custom files are restored.

- [ ] **Step 3: Commit the official baseline**

Run:

```bash
git add -A
git commit -m "chore: sync official ComfyUI master baseline"
```

Expected: the official tree is an isolated checkpoint.

### Task 3: Restore custom SDK and examples

**Files:**
- Create: `comfy_api/lora_helper.py`
- Create: `comfy_api/sdk.py`
- Create: `script_examples/n8n_bridge.py`
- Create: `script_examples/sdk_lora_example.py`
- Create: `script_examples/sdk_usage_example.py`
- Test: `tests-unit/comfy_api_test/sdk_test.py`

- [ ] **Step 1: Write failing SDK and LoRA behavior tests**

The tests must cover prompt queue payload construction, completion timeout, terminal WebSocket execution event handling, and replacement of model/CLIP references after adding one LoRA.

- [ ] **Step 2: Run the focused tests**

Run:

```bash
pytest tests-unit/comfy_api_test/sdk_test.py -q
```

Expected: FAIL because the custom SDK and helper are not yet restored.

- [ ] **Step 3: Restore the custom implementation**

Restore the implementation from `backup/pre-upstream-sync-20261020`, then adapt imports and any changed official API utility types without changing the public SDK signatures.

- [ ] **Step 4: Run the focused tests**

Run:

```bash
pytest tests-unit/comfy_api_test/sdk_test.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the SDK batch**

```bash
git add comfy_api/lora_helper.py comfy_api/sdk.py script_examples tests-unit/comfy_api_test/sdk_test.py
git commit -m "feat: restore ComfyUI SDK and LoRA helpers"
```

### Task 4: Restore API node customizations

**Files:**
- Create or modify: `comfy_api_nodes/apis/stability.py`
- Create or modify: `comfy_api_nodes/nodes_stability.py`
- Create or modify: `comfy_api_nodes/nodes_sora.py`
- Modify: `comfy_api_nodes/apis/__init__.py` when the official generated schemas require compatibility wiring
- Test: `tests-unit/comfy_api_nodes_test/custom_api_nodes_test.py`

- [ ] **Step 1: Write failing registration and schema tests**

Tests must assert that the Stability and Sora extensions expose their node classes, request models reject invalid required values, and valid request payloads use the official API client conventions.

- [ ] **Step 2: Run the focused tests**

Run:

```bash
pytest tests-unit/comfy_api_nodes_test/custom_api_nodes_test.py -q
```

Expected: FAIL before the custom nodes and schemas are restored.

- [ ] **Step 3: Restore and adapt the custom nodes**

Copy the custom files from `backup/pre-upstream-sync-20261020`. Resolve imports against the official API node utility modules and preserve the official extension discovery contract.

- [ ] **Step 4: Run the focused tests**

Run:

```bash
pytest tests-unit/comfy_api_nodes_test/custom_api_nodes_test.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the API node batch**

```bash
git add comfy_api_nodes tests-unit/comfy_api_nodes_test/custom_api_nodes_test.py
git commit -m "feat: restore custom Stability and Sora API nodes"
```

### Task 5: Reconcile asset query and ingestion extensions

**Files:**
- Modify: `app/assets/database/queries/asset.py`
- Modify: `app/assets/database/queries/asset_reference.py`
- Modify: `app/assets/database/queries/common.py`
- Modify: `app/assets/services/bulk_ingest.py`
- Modify: related official asset services and migrations only where required by imports or schema contracts
- Test: `tests-unit/assets_test/queries/test_custom_asset_queries.py`

- [ ] **Step 1: Write failing compatibility tests**

Tests must exercise the custom asset-reference query and batch-ingest public functions against the official asset schema and database session fixtures.

- [ ] **Step 2: Run the focused tests**

Run:

```bash
pytest tests-unit/assets_test/queries/test_custom_asset_queries.py -q
```

Expected: FAIL until the custom query and ingestion behavior is reconciled with the official asset implementation.

- [ ] **Step 3: Adapt the custom asset code**

Port only custom query predicates, projection behavior, and batch-ingest behavior. Keep official lifecycle, scanner, metadata, preview, and migration ownership intact.

- [ ] **Step 4: Run the focused tests**

Run:

```bash
pytest tests-unit/assets_test/queries/test_custom_asset_queries.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the asset batch**

```bash
git add app tests-unit/assets_test/queries/test_custom_asset_queries.py
git commit -m "feat: preserve custom asset query extensions"
```

### Task 6: Restore unique blueprints

**Files:**
- Create: local-only blueprint files from the backup manifest
- Modify: none for blueprints that already exist in the official tree

- [ ] **Step 1: Identify only official-missing blueprints**

Run:

```bash
comm -23 <(git ls-tree -r --name-only backup/pre-upstream-sync-20261020 -- blueprints | sort) <(git ls-tree -r --name-only HEAD -- blueprints | sort)
```

Expected: only blueprints absent from the official baseline are selected.

- [ ] **Step 2: Restore the unique blueprints**

Run:

```bash
git checkout backup/pre-upstream-sync-20261020 -- "blueprints/Image to Depth Map (Lotus).json" "blueprints/Video Inpaint(Wan2.1 VACE).json"
```

Expected: official same-name files remain unchanged; unique local blueprints are restored.

- [ ] **Step 3: Validate JSON**

Run:

```bash
python3 -m json.tool "blueprints/Image to Depth Map (Lotus).json" >/dev/null
python3 -m json.tool "blueprints/Video Inpaint(Wan2.1 VACE).json" >/dev/null
```

Expected: both commands exit successfully.

- [ ] **Step 4: Commit the blueprint batch**

```bash
git add blueprints
git commit -m "feat: preserve custom workflow blueprints"
```

### Task 7: Run full validation and document residual risk

**Files:**
- Modify: `README.md` only if the official baseline or restored public SDK needs accurate usage documentation
- Create: `docs/superpowers/reports/2026-10-20-comfyui-upstream-sync-validation.md`

- [ ] **Step 1: Run focused custom tests**

```bash
pytest tests-unit/comfy_api_test tests-unit/comfy_api_nodes_test tests-unit/assets_test/queries -q
```

- [ ] **Step 2: Run official tests**

```bash
pytest tests-unit -q
pytest tests/execution -q
```

- [ ] **Step 3: Run static and migration checks**

```bash
ruff check .
alembic upgrade head
python3 main.py --help
```

- [ ] **Step 4: Record failures and fixes**

The validation report must list each command, exit status, test count, and any dependency-gated checks that could not run. It must explicitly identify remaining incompatibilities rather than marking them as passed.

- [ ] **Step 5: Commit the validation report**

```bash
git add README.md docs/superpowers/reports/2026-10-20-comfyui-upstream-sync-validation.md
git commit -m "test: validate ComfyUI upstream sync"
```
