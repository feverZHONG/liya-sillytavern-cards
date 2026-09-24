# 莉娅的酒馆写卡方法 · SillyTavern Cards

> 把「一堆角色资料」变成一张 SillyTavern 能用的角色卡：格式规格、PList + Ali:Chat 写法、机制清单、三个 Python 工具，外加一个从资料走到成品卡的完整实例。
> 技术口径全部以官方仓库 [SillyTavern/SillyTavern](https://github.com/SillyTavern/SillyTavern) 为 ground truth。

## 这是什么

一套「写卡」的实操方法 + 一套纯标准库的 Python 工具。核心一句话：

**PList（属性块）进 `extensions.depth_prompt`，Ali:Chat（示例对话）进 `description`，first_mes 场景化开场。**

覆盖这些事：

- **格式** —— V2 必填 14 字段、`spec` 语义、顶层 V1 + `data` V2 双份的由来、PNG 嵌卡
- **写法** —— PList / Ali:Chat 的分工与具体写法、first_mes 铁律、depth 深度选择
- **机制** —— 世界书条目怎么用（selective / constant / position / insertion_order），进阶机制（概率 / 包含组 / 定时 / @D 深度）
- **上游** —— 只有资料、组织不成设定时，先用角色设定写作模板把资料变成设定文本
- **工具** —— 生成初稿 / 校验（含写卡质量深度检查）/ PNG 嵌卡
- **实例** —— `examples/白棠/`：原创演示角色，资料 → 设定 → 卡 → 校验全流程走通
- **踩坑** —— 发布前逐条自查（占位残留、`<START>` 复读、替用户行动、WEBP 改名当 PNG……）

## 怎么装

```bash
git clone https://github.com/feverZHONG/liya-sillytavern-cards.git ~/.hermes/skills/sillytavern-cards
```

工具是纯 Python 标准库，无需安装依赖；校验器的 token 统计若装了 `tiktoken` 会用同口径精确值，没装则按字符估算。

## 快速上手

```bash
cd ~/.hermes/skills/sillytavern-cards

# 1. 生成初稿（角色资料按下面的「三件套」摆在 examples/白棠/）
python3 scripts/make_tavern_card.py 白棠 --src examples \
  --genre "现代日常" --tags "示例,中文" --creator "你的署名" \
  --scenario "旧城巷尾的钟表铺，夜里十一点还亮着灯。" \
  --out /tmp/baitang-draft.json

# 2. 手写精修：first_mes 场景化、PList 换行为锚点、<START> 示例（这三处工具不做）

# 3. 校验（--deep 会点出占位残留 / 复读 / depth_prompt 缺失）
python3 scripts/validate_tavern_card.py 你的卡.json --deep

# 4. 可选：嵌成 PNG 卡（头像图当底图）
python3 scripts/embed_tavern_card.py 你的卡.json avatar.png card.png
```

## 目录

| 路径 | 内容 |
|:-----|:-----|
| `SKILL.md` | 入口：写卡总览 + 字段速查 + 工具链 + 制作流程 |
| `references/01-format-spec.md` | V2 格式规格（必填字段 / spec 语义 / JSON 模板） |
| `references/02-sources.md` | 资料从哪来：上游链接 / 本机镜像约定 / 角色素材清单 |
| `references/03-pitfalls.md` | 踩坑记录（发布前逐条自查） |
| `references/writing-method.md` | **写卡方法论完整版**（PList / Ali:Chat / first_mes 铁律） |
| `references/06-mechanism-checklist.md` | 一张卡能用哪些机制（含「缺了会白写」的两条） |
| `references/07-advanced-mechanisms.md` | 进阶机制落地写法（概率 / 包含组 / 定时 / @D / V3） |
| `references/08-official-writing-patterns.md` | 官方写法模式（对话式世界书 / sysprompt 预设 / talkativeness / PNG 坑） |
| `references/09-early-prompt-checklist.md` | 早年写卡前置规范：能用 ✅ / 不能用 ❌ |
| `references/10-setting-writing-template.md` | **角色设定写作模板 v1.2**（有资料 → 设定文本，写卡的上游） |
| `references/11-worked-example.md` | 完整实例走查（白棠：资料 → 卡 → 校验，含真实输出） |
| `references/tavern-field-mapping.md` | 官方源码字段映射（保存 / 读取逻辑） |
| `references/seraphina-card-notes.md` | 官方默认卡逆向（一张卡怎么填的官方示范） |
| `references/stwiki-writing-notes.md` | 官方 wiki 写卡核心（字段语义 / 世界书 / 宏 / token） |
| `references/scope-and-boundaries.md` | **配套文件**（不属于本 skill）：跟 AI 助手人格 / 角色档案的分界 |
| `scripts/make_tavern_card.py` | 三件套资料 → V2 卡初稿 |
| `scripts/validate_tavern_card.py` | 官方 validator 翻译 + 写卡质量深度检查 + token 统计 |
| `scripts/embed_tavern_card.py` | PNG 嵌卡（tEXt `chara`） |
| `examples/白棠/` | 演示角色的资料（三件套 + 外观） |
| `examples/白棠-卡.json` | 精修后的成品卡（V2） |

## 工具约定的输入格式（三件套）

一个角色一个目录：

| 文件 | 内容 |
|:-----|:-----|
| `IDENTITY.md` | `Name` + `Vibe`（一句话定位） |
| `persona-soul.md` | 第一人称自述：我是谁 / 怎么说话 / 核心 / 底线 |
| `AGENTS.md` | 互动手册：核心指令 / 说话风格 / 示例 / 性格锚点 / 对话节奏 / 禁止 / 边界 |
| `外观.md`（可选） | 外观特征，一行一条 |

不想每次敲参数：把默认值写进 `~/.config/tavern-cards.json`（或用 `$TAVERN_CARDS_CONFIG` 指定其它路径）：

```json
{
  "personas_root": "/path/to/personas",
  "curated_root": "/path/to/curated",
  "out_dir": "/path/to/cards",
  "genre": "作品名",
  "tags": ["中文"],
  "creator": "你的署名"
}
```

## 第三方资料

社区指南、官方 wiki、官方 spec 与 parser/validator 源码**不随本仓库分发**——仓库里只有自己的查证笔记与工具，出处与链接集中在 `references/02-sources.md`。
本仓库里的「角色设定写作模板 v1.2」为 **fever钟** 作品（原载 B 站专栏 [cv47543229](https://www.bilibili.com/read/cv47543229)），随仓库分发，转载请注明出处。

## 姊妹仓库


- [liya-chat-game-referee](https://github.com/feverZHONG/liya-chat-game-referee) · [liya-spy-game](https://github.com/feverZHONG/liya-spy-game) · [liya-sea-turtle-soup](https://github.com/feverZHONG/liya-sea-turtle-soup) —— 聊天里能玩的三件（回合制裁判引擎 / 谁是卧底 / 海龟汤）
- [liya-persona-authoring](https://github.com/feverZHONG/liya-persona-authoring) —— 给 AI agent 写它**自己**的身份文件（跟本仓库规则相反，别混用，见 `references/scope-and-boundaries.md`）
- [liya-subtraction-skill](https://github.com/feverZHONG/liya-subtraction-skill) —— 技能库精简与维护
- [liya-vision-recognition-traps](https://github.com/feverZHONG/liya-vision-recognition-traps) —— 视觉模型识图陷阱：19 条实测陷阱 + 真 OCR 通道 + AI 生图物理体检 + 两图差分
- [liya-sillytavern-worldbook](https://github.com/feverZHONG/liya-sillytavern-worldbook) —— 酒馆世界书（Lorebook）：触发链源码实证 + 触发体检 / 模拟 / 生成工具

## 提思路 / 提修正

- 新的写法、机制、踩坑 → 开 [Issue](https://github.com/feverZHONG/liya-sillytavern-cards/issues)，说清场景（什么卡、什么模型、出现什么现象）
- 想直接改 → Fork + PR，改动请写清「为什么要这么写」

## 许可

MIT（方法与工具）。「角色设定写作模板 v1.2」为 fever钟 作品，随仓库分发，转载请注明出处。

---

*莉娅（[@feverZHONG](https://github.com/feverZHONG)）· 宇宙美好记录官*
