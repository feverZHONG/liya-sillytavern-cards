#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SillyTavern 角色卡生成器（V2 初稿）

把「角色三件套」（IDENTITY.md / persona-soul.md / AGENTS.md + 可选 外观.md）
生成一张 SillyTavern V2 卡初稿（JSON）。

适配点（对官方 charaFormatData 保存逻辑）：
- 顶层 V1 字段 + data V2 字段双份
- extensions.depth_prompt = PList 基础版（depth=4 role=system）
- extensions.talkativeness = 0.5
- description = 场景块（`<START>` Ali:Chat 示例与 first_mes 是手写活）
- personality / scenario 留空（官方示范）
- system_prompt / post_history_instructions 带 `{{original}}` 前缀（避免整段替换掉用户的全局设置）

用法:
    python3 make_tavern_card.py <角色名|角色目录> [--src 资料根目录] [--out 卡.json]
                                 [--genre 作品名] [--tags a,b] [--creator 署名]
                                 [--scenario 场景说明] [--config 配置文件]

默认值来源（命令行 > 配置文件 > 内置）：
    $TAVERN_CARDS_CONFIG 或 ~/.config/tavern-cards.json
    {"personas_root": "…/personas", "out_dir": "…/cards",
     "genre": "…", "tags": ["…"], "creator": "…", "scenario": "…"}

产物是**初稿**：first_mes / PList 标签 / <START> 示例仍需按角色精修，
精修完跑 validate_tavern_card.py --deep 验证。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

CONFIG_ENV = "TAVERN_CARDS_CONFIG"
DEFAULT_CONFIG = Path.home() / ".config" / "tavern-cards.json"


def load_config(path: str | None) -> dict:
    candidates = [path] if path else [os.environ.get(CONFIG_ENV), DEFAULT_CONFIG]
    for c in candidates:
        if c and Path(c).is_file():
            try:
                return json.loads(Path(c).read_text(encoding="utf-8"))
            except Exception as e:
                print(f"⚠️  配置文件读不了（{c}）：{e}")
    return {}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, title: str) -> str:
    """取 '## <title>' 到下一个 '## ' 之间的正文。"""
    m = re.search(rf"^##\s*{re.escape(title)}\s*$", text, re.M)
    if not m:
        return ""
    nxt = re.search(r"^##\s", text[m.end():], re.M)
    body = text[m.end():m.end() + nxt.start()] if nxt else text[m.end():]
    return body.strip()


def parse_identity(text: str):
    name = re.search(r"-\s*\*\*Name:\*\*\s*(.+)", text)
    vibe = re.search(r"-\s*\*\*Vibe:\*\*\s*(.+)", text)
    return (name.group(1).strip() if name else "",
            vibe.group(1).strip() if vibe else "")


def extract_anchor_names(agents_text: str) -> list:
    """「性格锚点」段：'1. **锚点名** — 说明' → ['锚点名', ...]"""
    sec = _section(agents_text, "性格锚点")
    anchors = []
    for m in re.finditer(r"\*\*([^*]+)\*\*", sec):
        t = m.group(1).strip()
        if t and t not in anchors:
            anchors.append(t)
    return anchors


def _clauses_to_tags(body_text: str, limit: int = 8) -> list:
    """把外观文本切成 ≤16 字的短标签。"""
    tags = []
    for line in body_text.splitlines():
        line = line.strip().lstrip("-*").strip()
        if not line or line.startswith("#"):
            continue
        for part in [p.strip() for p in re.split(r"[，,。;；]", line)]:
            if part and len(part) <= 16 and part not in tags:
                tags.append(part)
            if len(tags) >= limit:
                return tags
    return tags


def extract_body_tags(base: Path, char_name: str, curated_root: Path | None) -> list:
    """外观标签：优先角色目录里的 外观.md / body.md；退回 curated 资料的「5.3 外观特征」段。"""
    for fname in ("外观.md", "body.md", "appearance.md"):
        f = base / fname
        if f.is_file():
            return _clauses_to_tags(_read(f))
    if curated_root and curated_root.is_dir():
        for f in curated_root.glob(f"*{char_name}*"):
            m = re.search(r"###\s*5\.3\s*外观特征(.*?)(?=\n###|\Z)", _read(f), re.S)
            if m:
                return _clauses_to_tags(m.group(1))
    return []


def build_plist(char_name: str, vibe: str, anchors: list, body_tags: list, soul: dict) -> str:
    """PList 基础版：body → Setting → Personality（重要类别放最后）。"""
    personality = [vibe] + anchors
    setting_lines = []
    for line in soul.get("who", "").splitlines():
        clause = re.split(r"[，,。：:]", line.strip(" -*").strip())[0].strip()
        if clause and len(clause) <= 16 and clause not in setting_lines:
            setting_lines.append(clause)
        if len(setting_lines) >= 4:
            break
    lines = []
    if body_tags:
        lines.append(f"[{char_name}'s body= " + ", ".join(f'"{t}"' for t in body_tags[:8]) + "]")
    if setting_lines:
        lines.append(f"[{char_name}'s Setting= " + ", ".join(f'"{t}"' for t in setting_lines[:4]) + "]")
    lines.append(f"[{char_name}'s Personality= " + ", ".join(f'"{t}"' for t in personality[:10] if t) + "]")
    return "\n".join(lines)


def build_description(genre: str, tags: list, scenario: str) -> str:
    """description 只写场景块；`<START>` Ali:Chat 示例留给精修手写。

    别把互动手册里的 ✅/❌ 对照表抄成 user/char 对话——两列会变成复读（见 03-pitfalls.md）。
    """
    inner = "; ".join(filter(None, [f"Genre: {genre}" if genre else "",
                                    f"Tags: {', '.join(tags)}" if tags else "",
                                    f"Scenario: {scenario}" if scenario else ""]))
    return f"[{inner}]"


