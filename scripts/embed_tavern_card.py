#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SillyTavern 角色卡 PNG 嵌卡器（Python 版官方 parser）

从官方仓库 src/character-card-parser.js 翻译（2026-08-13）。
- 把 V2 卡 JSON 嵌入 PNG tEXt chunk（keyword=chara，base64 编码）
- 同时清理旧的 chara/ccv3 chunk（防残留）
- 官方写入只支持 chara(V2)，ccv3(V3) 写入官方也不支持——V3 卡建议直接发 .json

用法:
    python3 embed_tavern_card.py <卡.json> <底图.png> <输出.png>
    python3 embed_tavern_card.py card.json avatar.png card_embedded.png
"""
import base64
import binascii
import json
import struct
import sys
import zlib

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _chunk(ctype: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(ctype + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + ctype + payload + struct.pack(">I", crc)


def embed_card(card_json: str, png_bytes: bytes) -> bytes:
    """把 V2 卡 JSON 嵌入 PNG。返回新 PNG 字节。"""
    if not png_bytes.startswith(PNG_SIG):
        raise ValueError("底图不是 PNG")
    # 先校验 JSON
    card = json.loads(card_json)
    if card.get("spec") != "chara_card_v2":
        raise ValueError("只支持 chara_card_v2 卡嵌入（官方写入仅 chara chunk）")

    pos = len(PNG_SIG)
    chunks = []
    while pos < len(png_bytes):
        length = struct.unpack(">I", png_bytes[pos:pos + 4])[0]
        ctype = png_bytes[pos + 4:pos + 8]
        payload = png_bytes[pos + 8:pos + 8 + length]
        chunks.append((ctype, payload))
        pos += 12 + length

    # 去掉旧的 chara/ccv3 tEXt
    kept = []
    for ctype, payload in chunks:
        if ctype == b"tEXt":
            try:
                kw = payload.decode("latin-1").partition("\x00")[0].lower()
                if kw in ("chara", "ccv3"):
                    continue
            except Exception:
                pass
        kept.append((ctype, payload))

    # IEND 前插入 chara tEXt
    b64 = base64.b64encode(card_json.encode("utf-8")).decode("ascii")
    tEXt = _chunk(b"tEXt", b"chara\x00" + b64.encode("ascii"))
    out = bytearray(PNG_SIG)
    for ctype, payload in kept:
        if ctype == b"IEND":
            out += tEXt
        out += _chunk(ctype, payload)
    return bytes(out)


def main():
    if len(sys.argv) < 4:
        print("用法: embed_tavern_card.py <卡.json> <底图.png> <输出.png>")
        return 2
    card_json = open(sys.argv[1], encoding="utf-8").read()
    png = open(sys.argv[2], "rb").read()
    out = embed_card(card_json, png)
    with open(sys.argv[3], "wb") as f:
        f.write(out)
    print(f"✅ 已嵌入: {sys.argv[3]} ({len(out)}B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
