# 机制补全清单：一张卡到底能用哪些机制

> 实战毛病：只用了 V2 最小字段，酒馆机制一半没上。
> 本文档是「一张卡能装多少机制」的完整清单。精修任何卡前对照一遍。

## V2 必填 14 字段（validator 硬校验）

`name` `description` `personality` `scenario` `first_mes` `mes_example` `creator_notes` `system_prompt` `post_history_instructions` `alternate_greetings`(数组) `tags`(数组) `creator` `character_version` `extensions`(对象)

## 机制清单（按优先级）

### 🟢 已在用

| 机制 | 位置 | 说明 |
|------|------|------|
| PList | extensions.depth_prompt.prompt | 核心保人设 |
| Ali:Chat | description `<START>` | 教说话方式 |
| 场景块 | description 顶部 `[Genre/Tags/Scenario]` | 定基调 |
| system_prompt / post_history_instructions | 各自字段 | 硬规则 |
| talkativeness | extensions | 0.5 默认 |
| character_book 最小字段 | character_book.entries | id/keys/secondary_keys/comment/content |
| 顶层 V1 双份 | 顶层 + data | 官方保存逻辑 |

### 🔴 缺了会白写的

| 机制 | 字段 | 坑 |
|------|------|-----|
| **selective 开关** | entry.selective | ① 不写/false → secondary_keys 整段被忽略（spec："ignored if selective == false"）；② 写了 true → 二级键变成**强制门槛**（默认 AND_ANY：主键且任一二级键），不是可选修饰。只想要「任一词触发」就别写 secondary_keys |
| **{{original}} 占位** | system_prompt / post_history_instructions | 不写 = 全替换用户全局 system prompt/jailbreak，分享卡会破坏用户自己的设置 |

### 🟡 该补的（增强质量）

| 机制 | 字段 | 用法 |
|------|------|------|
| **constant 常驻** | entry.constant=true | 核心关系条目永远在上下文中（预算内）。如「与用户的关系」条目设 constant |
| **position 插入位置** | entry.position='before_char'/'after_char' | after_char 影响更大（在角色描述后） |
| **insertion_order 优先级** | entry.insertion_order | 数值大=插入靠后=影响大；关系条目 300+，按重要性递增 |
| **enabled / case_sensitive** | entry.enabled / entry.case_sensitive | enabled 默认 true；中文关键词 case_sensitive 保持 false |
| **book 级 name/description** | character_book.name / description | 让世界书在 UI 里可读，不参与 prompt |
| **世界书条目 = 追加背景设定，不是台词本** | entry.content 平铺设定为主 | 台词本只有 description 的 Ali:Chat；世界书是设定库（v0.8 教训）。对话式 content 仅适用「解释世界观」场景（Eldoria 示范），人物关系/背景设定用平铺式 |
| **system_prompt 短写法** | system_prompt | 官方 sysprompt 预设都很短（1-2 句）；「别替用户行动」官方原文 `Do not decide what {{user}} says or does` |
| **talkativeness 群聊语义** | extensions.talkativeness | 0%=除非被提及否则不发言 / 100%=始终回复 / 默认 50%——群聊发言频率不是回复长度 |
| **regex 作用域脚本** | 存角色卡数据 | 内置扩展：查找替换/加 Markdown 样式/STscript 联动，随卡走 |
| **alternate_greetings** | 数组 | swipe 切换开场白：不同场景（咖啡馆/办公室/战场/茶会）各写一条 |
| **character_book 顶层** | scan_depth / token_budget / recursive_scanning | 预算控制；scan_depth=0 只扫最后一条消息 |
| **extensions 命名空间** | extensions."mycards" = {...} | spec 要求 key 命名空间化防冲突；存来源/皮肤索引/制作元数据 |
| **PNG 嵌卡** | embed_tavern_card.py | 发布用（tEXt chara），头像图当底 |

### ⚪ 可选/进阶（有需求再上）——具体写法见 `07-advanced-mechanisms.md`

| 机制 | 说明 |
|------|------|
| 概率触发 / 包含组 / 定时效果 | entry.extensions 承载（probability/group/sticky/cooldown），官方源码实证 |
| 关键词正则 | entry.keys 一律按正则处理（use_regex: true），含 `(` `[` `*` 要转义 |
| 白羽法（人设挪世界书 @D depth=2） | 独立世界书 + extensions.world 关联，导出自动嵌 character_book |
| 向量存储匹配 | 需要酒馆扩展 + 嵌入模型，entry.extensions.vectorized=true；默认关键词更可预测 |
| V3 格式 | chara_card_v3，data 宽松校验；新卡优先 V2，有需求才升 |

## 坑

- **secondary_keys 必须配 selective=true**，否则白写（spec 明文）
- **中文世界书关键词**：引擎默认 `match_whole_words = false`（中文 wiki 称「默认启用」，以源码为准）；即便开启，中文字符在 JS 里算 `\W`，单字键仍能命中。条目级要显式写 `extensions.match_whole_words`——顶层字段不生效
- **卡里 book 级 `scan_depth`/`token_budget`/`recursive_scanning` 是摆设**——引擎无读取点（源码实证），真正生效的是用户侧全局设置；要控就写条目级 `extensions`
- **位置字段**：卡侧顶层 `position` 只认 before_char/after_char；AN/EM/@D/输出口要写 `extensions.position`（数值枚举 0-7）
- character_book entries 的 `id` 不用参与 prompt（spec：not used in prompt engineering），只是内部索引
- constant 条目也受 token_budget 限制——别全设 constant
