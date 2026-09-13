# 写卡方法论：PLists + Ali:Chat（完整版）

> 三源查证：sillytavern.wiki 角色设计页 + Trappu 指南（PygmalionAI Wiki）+ 官方 Seraphina 示范卡。
> 社区补充：几份中文攻略（格式心法 / 傻瓜版教学 / 白羽 XML 格式 / FAQ）——出处见 `02-sources.md`。
> 2026-08-13 定稿。这是写卡的核心方法——description 教说话，PList 保人设。

## 核心分工（为什么这么写）

| 字段 | 放什么 | token 性质 |
|------|--------|-----------|
| `description` | **Ali:Chat 示例对话**（教说话方式/口癖/语气）+ 核心事实 | 永久（但对话久了进第三记忆篮变弱） |
| `extensions.depth_prompt.prompt` | **PList 属性块**（性格/外观/场景标签） | 永久（第一记忆篮，长对话保人设的关键） |
| `first_mes` | 场景化开场（开局事件+动作描写+对话钩子） | 临时（只发一次，但开局定风格） |
| `character_book` | 世界书条目（可选） | 按需触发 |

**为什么这么分：** description 里的示例对话定义角色，但对话长了会被挤出有效区；PList 放 `depth_prompt` 后，模型能「拉动」description 里的示例保持相关——长对话不 OOC。
（白羽记忆理论：Claude 对上下文开头+结尾印象最深、中间偏前记得烂——depth_prompt 深度 2-4 都在结尾区附近，正合适。）

## PList 写法（进 depth_prompt.prompt）

```
[角色名's Personality= "标签1", "标签2", ...]
[角色名's body= "发色", "瞳色", "服装", ...]
[角色名's Setting= "所属", "地位", "关系", ...]
```

- 官方结构：`{"prompt": "<PList>", "depth": 4, "role": "system"}`
- 傻瓜版教学：插入深度推荐 **2-3**（比官方 4 更浅，社区经验）；深度 2 可保人设永生难忘（配世界书 constant）
- 背景/设定**不用全取**，只放重要的（傻瓜版：你觉得用不到的可以省略）
- 第二种写法（分节）：`[角色名 = 外观...; 个性=...; 背景=...]`——也行，PList 没有固定写法，要素简化即可
- 标签来自：IDENTITY Vibe + AGENTS 性格锚点 + curated 外观特征

## Ali:Chat 写法（进 description）

```
[Genre: 世界观; Tags: 关键词; Scenario: 场景设定]  ← 场景块（description 顶部）

<START>
{{user}}: 「对话」
{{char}}: *动作描写* 「角色回复，带口癖」  ← 2-3 组，教风格
```

- 素材来源：角色设定/互动手册里已有的示例；作品语音台词；对话样本
- 对话要体现：口癖（同一句尾助词反复出现）、句式习惯、语气——示例里就要让口癖自然出现
- 官方示范：`{{char}}` 回复带 `*动作描写*` 的完整轮次

## first_mes 铁律

- 场景化开场：`*动作描写*` + 角色登场 + 对话钩子
- **别替用户行动**——只描写角色自己的动作，不 narrate 用户（否则模型学会替用户说话）
- 开头定风格：想要长回复就写详细，想要短句角色就写短——first_mes 是长度规范的样板
- 社区 FAQ：greeting 里用第三人称指代角色（「白棠」而不是「我」）
- 可以留空（懒人 0-shot 场景提示：删掉 first_mes，用户用 `[Scene: ...; Tags: ...; Instruction: ...]` 自定义）

## 其他字段

- `personality` / `scenario`：可留空（内容进 PList/Ali:Chat）
- `system_prompt` / `post_history_instructions`：精简填硬规则（口癖/句式限制/边界）；⚠️ 会替换用户设置，别塞成论文
- `extensions.talkativeness`：0.5 默认
- `extensions.world`：关联世界书名（有书才填）

## 格式心法（社区实战摘要）

> 摘要自社区攻略（出处见 `02-sources.md`），只留可复用的结论。

- **英文 xml 标签包 yaml 中文**：信息熵高，模型对 xml 敏感（`<worldview>`、`<角色名>` tag 包 job/appearance/personalities/skills）
- **数字概率**代替模糊词（「70%概率：出门散步」）
- 层级 2-5 子模块、深度 ≤3，再多大模型注意力涣散
- 中文≈1.5 token；数字用阿拉伯数字；别翻译成英文（丢味）
- 复杂长文本可拆 json 格式（提升解析能力）

## 验证

`validate_tavern_card.py --deep` 检查：depth_prompt 结构 / 顶层 V1 双份 / first_mes 占位残留 / first_mes 替用户行动。
