# 资料来源 · 查证与素材

> 写卡前先看这页：资料从哪来、哪份是 ground truth、本机镜像放哪。
> 改格式 / 看实现 / 查文档 → 先翻本目录 references，再回官方仓库对照。

## 一、上游（ground truth）

| 来源 | 用途 | 地址 |
|:-----|:-----|:-----|
| SillyTavern 本体源码 | 字段读写、validator、PNG 嵌卡实现的最终依据 | <https://github.com/SillyTavern/SillyTavern> |
| Character Card V2 spec | 字段语义原文 | <https://github.com/malfoyslastname/character-card-spec-v2> |
| sillytavern.wiki（官方 wiki） | 角色设计 / 世界书 / 宏 / 提示词管理器 | <https://sillytavern.wiki/> |
| 官方默认卡 `default_Seraphina.png` | 官方「一张卡怎么填」的示范 | 酒馆仓库 `default/content/` |
| Trappu《PLists + Ali:Chat》指南 | PList / Ali:Chat 写法的源头（PygmalionAI Wiki） | <https://wikia.schneedc.com/bot-creation/trappu/introduction> |
| 空桑《酒馆简单攻略》 | 社区实战：格式心法、token 效率 | <https://www.hqshi.cn/info/knowledge/sillytavern> |
| 飞书「角色卡编写」知识库 | Trappu 中文翻译 + 車卡教學 + 白羽 XML 笔记 | <https://sqivg8d05rm.feishu.cn/wiki/Nazdwr3H9inZs6k1aIQcFPA0nth> |
| SillyTavern 中文文档（第三方 retype 站） | 与 wiki 同源的中文文档 | <https://docs.eigeen.cc/> |
| 社区编卡器 | 可视化编卡 + AI 补全 | <https://character-tools.srjuggernaut.dev/> |

**第三方资料不随本仓库分发**：Trappu 指南（原文与中译）、空桑攻略全文、飞书知识库、sillytavern.wiki 全站镜像、官方 spec / parser / validator 源码——上面给链接，自己从源头取。
本目录里的文档都是**自己的查证笔记**：引用要点可以，别把别人的原文整段搬进来。

## 二、本机镜像（作者环境约定，换自己的路径即可）

| 内容 | 位置 |
|:-----|:-----|
| 酒馆本体（release tarball） | `downloads/SillyTavern/`——查 `src/validator/`、`src/character-card-parser.js`、`default/content/` |
| sillytavern.wiki 全站镜像 | `downloads/sillytavern-wiki/`（镜像脚本自备） |
| 第三方资料（社区指南 / 飞书知识库 / wiki / 官方 spec 原文） | `workspace/references/酒馆社区资料/` |

## 三、角色素材从哪来

原料不是「印象」，是**可核对的资料**。一个角色的料源清单：

| 料 | 去哪找 | 进卡位置 |
|:---|:-------|:---------|
| 基础信息 / 背景 / 剧情 | 作品 wiki、官方设定集 | PList `Setting=` + `character_book` 条目 |
| 性格 / 锚点 | 官方人物介绍、剧情表现 | PList `Personality=` |
| 外观特征 | 官方立绘说明、设定资料 | PList `body=` |
| 语气 / 台词 | 语音、剧情对话、语音集 | first_mes 与 Ali:Chat 的素材（**设定文本里禁止摘抄**，见模板核心规则 3） |
| 关系网 | 官方关系图、剧情 | `character_book` 条目（平铺设定为主） |

**两条纪律：**

1. **世界书是设定库，不是台词本**——台词的活由 description 的 Ali:Chat 干（见 `08-official-writing-patterns.md`）
2. **资料不足先补资料**——设定写不出来通常是资料没到位，不是文笔问题；缺的部分去补料，别硬编
