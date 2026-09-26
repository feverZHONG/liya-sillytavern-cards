---
name: sillytavern-cards
tier: T2  # T分级: T2=直接做 / T1=先请示 / T0=一律拒
description: 写 SillyTavern 角色卡——V2/V3 格式规格、PList+Ali:Chat 写法、机制清单、三个 Python 工具、可照着走的完整实例。触发：酒馆、SillyTavern、角色卡、写卡、卡格式。
---

# 酒馆角色卡 · SillyTavern Cards

> **核心目的：写卡。** 把「一堆角色资料」变成一张 SillyTavern 能用的卡（V2 JSON / PNG 嵌卡）。
> 不碰酒馆部署/运行。技术口径全部以官方仓库 SillyTavern/SillyTavern 为 ground truth。

## 边界

**只写卡，不跑酒馆。** 本 skill 从头到尾只做一件事：把角色资料变成一张 SillyTavern 能用的卡（V2 JSON / PNG 嵌卡）。酒馆本身的部署、运行、扩展、调试都不在范围内。

## 触发

酒馆 / SillyTavern / 角色卡 / 写卡 / 精修 / 卡格式 / PList / Ali:Chat

## 一张卡怎么写（总览）

> 一句话核心：**PList（属性块）进 `extensions.depth_prompt`，Ali:Chat（示例对话）进 `description`，first_mes 场景化开场。**

```
角色资料 ──(设定模板)──> 设定文本 ──(工具/手写)──> V2 卡 JSON ──(校验)──> 发布
          references/10      + 手写精修      scripts/make   scripts/validate
```

| 字段 | 放什么 |
|------|--------|
| `description` | `[Genre/Tags/Scenario]` 场景块 + `<START>` Ali:Chat 示例（教说话方式） |
| `extensions.depth_prompt.prompt` | PList 属性块（`[角色's Personality= ...]` / `body= ...` / `Setting= ...`），depth 2-4 |
| `first_mes` | 场景化开场：`*动作描写*` + 登场 + 对话钩子；**别替用户行动** |
| `personality`/`scenario` | 留空（内容进 PList/Ali:Chat） |
| `system_prompt`/`post_history_instructions` | 精简硬规则（口癖/句式/边界），别塞满 |

完整方法论 → `references/writing-method.md`（**写卡前先翻**）。

## 工具链（Python 适配官方实现）

`scripts/` 三件套，纯标准库、无第三方依赖：

| 脚本 | 用途 |
|------|------|
| `make_tavern_card.py <角色名\|角色目录> [--src 根目录] [--out 卡.json]` | 三件套资料 → V2 卡初稿（顶层 V1 双份 + depth_prompt PList 基础版 body→Setting→Personality + 场景块 description + 自动校验）。`<START>` 示例和 first_mes 精修是手写活 |
| `validate_tavern_card.py <卡.json\|卡.png> [--deep]` | 官方 validator 翻译：V1/V2/V3 识别 + V2 14 必填字段 + PNG 解卡；`--deep` 加写卡质量检查（V2/V3 都查：depth_prompt / first_mes 占位 / 顶层双份 / 【需补充】残留 / `<START>` 块 user-char 复读 / PList 施工注释）；**默认输出 token 统计（累计/恒定，酒馆 UI 同口径）** |
| `embed_tavern_card.py <卡.json> <底图.png> <输出.png>` | PNG 嵌卡（tEXt `chara`，官方写入同款） |
| 世界书（机制 / 独立书 / 触发模拟 / 接卡） | `sillytavern-worldbook` skill + `bin/wb` + `tavern world` |

### 输入格式（工具约定的「三件套」）

一个角色一个目录，目录里放：

| 文件（示范路径） | 内容 | 进卡位置 |
|------|------|---------|
| `examples/白棠/IDENTITY.md` | `Name` + `Vibe`（一句话定位） | `name` + PList Personality 首标签 |
| `examples/白棠/persona-soul.md` | 第一人称自述：我是谁 / 怎么说话 / 核心 / 底线 | PList `Setting=` + Ali:Chat 素材 |
| `examples/白棠/AGENTS.md` | 互动手册：核心指令 / 说话风格 / 示例 / 性格锚点 / 对话节奏 / 禁止 / 边界 | PList Personality 锚点 + `system_prompt` + `post_history_instructions` |
| `examples/白棠/外观.md`（可选） | 外观特征，一行一条 | PList `body=` |

