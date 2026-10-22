# 踩坑记录 · Pitfalls

> 写卡/转换时踩过的坑。发布前逐条自查。

## first_mes

- **别用第三人称**——酒馆默认开场白是角色自说，写「我是白棠」而不是「白棠是个修表匠」
- **别替用户行动**——只描写角色自己的动作，不 narrate 用户（否则模型学会替用户说话）
- **占位残留必清**——`*门被推开，一道熟悉的身影出现在眼前。*` 这种脚本初稿不能直接发布，必须按角色语气重写（动作/场景/钩子）

## mes_example

- **格式**——用 `<START>` 分隔轮次，用户话写 `{{user}}`（酒馆变量），别写死人名

## system_prompt / post_history_instructions

- **别塞太满**——system_prompt 替换用户全局 system prompt，塞成论文会稀释人格还占上下文；硬规则（口癖/句式）精简填，性格内容进 PList/depth_prompt
- post_history_instructions 同理，替换 ujb 设置，空字符串 = 用默认

## 工具链坑

- **脚本产物缺 depth_prompt**——曾有一批用旧版 make 脚本生成的卡 extensions 全空（无 depth_prompt/talkativeness），只有精修过的卡是完整产物。生成完必须跑 `validate --deep` 确认 depth_prompt 在，不能只看 V2 硬校验
- **validate 脚本单文件参数**——`validate_tavern_card.py <卡.json|卡.png>` 只收一个文件，批量要 for 循环；`--deep` 无 warning 时静默通过（exit 0），不是没执行

## 中文

- **中文卡没问题**——SillyTavern 原生支持 UTF-8，不需要额外转码

## 验证

- **验证用 validate 脚本，不靠跑酒馆**——`validate_tavern_card.py` 是官方 validator 翻译版（node 原版双验证过），卡写没写对它说了算；不用起酒馆实例做导入验证

## 发布

- **PNG 嵌卡导入报错两个原因**（官方 FAQ）：① 卡内没嵌定义信息，只是普通图片；② 扩展名 .png 实际是 WEBP 文件——重命名 .webp 再试。发布前自查文件头是不是 PNG 签名（`\x89PNG`）
