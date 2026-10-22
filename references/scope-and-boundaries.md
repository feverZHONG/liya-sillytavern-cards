# 定位与适用面（跟角色设定 / 酒馆卡 / 角色档案的分界）

> 一页说清：本 skill 管什么、不管什么。「写人格」这件事在库里分三家，规则不同**甚至相反**——混用必出事。
> 别处（如角色设定模板）再提本 skill 时，以本文件为准。

## 一句话定位

**给 AI agent 写它自己的身份文件**（SOUL.md / system prompt 里的人格部分）——目标是让 agent **做得对**：说话像它、决策像它。
判据一句话：**这段文字有没有指导我行动？没有就砍。**

## 三家分工（同族不同用）

| | `persona-authoring`（本 skill） | 角色扮演设定（`sillytavern-cards` + 设定模板） | `chara-profile` |
|:--|:--|:--|:--|
| 对象 | AI agent **自己**（SOUL.md） | 演给用户看的**角色**（酒馆卡 / 设定文本） | 真实作品里的角色（**公开资料**） |
| 目标 | **做得对**——决策与语气一致 | **演得像**——外貌、情绪、关系都要 | **记得准**——多源核实、可追溯 |
| 外貌描写 | ❌ 减法对象（没人看得到它长什么样） | ✅ 必须留（模板「二、外貌」整节） | ✅ 客观收录 |
| 语录 | 原句可作行为锚点与示例 | ❌ **禁止摘抄**，须自主拟定（模板核心规则 3） | ✅ 照录 + 标来源 |
| 情绪 | 写成行为规则（触发条件 → 反应） | ✅「三层情绪反馈」逐档写 | 只记原作描写 |
| 输出物 | SOUL.md / 身份文件 | 设定文本 → V2 卡（PList / Ali:Chat） | 五节档案 md |
| 落盘换行 | 散文式，不敏感 | **换行即结构**（提示词模板，必须用代码块包住） | 不敏感 |

**选哪家（一句话判据）：**

- 「让 agent 说话/决策像它」→ 本 skill
- 「写一个能演起来的角色」→ 酒馆那条线（`sillytavern-cards`，上游是设定模板）
- 「把某作品角色的资料整理准」→ `chara-profile`

## 最容易踩的四个误用

1. **拿 SOUL 的减法去砍角色设定** → 把「外貌」「三层情绪反馈」当装饰删掉，角色就演不起来了
2. **拿角色模板的规则来写 SOUL** → 照搬「禁止动作/场景/心理描述」，助手的行为锚点全丢，人格变成产品说明书
3. **把 agent 人格当作品角色建档**（或反过来）→ 档案要求来源可查，而人格文件是**自定**的，没有第三方来源
4. **语录处理混用** → 角色设定禁摘抄（防复读），人格文件反而要原句（原句是硬规则与示例的来源）

## 配套（跨文件 / 跨仓库）

- **角色设定写作模板 v1.2**（fever钟，B站 cv47543229）
  本地：`skills/sillytavern-cards/references/10-setting-writing-template.md`
  公开仓库：<https://github.com/feverZHONG/liya-persona-authoring> → `references/setting-writing-template.md`
- 酒馆写卡（公开仓库 <https://github.com/feverZHONG/liya-sillytavern-cards>，本机 skill `sillytavern-cards`）与精修：`tavern-card-refinement`
- 客观角色档案：`chara-profile`
- 本 skill 自己的减法流程：`references/identity-file-debloat.md`