完整范例见 `examples/白棠-卡.json`（成品卡）与 `references/11-worked-example.md`（走查）——原创演示角色，从资料到成品卡全流程走通。

**默认值**：脚本支持 `--src/--out/--genre/--tags/--creator` 显式传参；也可以放一份配置文件（`$TAVERN_CARDS_CONFIG` 或 `~/.config/tavern-cards.json`），省得每次敲。

## 卡制作流程

0. **只有资料、组织不成设定？** 先跑 `references/10-setting-writing-template.md` 把资料变成设定文本——这是写卡的上游，产出可直接喂 PList/Ali:Chat
1. `make_tavern_card.py <角色> --src <角色目录的父目录>` → 卡 JSON 初稿
2. **精修三处**（自动生成只是基础版）：`first_mes` 场景化改写 / PList 标签精修 / `<START>` 示例补动作描写
3. **对照互动手册（`AGENTS.md`）逐条落实硬规则**——system_prompt 收口癖/句式限制，post_history_instructions 收对话节奏/禁止事项（漏一条，卡里的人就不像）
4. `validate_tavern_card.py 卡.json --deep` → 必须 ✅ V2（V3 同样跑）
5. **token 统计**：validate 默认输出「累计/恒定」；酒馆界面实测值可登记进 `extensions.<你的命名空间>.token_stats`
6. 可选：`embed_tavern_card.py` → PNG 卡
7. **可用性验收（不装酒馆）**：自己按卡演 3-4 轮最难的输入，再派 1-2 个隔离样本跑固定话术（**必须含多轮追问**）→ 看「哪条规则最难守、哪里停下来权衡」；**两个样本独立指向同一处才是真问题**。流程 → `tavern-card-refinement`「交付前的可用性验收」；写法反模式 → `references/writing-method.md` 末节
8. 发布（PNG 或 JSON）

**V3 需补充卡流程（模板卡 / 导出卡补全）：**

- 卡里 `personality`/`scenario`/`mes_example` 标【需补充】→ 按素材手写填上（`data` + 顶层双份），顺手清掉 description / first_mes / system_prompt 里的【这里...】模板注释头
- 示例对话：`mes_example` 用 `<START>` 分隔，与 description 里已有的 `<START>` 示例**不重复**（覆盖其他性格面）
- `validate_tavern_card.py 卡.json --deep` → V3 通过 + 无占位残留 warning 才算完

## 引用表

| 你要查什么 | 打开 |
|:-----------|:-----|
| V2 格式规格（必填字段/spec 语义/JSON 模板） | `references/01-format-spec.md` |
| 资料从哪来（上游链接 / 本机镜像 / 素材清单） | `references/02-sources.md` |
| 踩坑记录（发布前逐条自查） | `references/03-pitfalls.md` |
| 写卡方法论完整版（PList / Ali:Chat / first_mes 铁律） | `references/writing-method.md` |
| 机制补全清单（一张卡能用哪些机制） | `references/06-mechanism-checklist.md` |
| 进阶机制落地指南（概率 / 包含组 / 定时 / 白羽法 / V3） | `references/07-advanced-mechanisms.md` |
| 官方写法模式（对话式世界书 / sysprompt 预设 / talkativeness / PNG 坑） | `references/08-official-writing-patterns.md` |
| 早年前置修订（写卡检查清单：能用 ✅ / 不能用 ❌） | `references/09-early-prompt-checklist.md` |
| **角色设定写作模板（有资料 → 设定文本）** | `references/10-setting-writing-template.md` |
| 完整实例：资料 → 设定 → 卡 → 校验 | `references/11-worked-example.md` + `examples/白棠/` |
| 官方源码字段映射（保存/读取逻辑） | `references/tavern-field-mapping.md` |
| 官方默认卡逆向（一张卡怎么填的官方示范） | `references/seraphina-card-notes.md` |
| 官方 wiki 写卡核心（字段语义 / 世界书 / 宏 / token） | `references/stwiki-writing-notes.md` |
| **世界书机制与触发条件（源码实证：触发链 / selective / 扫描深度 / 预算 / 过滤器）** | `sillytavern-worldbook/references/12-worldbook-mechanics.md` |

## 关联

- **分界**：「给 AI 助手写它自己的人格文件」是另一条线（规则相反）——分界文档见 <https://github.com/feverZHONG/liya-persona-authoring>（本仓库也随带一份，即 references 里的 scope-and-boundaries）
- 角色客观档案（资料整理，不写卡）：另一类活，别混
