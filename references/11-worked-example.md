# 完整实例：从一堆资料到一张能用的卡

> 演示角色 **白棠**（原创，非任何作品角色）走一遍全流程：资料 → 设定文本 → 卡初稿 → 精修 → 校验 → 发布。
> 所有文件在 `examples/` 里，命令可以照着重跑一遍。

## 0. 手里有什么

写卡不是从空白开始，是从**一堆碎片**开始。比如：

```
旧城巷尾有个修表的，招牌叫「三点半」，因为橱窗里那只钟永远慢三秒
她话很少，说时间必带数字；被夸就不接话
围裙口袋里常年一颗橘子硬糖
「这个不修。」是她的口头禅
```

先跑 `10-setting-writing-template.md`（角色设定写作模板）把这些碎片填成一份**设定文本**——
按「基础信息 / 外貌 / 性格 / 小习惯 / 三层情绪反馈 / 与用户的关系」分节，缺口一目了然：

```text
基础信息｜名字：白棠 · 身份：钟表铺的修表匠（旧城巷尾）· 最喜欢的东西：橘子硬糖
……
言行规范｜语言习惯：句子短，句末常停半秒再补一句
　　　　　说话风格：提到时间必须带数字
　　　　　情绪点：被夸时会把话题拧回表上
```

设定文本再拆成工具要的**三件套**（见 `examples/白棠/`，四个文件不到 4KB）：

| 文件 | 干什么 |
|:-----|:-------|
| `../examples/白棠/IDENTITY.md` | 名字 + 一句话定位 |
| `../examples/白棠/persona-soul.md` | 第一人称自述（我是谁 / 怎么说话 / 核心 / 底线） |
| `../examples/白棠/AGENTS.md` | 互动手册（核心指令 / 说话风格 / 示例 / 性格锚点 / 对话节奏 / 禁止 / 边界） |
| `../examples/白棠/外观.md` | 外观一行一条 |

## 1. 生成初稿

```bash
cd skills/sillytavern-cards
python3 scripts/make_tavern_card.py 白棠 --src examples \
  --genre "现代日常" --tags "示例,中文" --creator "你的署名" \
  --scenario "旧城巷尾的钟表铺，夜里十一点还亮着灯。" \
  --out /tmp/baitang-draft.json
```

实际输出：

```text
✅ 已生成: /tmp/baitang-draft.json（资料来自 examples/白棠）
⚠️  待精修：first_mes（场景/动作/钩子）、PList 标签、<START> 示例（手写，别抄对照表）
✅ V2 通过（/tmp/baitang-draft.json）
📊 token 统计（tiktoken cl100k_base）：累计=817  恒定=278
```

脚本干的活（都是机械部分）：顶层 V1 + `data` V2 双份、`depth_prompt` 骨架、`talkativeness: 0.5`、
`system_prompt` / `post_history_instructions` 带 `{{original}}` 前缀、字段硬校验。

## 2. 精修三处（这一步是手写活）

| 字段 | 初稿 | 精修后 |
|:-----|:-----|:-------|
| `first_mes` | 「*白棠放下手里的活，抬眼看向来人。*」——泛，没场景 | 夜里十一点四十七、灯管闪两下、准数报时刻、末句「……水在炉子上」 |
| PList | Vibe 整句 + 锚点名，`Setting` 是散句 | body 收成短标签；`Setting` 换身份/地点；`Personality` 换成**行为锚点**（话短 / 被夸就拧回表上 / 句末停半秒再补一句） |
| `description` | 只有场景块 | 补三组 `<START>`：待客 / 独处 / 被夸——三个不同性格面，user 与 char 的话**不能同句** |

精修后的成品：`examples/白棠-卡.json`（`character_version: 0.2`）。

精修时对照 `AGENTS.md` 逐条落实硬规则——**漏一条，卡里的人就不像**：
「时间必须说准数」进 system_prompt；「被夸不接」「打烊后句子长一句」进 post_history_instructions。

## 3. 校验

```bash
python3 scripts/validate_tavern_card.py examples/白棠-卡.json --deep
```

```text
✅ V2 通过（examples/白棠-卡.json）
📊 token 统计（字符估算（中文≈1.5/其他≈0.3））：累计=1164  恒定=543
```

`--deep` 无输出 = 无 warning（占位残留 / `<START>` 复读 / depth_prompt 缺失 / 顶层缺 V1 双份都会被点出来）。
**注意别在成品上直接重跑 `make`**——生成初稿另存路径，成品单独改。

## 4. 发布

- 直接发 `.json`，或 `embed_tavern_card.py 卡.json 底图.png 输出.png` 嵌成 PNG 卡（头像图当底）
- PNG 发布前自查文件头是不是 `\x89PNG`（WEBP 改名成 .png 是导入失败的头号原因，见 `03-pitfalls.md`）

## 这个实例证明了什么

1. **工具只做机械部分**——顶层双份、PList 骨架、字段校验；像不像这个人是手写的
2. **上游是设定文本**——资料乱就直接写卡，写出来一定是散的（第 0 步别跳）
3. **口径可搬**——把 `examples/白棠/` 换成你自己的角色目录，流程一个字不用改