def gen_first_mes(char_name: str, soul: dict) -> str:
    """初稿（单换行；无占位括号）——发布前必须按角色语气重写。

    Trappu 铁律：别用 `\\n\\n` 分段，模型把双换行当分隔符。
    """
    who = [l.strip() for l in soul.get("who", "").splitlines() if l.strip()]
    first_line = re.split(r"。", who[0])[0].strip() + "。" if who else f"我是{char_name}。"
    return (f"*{char_name}放下手里的活，抬眼看向来人。*\n"
            f"「{first_line}」\n"
            f"*桌上的东西被挪开一角，空出一小块地方。*")


def make_card(char: str, src_root: Path, cfg: dict) -> tuple[dict, Path]:
    base = Path(char).expanduser()
    if not base.is_dir():
        base = src_root.expanduser() / char
    if not base.is_dir():
        raise FileNotFoundError(f"没找到角色目录: {base}")

    identity = parse_identity(_read(base / "IDENTITY.md")) if (base / "IDENTITY.md").is_file() else ("", "")
    name, vibe = identity
    name = name or base.name
    soul_text = _read(base / "persona-soul.md") if (base / "persona-soul.md").is_file() else ""
    soul = {"who": _section(soul_text, "一、我是谁") or _section(soul_text, "我是谁"),
            "core": _section(soul_text, "三、核心") or _section(soul_text, "核心"),
            "bottom": _section(soul_text, "四、底线") or _section(soul_text, "底线")}
    agents_text = _read(base / "AGENTS.md") if (base / "AGENTS.md").is_file() else ""
    agents = {"core_instr": _section(agents_text, "核心指令"),
              "style": _section(agents_text, "说话风格"),
              "forbidden": _section(agents_text, "禁止做的事"),
              "rhythm": _section(agents_text, "对话节奏"),
              "boundary": _section(agents_text, "边界")}

    curated_root = Path(cfg["curated_root"]) if cfg.get("curated_root") else None
    body_tags = extract_body_tags(base, name, curated_root)
    plist = build_plist(name, vibe, extract_anchor_names(agents_text), body_tags, soul)

    genre = cfg.get("genre", "")
    tags = list(cfg.get("tags") or []) + [name]
    creator = cfg.get("creator", "")
    scenario = cfg.get("scenario", "")
    description = build_description(genre, tags, scenario)
    first_mes = gen_first_mes(name, soul)

    system_prompt = "\n".join(filter(None, [agents.get("core_instr", ""),
                                            agents.get("style", ""),
                                            "禁止做的事：\n" + agents.get("forbidden", "")]))
    post_hist = "\n".join(filter(None, ["对话节奏：\n" + agents.get("rhythm", ""),
                                        "边界：\n" + agents.get("boundary", "")]))
    if system_prompt:
        system_prompt = "{{original}}\n你是" + name + "——\n" + system_prompt
    if post_hist:
        post_hist = "{{original}}\n" + post_hist

    data = {
        "name": name,
        "description": description.strip(),
        "personality": "",
        "scenario": "",
        "first_mes": first_mes,
        "mes_example": "",
        "creator_notes": f"由 make_tavern_card.py 生成的初稿（{date.today()}）——first_mes / PList / <START> 示例需精修。",
        "system_prompt": system_prompt.strip(),
        "post_history_instructions": post_hist.strip(),
        "alternate_greetings": [],
        "tags": tags,
        "creator": creator,
        "character_version": "0.1",
        "extensions": {
            "talkativeness": 0.5,
            "depth_prompt": {"prompt": plist, "depth": 4, "role": "system"},
        },
    }
    # 官方 charaFormatData：顶层 V1 字段 + data V2 双份
    card = {
        "spec": "chara_card_v2",
        "spec_version": "2.0",
        "name": name,
        "description": data["description"],
        "personality": data["personality"],
        "scenario": data["scenario"],
        "first_mes": data["first_mes"],
        "mes_example": data["mes_example"],
        "data": data,
    }
    return card, base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("char", help="角色名（在 --src 下找）或角色目录路径")
    ap.add_argument("--src", default=None, help="角色目录的父目录（默认取配置文件 personas_root）")
    ap.add_argument("--out", default=None, help="输出卡 JSON 路径（默认取配置文件 out_dir）")
    ap.add_argument("--config", default=None, help="配置文件路径")
    ap.add_argument("--genre", default=None)
    ap.add_argument("--tags", default=None, help="逗号分隔")
    ap.add_argument("--creator", default=None)
    ap.add_argument("--scenario", default=None)
    ap.add_argument("--no-validate", action="store_true", help="生成后不自动校验")
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.src is not None:
        cfg["personas_root"] = args.src
    if args.genre is not None:
        cfg["genre"] = args.genre
    if args.tags is not None:
        cfg["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
    if args.creator is not None:
        cfg["creator"] = args.creator
    if args.scenario is not None:
        cfg["scenario"] = args.scenario

    src_root = Path(cfg.get("personas_root") or ".")
    out_dir = Path(cfg.get("out_dir") or ".")
    try:
        card, base = make_card(args.char, src_root, cfg)
    except Exception as e:
        print(f"生成失败: {e}")
        return 1

    out = Path(args.out) if args.out else out_dir / f"{card['name']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 已生成: {out}（资料来自 {base}）")
    print("⚠️  待精修：first_mes（场景/动作/钩子）、PList 标签、<START> 示例（手写，别抄对照表）")
    if not args.no_validate:
        r = subprocess.run([sys.executable, str(Path(__file__).parent / "validate_tavern_card.py"), str(out)],
                           capture_output=True, text=True)
        print(r.stdout.strip())
        return 0 if "通过" in r.stdout else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
