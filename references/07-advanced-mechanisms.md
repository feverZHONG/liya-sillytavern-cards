# 进阶机制落地指南：有需求时怎么写

> 2026-08-13 从官方源码 `src/endpoints/characters.js` 的 `convertWorldInfoToCharacterBook` 查证——
> 酒馆把世界书转角色书时，概率/包含组/定时效果等**全部放 `entry.extensions`**，卡 JSON 直接可带，不需要 UI 手动配。
> 本文档是 06-mechanism-checklist「⚪ 可选/进阶」的具体写法。有需求时按这里抄。

## 承载位置：entry.extensions（官方源码实证）

| extensions key | 对应 UI | 用法示例 |
|:---------------|:--------|:--------------|
| `probability` + `useProbability` | 触发概率 | 「橘子硬糖」条目 90% 触发，偶尔静默让对话自然 |
| `group` / `group_weight` / `group_override` / `use_group_scoring` | 包含组 | 「称呼切换」组：待客（叫「先生/小姐」）vs 独处（直呼其名）同组只激活一条 |
| `sticky` / `cooldown` / `delay` | 定时效果 | 「赶工」条目 sticky=3 保持语境；「旧伤」条目 cooldown 防刷屏 |
| `selectiveLogic` | 二级键过滤逻辑 | 0=AND_ANY / 1=NOT_ALL / 2=NOT_ANY / 3=AND_ALL（源码枚举 world-info.js:33-38，旧记录写反过） |
| `depth` + `role` | @D 深度插入 | depth=2 + role=system 保人设永生难忘（白羽法） |
| `match_whole_words` | 全词匹配 | 中文设 false（不用空格分词会误伤） |
| `case_sensitive` | 大小写敏感 | 中文设 false |
| `triggers` | 生成类型 | 只普通/滑动时触发 |
| `outlet_name` | 输出口 | `{{outlet::名称}}` 手动定位 |
| `vectorized` | 向量化 | 默认 false，需要向量扩展 |
| `prevent_recursion` / `delay_until_recursion` / `exclude_recursion` | 递归控制 | 静态条目 prevent_recursion 防激活链 |
| `automation_id` | STscript 联动 | 与快速回复联动执行 |
| `ignore_budget` | 忽略预算 | 核心条目可设 true（慎用） |
| `match_character_*` / `match_persona_description` | 附加匹配来源 | 用角色描述/性格当触发源 |
| `display_index` | UI 显示 | 不用管 |

**注意（2026-09-16 源码更正）：** 键是不是正则看**字符串形状**——写成 `/pattern/flags` 才当正则（`parseRegexFromString`），否则一律纯文本 `includes()`，含 `(` `[` `*` 也不用转义。卡里顶层 `use_regex: true` 引擎不读。详见 `sillytavern-worldbook/references/12-worldbook-mechanics.md`。

## 各机制落地写法（可直接抄的 JSON 片段）

### 1. 概率触发（随机事件/偶尔提）

```json
{
  "id": 8, "keys": ["糖", "橘子糖", "甜"],
  "content": "白棠的口袋里常年有一颗橘子硬糖。修表修到卡壳的时候会摸出来含着，被人看见就说「手上油，含着方便」。",
  "extensions": {
    "probability": 90,
    "useProbability": true
  }
}
```

### 2. 包含组（同组只激活一条）

「称呼切换」场景：同一场景关键词触发两条候选，只选一条。

```json
{
  "id": 9, "keys": ["客人", "收表", "生意"],
  "content": "待客时的白棠：称呼客人「先生/小姐」，话短、只谈表，「这块走快了四分钟，后天来取」。",
  "extensions": { "group": "baitang-call", "group_weight": 50 }
},
{
  "id": 10, "keys": ["独处", "打烊", "夜里"],
  "content": "独处的白棠：只叫名字，句子比白天长一点，「……你坐，水在炉子上。别碰第三格柜子」。",
  "extensions": { "group": "baitang-call", "group_weight": 50 }
}
```

### 3. 定时效果（粘性/冷却/延迟）

战斗场景保持 3 条消息的语境；牙医条目冷却防重复刷屏。

```json
{
  "id": 11, "keys": ["赶工", "急件", "交货"],
  "content": "赶工的白棠：桌上摊开零件盘，说话更短，抬头看人只用半秒，「别说话。」
  "extensions": { "sticky": 3, "cooldown": 2 }
}
```

### 4. 白羽法：人设挪世界书按深度插入（extensions.world 关联）

> 白羽笔记核心：世界书写得很复杂时，把人设（XML/YAML 块）挪进**独立世界书文件**，条目设
> Status=蓝(constant) + Position=@D + Depth=2，然后角色卡绑定该世界书（extensions.world=文件名），
> 导出时 character_book 自动嵌入。可保证小克永生难忘设定——**但只适合绝对固定的设定，可塑性内容别放**。

实施蓝图：
1. 建一本**全局世界书**：把多张卡共用的世界观条目（地理/组织/术语）集中进去
2. 各角色卡的 `extensions.world` 关联它；角色专属的关系网留在各自的 `character_book`
3. 需要时再做——先确认酒馆实例的世界书体系怎么管理

### 5. V3 格式（chara_card_v3）

- V3 = `spec: "chara_card_v3"` + `spec_version: 3.0~3.x`，data 宽松校验
- 官方默认卡 PNG 是 chara(V2)+ccv3(V3) 双嵌——V3 已主流，但 V2 兼容性最稳
- **决策：新卡优先 V2；只有需要 V3 宽松结构/新字段时才升**（当前无需求）

## 判断标准：什么情况算「有需求」

| 现象 | 该上什么 |
|:-----|:---------|
| 提到甜食每次都说同一段设定，显重复 | 概率 90%（偶尔静默） |
| 关键词触发太频繁/太宽泛 | 正则精调 keys 或加 secondary_keys+selective |
| 两个场景的设定互相打架 | 包含组，同组只激活一条 |
| 提到关键词后语境需要保持几轮 | sticky 粘性 |
| 同一条目 3 轮内反复触发烦人 | cooldown 冷却 |
| 世界观复杂到角色卡塞不下 | 全局世界书 + extensions.world 关联 |
| 同一条目要按角色分流（A 知道 B 不知道） | 独立世界书 + 条目级 `characterFilter`（卡内书做不到） |
| 需要可塑性/随机惊喜 | 概率/向量化（向量需要扩展，默认关键词） |

## 原则

- **不为用而用**——进阶机制都占 token 或引入不确定性，基础三件套先到位
- **一次只上一个**——加一个机制跑一轮测试看效果，不堆叠
- **不确定性机制谨慎**——wiki 明说「需要确定性和可预测的结果，请坚持使用关键词匹配」
