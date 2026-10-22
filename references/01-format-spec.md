# V2 格式规格 · Character Card V2

> 官方查证（2026-08-13）：github.com/SillyTavern/SillyTavern（src/validator/TavernCardValidator.js + src/character-card-parser.js）→ github.com/malfoyslastname/character-card-spec-v2。
> 上游原文（spec / parser / validator）链接见 `02-sources.md`——改格式先回官方仓库对照，别凭记忆。

## V2 必填字段（官方 validator 硬校验，14 个）

`name` `description` `personality` `scenario` `first_mes` `mes_example` `creator_notes` `system_prompt` `post_history_instructions` `alternate_greetings`(数组) `tags`(数组) `creator` `character_version` `extensions`(对象)

`character_book`（角色 lorebook）可选——有则必须含 `extensions`+`entries`(数组)。

## JSON 模板

```json
{
  "spec": "chara_card_v2",
  "spec_version": "2.0",
  "name": "白棠",
  "description": "...",
  "personality": "",
  "scenario": "",
  "first_mes": "...",
  "mes_example": "",
  "data": {
    "name": "白棠",
    "description": "...",
    "personality": "",
    "scenario": "",
    "first_mes": "...",
    "mes_example": "",
    "creator_notes": "...",
    "system_prompt": "...",
    "post_history_instructions": "...",
    "alternate_greetings": [],
    "character_book": {},
    "tags": ["示例", "中文", "白棠"],
    "creator": "填你的署名",
    "character_version": "0.1",
    "extensions": {
      "talkativeness": 0.5,
      "depth_prompt": {"prompt": "[PList]", "depth": 4, "role": "system"}
    }
  }
}
```

## 格式要点

- **纯 JSON 即可导入**；PNG 嵌卡 = tEXt chunk 存 base64 JSON：keyword **`chara`** = V2、**`ccv3`** = V3（读取时 ccv3 优先；官方写入只支持 chara）
- **V3 已存在**（`chara_card_v3`，spec_version 3.0~3.x，data 宽松校验）——做新卡优先 V2，V3 等有实际需求再说
- **顶层 V1 字段 + data V2 双份**——官方 charaFormatData 保存时就是这么写的（顶层兼容旧前端），写卡照做
- `first_mes`（开场白）三件套里**没有现成的**——必须按角色语气创作，这是转换唯一要写新东西的地方

## spec 关键语义（实测原文）

| 字段 | 语义 |
|------|------|
| system_prompt | **替换**用户全局 system prompt（空字符串 = 用默认）；支持 `{{original}}` 占位符还原原设置 |
| post_history_instructions | **替换** ujb/jailbreak 设置（空 = 用默认）；同样支持 `{{original}}` |
| creator_notes | 不进 prompt，用于展示（至少一段） |
| tags / creator / character_version | 不进 prompt engineering，只用于排序/筛选/展示 |
| extensions | **必须**默认 `{}`；key 要命名空间化防冲突（如 `"mycards": {...}`）；导入导出不得销毁未知 key |
| alternate_greetings | 附加开场白数组（酒馆提供 swipe 切换） |
| character_book | 角色专属 lorebook（可选）；与用户 world book 叠加，角色书优先 |
