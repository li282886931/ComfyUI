# ComfyUI Upstream Sync Design

## Goal

同步 `Comfy-Org/ComfyUI` 的最新 `master` 到当前仓库，同时保留当前仓库的 SDK、LoRA helper、n8n bridge、Sora/Stability API 节点、资产查询扩展和本地 blueprint。

## Context

当前仓库与官方仓库没有共同 Git 历史，不能直接使用普通 merge 或 cherry-pick。当前提交时间为 2026-08-04，官方 `master` 为 2026-10-19。官方树包含约 1303 个文件，当前树包含约 789 个文件；双方有 772 个同路径文件，其中 431 个内容不同。

## Design

以官方最新 `master` 作为代码基线，在独立同步分支上迁移本地定制：

- 保留 `comfy_api/sdk.py` 和 `comfy_api/lora_helper.py`。
- 保留 SDK、LoRA 和 n8n 示例脚本。
- 保留 Sora 和 Stability API 节点、schema 及注册入口；如果官方已新增同一服务实现，以官方公共 API 结构为主适配本地行为。
- 保留本地资产数据库查询和批量导入扩展，并根据官方资产模型、迁移和服务接口调整导入。
- 保留当前仓库独有且官方没有的 blueprint；同名 blueprint 采用官方版本。
- 迁移官方新增模型、节点、资产服务、执行能力、数据库迁移、测试和 CI 文件。

同名文件的处理以官方实现为主，不使用整文件覆盖。每个冲突文件都检查导入、注册表、协议、配置和数据库迁移依赖。数据库迁移保持官方迁移顺序，不覆盖既有本地迁移。

## Validation

- 在迁移开始前建立当前提交的回滚分支和同步分支。
- 增加 SDK 的队列、WebSocket 完成、超时、历史结果和 LoRA 注入测试。
- 增加定制节点注册和请求 schema 测试。
- 运行官方单元测试、执行测试、静态检查、数据库迁移检查和最小启动检查。
- 迁移过程中按“官方基线、定制模块、入口适配、测试修复”分批提交。

## Out of Scope

- 不重写 SDK 的公开 API。
- 不引入新的第三方 API 服务。
- 不删除官方已有功能。
- 不修改工作区中未纳入 Git 的用户文件。
