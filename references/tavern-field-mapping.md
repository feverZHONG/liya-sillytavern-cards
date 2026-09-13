# 官方实现笔记：V2 卡字段读写映射（src/endpoints/characters.js 精读）

> 来源：官方仓库 `src/endpoints/characters.js`（2026-08-13 精读）。
> 写卡时字段的确切语义/默认值以本笔记为准。

## charaFormatData（前端表单 → V2 卡保存）

保存时**同时写顶层（V1 兼容）和 data（V2）双份**：

### 顶层（V1 兼容 + 老 ST 扩展字段）
| 字段 | 值 |
|------|-----|
| name / description / personality / scenario / first_mes / mes_example | 对应表单值（空→''） |
| creatorcomment | data.creator_notes（老字段别名） |
| avatar | 'none' |
| chat | `{名字} - {时间}` |
| talkativeness | 默认 0.5 |
| fav | 'true' → true |
| tags | 字符串按逗号拆分去空格，或数组原样 |

### data（V2 新字段）
- 六基础字段同上（data.* 双份）
- data.creator_notes / system_prompt / post_history_instructions / creator / character_version / alternate_greetings
- alternate_greetings：数组保留 / 字符串→`[字符串]` / 其他→`[]`

### data.extensions（ST 扩展）
| 字段 | 默认 |
|------|------|
| talkativeness | 0.5 |
| fav | false |
| world | ''（关联世界书文件名） |
| **depth_prompt** | `{"prompt": "", "depth": 4, "role": "system"}` |

depth_prompt 写入逻辑：`depth` 非数字→4；`role` 缺省→'system'。

### character_book（角色世界书）
- 有 `data.world` 时：读对应世界书文件 → `data.character_book`（原样存或 convertWorldInfoToCharacterBook 转换）

## readFromV2（V2 卡 → 前端）

fieldMappings（charField → data 路径）：
```
name→name, description→description, personality→personality,
scenario→scenario, first_mes→first_mes, mes_example→mes_example,
talkativeness→extensions.talkativeness(默认0.5),
fav→extensions.fav(默认false), tags→tags
```
- 缺 extensions.talkativeness → 补 0.5；缺 extensions.fav → 补 false
- 顶层 V1 值与 data V2 值不一致 → 打 warning（以 data 为准覆盖）

## 写卡结论

1. **顶层 V1 字段 + data V2 字段都写**（官方保存就是这么干的）——兼容旧前端
2. `extensions.talkativeness` 必带（0.5）；`extensions.depth_prompt` 结构 `{"prompt","depth":4,"role":"system"}`
3. `alternate_greetings` 用数组
4. character_book 与 world 关联——有世界书再填
