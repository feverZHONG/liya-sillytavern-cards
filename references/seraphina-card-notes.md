# 官方默认卡结构笔记（default_Seraphina.png 逆向）

> 来源：官方仓库 `default/content/default_Seraphina.png`（酒馆自带默认卡，PNG 双嵌 chara(V2)+ccv3(V3)）。
> 这是官方对「一张卡怎么填」的示范——写卡对照物。

## PNG 嵌卡实测
- 同一 PNG 同时嵌 **chara（V2）** 和 **ccv3（V3）** 两个 tEXt chunk
- 读取时 ccv3 优先（官方 parser 行为）
- chara 的 JSON 顶层是**混合结构**：V1 字段（name/description/personality/first_mes/mes_example/scenario）+ spec/spec_version/data

## 字段分布（官方示范）

| 字段 | 值 | 说明 |
|------|-----|------|
| name | "Seraphina" | |
| description | **2851 字符** | 核心！属性标签块 + `<START>` 对话示例全在这 |
| personality | 空 | 官方示范留空 |
| scenario | 空 | 官方示范留空 |
| first_mes | **785 字符** | 场景化开场（被野兽攻击昏迷→被救→自我介绍→关心） |
| mes_example | 空 | 示例进了 description |
| system_prompt | 空 | |
| post_history_instructions | 空 | |
| creator_notes | "Example character..." | |
| tags | 空数组 | |
| extensions | talkativeness: 0.5 / fav: false / world: "Eldoria" / depth_prompt: {"prompt":"","depth":4,"role":"system"} | depth_prompt 官方卡里也是空的，结构在 |
| character_book | 4 条 entries（id/keys/secondary_keys/comment/content） | content 是 Ali:Chat 风格对话示例 |

## description 的三段式（官方示范）

```
[Seraphina's Personality= "caring", "protective", ...22个标签]   ← 性格标签块
[Seraphina's body= "pink hair", "long hair", "amber eyes", ...]  ← 外观标签块
[Genre: fantasy; Tags: adventure, Magic; Scenario: You were attacked by beasts...] ← 场景块

<START>
{{user}}: "Describe your traits?"
{{char}}: *动作描写* "回复..."  ← 长示例对话，教模型风格（官方 785 字级别）
```

## 写卡对照清单

- [ ] description：标签块（性格/外观/场景）+ `<START>` 示例（3 组左右）
- [ ] first_mes：场景化开场，785 字级别详细（按角色风格可短）
- [ ] extensions.depth_prompt：PList 属性块（至少结构在）
- [ ] extensions.talkativeness：0.5
- [ ] 顶层 V1 字段 + data V2 字段双份（官方保存逻辑）
- [ ] character_book：有世界书需求再加（世界观条目）
