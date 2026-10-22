#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SillyTavern 角色卡校验器（Python 版官方 validator）

从官方仓库 src/validator/TavernCardValidator.js 翻译（2026-08-13）。
支持:
- V1 / V2 / V3 spec 识别
- V2 data 14 必填字段硬校验 + character_book 校验
- PNG 嵌卡输入: 自动从 tEXt chunk 抽取 chara(V2)/ccv3(V3) base64 JSON

用法:
    python3 validate_tavern_card.py <卡文件.json|卡文件.png>
    退出码: 0=通过(打印 spec 版本), 1=未通过(打印原因), 2=文件读不了
"""
import base64
import json
import struct
import sys
import zlib

V1_FIELDS = ["name", "description", "personality", "scenario", "first_mes", "mes_example"]
V2_FIELDS = [
    "name", "description", "personality", "scenario", "first_mes", "mes_example",
    "creator_notes", "system_prompt", "post_history_instructions", "alternate_greetings",
    "tags", "creator", "character_version", "extensions",
]


def _extract_png_text_chunks(data: bytes) -> dict:
    """从 PNG 字节里抽 tEXt chunk（keyword -> text）。"""
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("不是 PNG 文件")
    pos = 8
    out = {}
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        if ctype == b"tEXt":
            try:
                kw, _, text = payload.decode("latin-1").partition("\x00")
                out[kw.lower()] = text
            except Exception:
                pass
        pos += 12 + length
    return out


def load_card(path: str):
    """读卡文件: .json 直接解析, .png 抽 tEXt chara/ccv3。返回 (card_dict, source_note)。"""
    with open(path, "rb") as f:
        raw = f.read()
    if path.lower().endswith(".png"):
        chunks = _extract_png_text_chunks(raw)
        if "ccv3" in chunks:
            return json.loads(base64.b64decode(chunks["ccv3"])), "PNG ccv3(V3)"
        if "chara" in chunks:
            return json.loads(base64.b64decode(chunks["chara"])), "PNG chara(V2)"
        raise ValueError("PNG 里没有 chara/ccv3 元数据")
    return json.loads(raw.decode("utf-8")), path


def validate(card: dict):
    """返回 (version, error)。version: 1/2/3 或 False。error: None 或原因字符串。

    注意官方卡是混合结构：顶层保留 V1 6 字段（兼容旧前端）+ data 里 V2/V3 新格式。
    检测到 spec 字段时优先按 V2/V3 判定（贴近实际使用），纯 V1 卡才报 1。
    """
    has_spec = isinstance(card.get("spec"), str)
    # V2
    if card.get("spec") == "chara_card_v2" and card.get("spec_version") == "2.0":
        data = card.get("data")
        if not isinstance(data, dict):
            return False, "No tavern card data found"
        missing = [f for f in V2_FIELDS if f not in data]
        if missing:
            return False, f"data.{missing[0]}"
        if not isinstance(data["alternate_greetings"], list):
            return False, "data.alternate_greetings must be array"
        if not isinstance(data["tags"], list):
            return False, "data.tags must be array"
        if not isinstance(data["extensions"], dict):
            return False, "data.extensions must be object"
        cb = data.get("character_book")
        if cb is not None:
            if not isinstance(cb, dict) or "extensions" not in cb or "entries" not in cb:
                return False, "data.character_book.extensions/entries"
            if not isinstance(cb["entries"], list) or not isinstance(cb["extensions"], dict):
                return False, "data.character_book entries/extensions type"
        return 2, None
    # V3
    if card.get("spec") == "chara_card_v3":
        try:
            v = float(card.get("spec_version", "0"))
        except (TypeError, ValueError):
            return False, "spec_version"
        if 3.0 <= v < 4.0 and isinstance(card.get("data"), dict):
            return 3, None
        return False, "V3 spec_version 需 3.0~3.x"
    # V1: 顶层 6 字段（无 spec 的纯 V1 卡，或顶层兼容层）
    if not has_spec:
        missing = [f for f in V1_FIELDS if f not in card]
        if not missing:
            return 1, None
    return False, "neither V1 nor V2/V3 matched"


def deep_check(card: dict):
    """写卡质量深度检查（官方 validator 之外的实战检查）。返回 (pass, warnings)。

    覆盖：depth_prompt 结构 / 顶层 V1 双份 / first_mes 替用户行动 / first_mes 占位残留。
    V2/V3 都查（V3 的 data 结构与 V2 相同，占位符残留检查对 V3 尤其重要——需补充卡模板）。
    """
    warnings = []
    spec = card.get("spec")
    if spec not in ("chara_card_v2", "chara_card_v3"):
        return True, warnings
    data = card.get("data", {})
    ext = data.get("extensions", {})

    # 1. 占位符残留（需补充卡模板：personality/scenario/mes_example 标【需补充】）
    for f in ("personality", "scenario", "mes_example", "description", "first_mes"):
        v = data.get(f, "")
        if isinstance(v, str) and "【需补充】" in v:
            warnings.append(f"⚠️ data.{f} 还有【需补充】占位残留——发布前必须填真实内容")
        if isinstance(v, str) and "【这里" in v:
            warnings.append(f"⚠️ data.{f} 还有模板占位残留（【这里...】）——发布前必须填真实内容")

    # 1b. <START> Ali:Chat 复读检测（2026-08-26：旧脚本把 AGENTS 对照表两列抄成 user/char 对话，
    #     示例变成复读用户——模型学到的是复读。对照表不是对话轮次，user/char 同句=污染示例）
    #     2026-09-26：示例可归位到 mes_example（槽位归位），两处都扫
    for src in ("description", "mes_example"):
        text = data.get(src, "")
        if not (isinstance(text, str) and "<START>" in text):
            continue
        for i, block in enumerate(text.split("<START>")[1:], 1):
            if "{{user}}" in block and "{{char}}" in block:
                u = block.split("{{user}}:")[1].split("{{char}}:")[0].strip()
                c = block.split("{{char}}:")[1].split("<START>")[0].strip()
                if u and u == c:
                    warnings.append(f"⚠️ {src} 第 {i} 个 <START> 块 {{user}} 与 {{char}} 同句复读——示例污染，删掉或改手写对话轮次")

    # 1c. PList 施工注释残留（2026-08-26：make 脚本曾把「# PList 基础版——需按角色精修」写进 prompt，
    #     施工注释直接暴露给模型）
    dp_prompt = ""
    dp = ext.get("depth_prompt")
    if isinstance(dp, dict):
        dp_prompt = dp.get("prompt", "")
    if isinstance(dp_prompt, str) and ("PList 基础版" in dp_prompt or "需按角色精修" in dp_prompt):
        warnings.append("⚠️ depth_prompt.prompt 还有「PList 基础版/需按角色精修」施工注释——删掉，注释不进 prompt")

    # 2. depth_prompt 结构（写卡核心：PList 位置）
    dp = ext.get("depth_prompt")
    if not isinstance(dp, dict):
        warnings.append("⚠️ extensions.depth_prompt 缺失——PList 属性块应放这里（长对话保人设）")
    else:
        if not dp.get("prompt"):
            warnings.append("⚠️ depth_prompt.prompt 为空——PList 标签块没写")
        try:
            depth = int(dp.get("depth", 4))
            if not (0 <= depth <= 10):
                warnings.append(f"⚠️ depth_prompt.depth={depth} 超出常见范围 0-10")
        except (TypeError, ValueError):
            warnings.append("⚠️ depth_prompt.depth 不是数字")
        if dp.get("role") not in ("system", "user", "assistant"):
            warnings.append("⚠️ depth_prompt.role 建议 system/user/assistant")
    if "talkativeness" not in ext:
        warnings.append("⚠️ extensions.talkativeness 缺失（默认 0.5）")

    # 3. 顶层 V1 双份（官方 charaFormatData 保存逻辑）
    for f in ("name", "description", "personality", "scenario", "first_mes", "mes_example"):
        if f not in card:
            warnings.append(f"⚠️ 顶层缺 V1 字段 `{f}`——官方保存是顶层+data 双份，建议补")
        elif isinstance(card.get(f), str) and "【需补充】" in card.get(f, ""):
            warnings.append(f"⚠️ 顶层 `{f}` 还有【需补充】占位残留——需与 data 同步填")

    # 4. first_mes 质量
    fm = data.get("first_mes", "")
    if not fm:
        warnings.append("⚠️ first_mes 为空（可留空让用户自定义场景，但通常该有）")
    else:
        if "请按角色语气精修" in fm or "初稿" in fm or "占位" in fm:
            warnings.append("⚠️ first_mes 还有生成占位残留——发布前必须改写成角色语气")
        # 替用户行动：*你...* 动作描写
        import re
        if re.search(r"\*你[^*]{0,20}\*", fm):
            warnings.append("⚠️ first_mes 出现 `*你...*` 动作描写——替用户行动，模型会学会代打（只描写角色自己的动作）")

    return len(warnings) == 0, warnings


def count_card_tokens(card: dict):
    """按酒馆 UI 同口径统计卡 token（RossAscends-mods.js RA_CountCharTokens）。

    口径（index.html 里 data-token-counter 元素）：
    - 累计 = name + description + personality + scenario + first_mes + mes_example
            + system_prompt + post_history_instructions + depth_prompt.prompt
    - 恒定 = 其中标 data-token-permanent 的字段（name/description/personality/scenario/depth_prompt）
    注意：alternate_greetings / character_book 不计入酒馆卡片面板统计（世界书单独算）。

    返回 (total, permanent, tokenizer_note)。优先 tiktoken（cl100k_base，与酒馆 getTokenCountAsync
    同为 BPE 系，量级一致），不可用则按中文字符 ≈1.5 token、其他 ≈0.3 token 估算。
    """
    data = card.get("data", card)
    ext = data.get("extensions", {})
    perm_fields = ["name", "description", "personality", "scenario"]
    all_fields = perm_fields + ["first_mes", "mes_example", "system_prompt", "post_history_instructions"]

    enc = None
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
    except Exception:
        enc = None

    def count(s: str) -> int:
        s = s or ""
        if enc is not None:
            return len(enc.encode(s))
        cn = sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")
        return int(cn * 1.5 + (len(s) - cn) * 0.3)

    total = 0
    permanent = 0
    for f in all_fields:
        n = count(data.get(f, ""))
        total += n
        if f in perm_fields:
            permanent += n
    dp = ext.get("depth_prompt", {}).get("prompt", "") if isinstance(ext.get("depth_prompt"), dict) else ""
    total += count(dp)
    permanent += count(dp)

    note = "tiktoken cl100k_base" if enc is not None else "字符估算（中文≈1.5/其他≈0.3）"
    return total, permanent, note


def main():
    if len(sys.argv) < 2:
        print("用法: validate_tavern_card.py <卡.json|卡.png> [--deep]")
        return 2
    if sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    deep = "--deep" in sys.argv
    try:
        card, note = load_card(sys.argv[1])
    except Exception as e:
        print(f"读取失败: {e}")
        return 2
    ver, err = validate(card)
    if ver:
        print(f"✅ V{ver} 通过（{note}）")
        total, permanent, tok_note = count_card_tokens(card)
        print(f"📊 token 统计（{tok_note}）：累计={total}  恒定={permanent}")
        if deep:
            ok, warnings = deep_check(card)
            if warnings:
                print("--- 深度检查 ---")
                for w in warnings:
                    print(w)
            return 0 if ok else 1
        return 0
    print(f"❌ 校验失败: {err}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
