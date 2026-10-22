# SillyTavern Wiki 写卡核心知识（提炼自 sillytavern.wiki 中文文档）

> 本文件只提炼 sillytavern.wiki 里写卡直接相关的核心（摘录 2026-08-13）。
> 更细的回 wiki 原页面查：<https://sillytavern.wiki/>；上游链接汇总见 `02-sources.md`。

## 一、角色设计（usage/core-concepts/characterdesign）

### 字段语义
- **角色名称是唯一必填字段**，其余可留空
- **角色描述（description）**：始终包含在提示词中，所有重要事实都应填这。可自由文本/伪代码对话风格，长度不限（200~2000 token 都行）
- **永久 Token**（每次生成都发）：角色名称 + 描述框 + 个性框 + 场景框
- **非永久**：第一条消息（仅聊天开始发一次）、示例消息（上下文满被推出，可强制保留）

### first_mes（第一条消息）
- **决定角色写作风格和长度规范**——比其他内容影响更大，按期望的回复方式来写（简短或详细）
- 支持 Markdown 和 HTML
- **备用问候语（alternate_greetings）**：额外滑动选项；群聊中随机选取一条开场

### 高级定义
- 主提示词（system_prompt）：需启用「优先使用角色提示词」才覆盖系统提示词
- 历史后指令（post_history_instructions）：需启用「优先使用角色指令」
- `{{original}}` 占位符：插入系统设置中的默认提示词
- **角色注释（Character's Note）**：特定消息深度注入的强化文本，强化特定角色特征，**permanent**
  - @ 深度：注入位置（0=最后一条消息之后）
  - 角色：user/system/assistant
- 健谈程度（talkativeness）：群聊触发概率 0-100%，默认 50%
- 对话示例（mes_example）：每个示例前加 `<START>`，块式从上下文推出

### token 成本
- 角色定义 token 超模型上下文一半 → 计数器变红，AI「记忆」减半
- 上下文 = 每次请求发给模型的信息；ST 自动分配最优上下文

## 二、世界信息 World Info（usage/core-concepts/worldinfo）

> character_book（角色世界书）的机制同此。写卡加世界书条目时用。

### 条目结构
- **关键词**：触发激活的关键词列表，默认不区分大小写；纯文本关键词**不支持逗号**（逗号是分隔符）；支持正则（Javascript 风格，`/.../` 分隔）
- **可选过滤器**：AND ANY（主+任一过滤）/ AND ALL（主+全部过滤）/ NOT ANY（主+无过滤词）/ NOT ALL（有过滤词则阻止）
- **条目内容**：激活后插入提示词的文本

### 插入顺序
- 数值型；**数值大的插入上下文靠后、影响更大**（100 号在 250 号之前出现）

### 插入位置
- 角色定义之前（适度影响）/ 角色定义之后（影响更大）
- 示例消息之前/之后（解析为示例对话块）
- 作者注记顶部/底部（作者注记禁用=插入频率 0 时被忽略！）
- @ D：指定深度（深度 0 = 提示词底部）
- 输出口：不自动注入，用 `{{outlet::名称}}` 宏控制显示位置
- 角色（系统/用户/助手消息）

### 用法场景
- 角色背景知识 / 人设知识库 / 聊天知识库
- 递归扫描：条目内容可触发其他条目
- ST 扫描缓冲区给每条消息加 `角色名:` 前缀（v1.12.6 后加 `\x01` 前置）——正则可用 `/\x01{{user}}:[^\x01]*?hello/` 匹配特定角色的消息

## 三、高级格式化（usage/core-concepts/advancedformatting，背景）

- 系统提示词：文本补全 API 的主提示词，定义模型角色/基调；聊天补全 API 用提示词管理器
- 上下文模板：按模型定制的角色数据转换规则
- 分词器：token≈3~4 字符
- 停止字符串：JSON 数组，模型输出以停止字符串结尾则移除
- 回复起始内容：预填充提示词最后一行（`<think>\nSure!`），强制模型从该点继续

## 四、宏 macros（usage/core-concepts/macros）

写卡/示例对话里常用的宏：
- `{{user}}`：当前用户/人设名称；`{{char}}`：当前角色名称（示例对话必用）
- `{{random::a::b::c}}`：随机选一个；`{{roll:1d20}}`：骰子
- `{{setvar::k::v}}` / `{{getvar::k}}`：变量读写
- `{{original}}`：系统提示词占位符（高级定义里用）
- `{{outlet::名称}}`：世界书输出口位置控制
- ⚠️ **宏在人设和角色描述中含义相反**——{{user}}/{{char}} 在人设里是互换的（人设描述里 {{char}} 指用户自己）

## 五、人设 personas（usage/core-concepts/personas）

- 人设 = 用户自己的身份（显示名+头像+可选描述），不是角色的
- 角色可「转换为人设」（只用 name+description）
- 写卡不需要管人设，但要知道 {{user}}/{{char}} 的语义切换

## 六、写卡相关 wiki 页面索引

在 <https://sillytavern.wiki/> 站内按路径找：

| 主题 | wiki 路径 |
|------|-----------|
| 角色设计 | `usage/core-concepts/characterdesign` |
| 世界书 | `usage/core-concepts/worldinfo` |
| 高级格式化 | `usage/core-concepts/advancedformatting` |
| 人设 | `usage/core-concepts/personas` |
| 宏 | `usage/core-concepts/macros` |
| 提示词 | `usage/prompts/prompts` |
| 上下文模板 | `usage/prompts/context-template` |
| 指令模式 | `usage/core-concepts/instructmode` |
| 角色管理 | `usage/characters` |
