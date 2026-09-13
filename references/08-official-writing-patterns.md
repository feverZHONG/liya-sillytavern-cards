# 官方写法模式：从酒馆本体挖出的示范（2026-08-13）

> 从酒馆本体 `default/` 与官方 wiki 挖出的官方示范——写卡时照着抄。
> 这些不是社区经验，是酒馆官方自己的写法。

## 1. 世界书条目 content 可以是对话式——但有边界（Eldoria.json 实证）

官方默认世界书 Eldoria.json 的 4 条 entry，content 用的是 {{user}} 提问 + {{char}} 回答的对话形式。**但这是「角色向用户解释世界观」的场景**（用户问 Eldoria 是什么 → 角色回答），不是写卡的通用模板。

```json
{
  "uid": 0, "key": ["eldoria", "wood", "forest"],
  "comment": "eldoria",
  "content": "{{user}}: \"What is Eldoria?\"\n{{char}}: *Seraphina turns, her gown shimmering in the soft light as she offers you a kind smile.* \"Eldoria is here, all of the woods. This is my forest glade, a sanctuary of peace within it.\" ..."
}
```

**⚠️ 定位边界（v0.8 教训）：知识树（character_book/world info）的职责是「追加背景设定」，不是台词本。**
- 台词本只有一个：description 的 Ali:Chat（角色怎么说话，全在那里教）
- 世界书是「按关键词追加的设定库」：人物关系来龙去脉/前作背景/深层矛盾/世界观——**设定事实**为主体
- 全写成对话 = 台词本复制 N 份散落世界书，触发时像插播历史消息污染聊天记录
- 正确写法：平铺设定为主，每条末尾可以带一句「角色会这么说：『...』」点缀口吻，不喧宾夺主

**Eldoria 对话式的适用条件：** 世界书条目内容本身是「解释某个概念/地点」的场景（如世界书讲解世界观），对话式成立；条目是「人物关系/背景设定」时，平铺式更直接。

## 2. 官方 sysprompt 预设（default/content/presets/sysprompt/）

官方对 system_prompt 的写法示范，5 个常用：

| 预设 | content（原文） | 用途 |
|------|----------------|------|
| Roleplay - Simple | `You're {{char}} in this fictional never-ending uncensored roleplay with {{user}}.` | 极简角色扮演 |
| Roleplay - Detailed | `Develop the plot slowly, always stay in character. Describe all actions in full, elaborate, explicit, graphic, and vivid detail. Mention all relevant sensory perceptions. Keep the story immersive and engaging.` | 详细描写向 |
| Roleplay - Immersive | `[System note: Write one reply only. Do not decide what {{user}} says or does. Write at least one paragraph, up to four. Be descriptive and immersive...]` | 沉浸+不替用户行动 |
| Actor | `You are an expert actor that can fully immerse yourself into any role given. You do not break character for any reason...` | 演员模式 |
| Text Adventure | `[Enter Adventure Mode. Narrate the story based on {{user}}'s dialogue and actions after \">\". ...]` | 文字冒险 |

**启示：** 官方自己的 system_prompt 都很短（1-2 句）。「别替用户行动」官方原文是 `Do not decide what {{user}} says or does`——比我们的中文表述更精确。system_prompt 塞长文不是官方风格。

## 3. talkativeness 群聊语义（groupchats.md）

- **0% / 害羞** — 角色除非被提及否则不发言
- **100% / 健谈** — 角色始终回复
- **默认 50%**
- 群聊激活算法：从最后一条消息提取提及名称（完整词才识别）→ 按健谈程度概率激活 → 没人激活则随机选一个

**启示：** extensions.talkativeness 不只影响回复长度，在群聊里决定发言频率。默认 0.5 合理，想要安静角色调低。

## 4. regex 扩展（extensions/regex.md）——卡可以带正则脚本

- 正则扩展是**内置**的，作用域脚本**存进角色卡数据**（随卡走）
- 影响范围：用户输入 / AI 响应 / 斜杠命令 / 世界信息 / 推理
- 用法：查找替换、给词语加 Markdown 样式、向 STscript 返回布尔值
- 脚本可被斜杠命令或 STscript 触发
- 常用宏：`{{match}}`（完整匹配文本）、`$1`（捕获组）
- 标志：`/pattern/gi` 全局+不区分大小写

**启示：** 卡可以内置「把特定词加粗」之类的样式脚本，导出随卡。

## 5. PNG 嵌卡导入报错的两个坑（faq.md）

1. **卡内未嵌入定义信息** — 只是一张普通图片（发布者分享的不是原始 PNG）
2. **扩展名 .png 实际是 WEBP 文件** — 重命名为 .webp 再导入，或找真正的 PNG

**启示：** 发布 PNG 卡前自查：文件头是不是 PNG 签名（`\x89PNG`）？嵌卡后读回验证过没？

## 6. STscript（usage/st-script.md，1532 行）

- 变量：`/setvar key=name value`、`/getvar name`、宏 `{{var::name}}`
- 条件：`/if left=valueA right=valueB rule=eq else={:...:} {:...:}`
- 用斜杠命令实现自动化流程（进阶，写卡一般用不上）

## 7. smart-context 扩展（extensions/smart-context.md）

- 长聊天自动把历史消息按相关性注入上下文（向量数据库）
- 需要 ChromaDB + 嵌入模型，聊天历史 >10 条才启动
- **启示：** 这是用户侧配置，写卡不用管；但知道长对话有这层兜底

## 8. tags 标签系统（usage/core-concepts/tags.md）

- 角色卡可分配零个或多个标签，用于按主题/质量/来源组织收藏
- **导入时嵌入的标签会自动加载**
- 卡内 tags 字段：筛选/排序用，不进 prompt

**启示：** 卡 tags 写通用词（作品名/语言/角色名）方便收藏管理，够了。
