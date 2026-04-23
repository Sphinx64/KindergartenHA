# -*- coding: utf-8 -*-
"""Mergt die Sektion ab 'einzeltropfen' aus theater-ha in die HA-config (alt_*)."""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(r"c:\theater-ha\config\scripts.yaml")
DST = Path(__file__).resolve().parent / "scripts.yaml"
# Zeilen 2206..4265 (1-basiert) = theater-ha "neue scripte" bis theater_streit_naechste_phase_v2
SLICE_START, SLICE_END = 2205, 4265

BR2_PAT = re.compile(
    r"      brightness_pct: '\{\[ \(states\(''input_number\.theater_master_brightness''\) \| float\(500\)\r?\n"
    r"        / 10\) \| int, 100\] \| min \}\}'"
)


def _fix_blau_farbe_blocks(s: str) -> str:
    parts = s.split("theater_farbe_blau")
    if len(parts) < 2:
        return s
    out = [parts[0]]
    for p in parts[1:]:
        p2, n = BR2_PAT.subn("      brightness_pct: 100", p, count=1)
        out.append(p2)
    return "theater_farbe_blau".join(out)


def _fix_rot_letztes_hell(s: str) -> str:
    m = re.search(
        r"(?ms)^(theater_rot_v2:.*?)(^theater_gelb_v2:)", s
    )
    if not m:
        return s
    rot, nxt = m.group(1), m.group(2)
    it = list(BR2_PAT.finditer(rot))
    if not it:
        return s
    a, b = it[-1].span()
    new_rot = rot[:a] + "      brightness_pct: 100" + rot[b:]
    return s[: m.start()] + new_rot + nxt + s[m.end() :]


def _fix_gelb_letztes_hell(s: str) -> str:
    m = re.search(
        r"(?ms)^(theater_gelb_v2:.*?)(^theater_giftgelb_v2:)", s
    )
    if not m:
        return s
    ge, nxt = m.group(1), m.group(2)
    it = list(BR2_PAT.finditer(ge))
    if not it:
        return s
    a, b = it[-1].span()
    new_ge = ge[:a] + "      brightness_pct: 100" + ge[b:]
    return s[: m.start()] + new_ge + nxt + s[m.end() :]


def _brightness_pass(s: str) -> str:
    s = _fix_blau_farbe_blocks(s)
    s = _fix_rot_letztes_hell(s)
    s = _fix_gelb_letztes_hell(s)
    return s


KEY_MAP = {"theater_finale_v2": "alt_theater_finale_regenbogen"}


def _is_root_key_line(line: str) -> bool:
    t = line.rstrip("\n")
    if not t or t[0] == "#" or t[0] == " ":
        return False
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*:\s*$", t))


def _split_root_blocks(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines(keepends=True)
    keys: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if not line or line[0] in " \n":
            continue
        if _is_root_key_line(line):
            keys.append((i, line.split(":", 1)[0].strip()))
    out: list[tuple[str, str]] = []
    for j, (i, k) in enumerate(keys):
        end = keys[j + 1][0] if j + 1 < len(keys) else len(lines)
        out.append((k, "".join(lines[i:end])))
    return out


def _dest_key(src_key: str) -> str:
    if src_key in KEY_MAP:
        return KEY_MAP[src_key]
    if src_key == "einzeltropfen":
        return "alt_einzeltropfen"
    if src_key.startswith("theater_"):
        return "alt_" + src_key
    return src_key


def _set_root_key_first_line(block: str, new_key: str) -> str:
    lines = block.splitlines(keepends=True)
    if not lines:
        return block
    lines[0] = f"{new_key}:" + (lines[0].split(":", 1)[1] if ":" in lines[0] else "\n")
    return "".join(lines)


def _all_script_replacements(s: str) -> str:
    ids = set(re.findall(r"script\.(theater_[a-z0-9_]+|einzeltropfen)", s))
    for i in sorted(ids, key=len, reverse=True):
        if i == "einzeltropfen":
            s = s.replace("script.einzeltropfen", "script.alt_einzeltropfen")
        else:
            s = s.replace(f"script.{i}", f"script.alt_{i}")
    s = s.replace("script.einzeltropfen", "script.alt_einzeltropfen")
    s = s.replace(
        "script.alt_theater_finale_v2", "script.alt_theater_finale_regenbogen"
    )
    s = s.replace("script.theater_finale_v2", "script.alt_theater_finale_regenbogen")
    return s


def _process_one_block(src_key: str, block: str) -> str:
    dk = _dest_key(src_key)
    t = _set_root_key_first_line(block, dk)
    t = _all_script_replacements(t)
    t = t.replace(
        "value: script.alt_theater_finale_helper_v2",
        "value: script.alt_theater_finale_regenbogen",
    )
    t = t.replace(
        "value: script.alt_theater_finale_regenbogen",
        "value: script.alt_theater_finale_regenbogen",  # idempotent
    )
    if not t.endswith("\n"):
        t += "\n"
    return t


def replace_block(dest: str, key: str, new_block: str) -> str:
    new_block = new_block.rstrip() + "\n"
    m = re.search(
        rf"(?ms)^{re.escape(key)}:.*?(?=\n^alt_[a-z0-9_]+:|\Z)",
        dest,
    )
    if not m:
        return dest
    return dest[: m.start()] + new_block + dest[m.end() :]


def has_block(dest: str, key: str) -> bool:
    return re.search(rf"^{re.escape(key)}:\s*$", dest, re.MULTILINE) is not None


def insert_after_key(dest: str, after_key: str, new_block: str) -> str:
    new_block = new_block.rstrip() + "\n"
    m = re.search(
        rf"(?ms)(^{re.escape(after_key)}:.*?)((?=\n^alt_[a-z0-9_]+:))", dest
    )
    if not m:
        raise SystemExit(f"Einfügen: Anker {after_key} nicht gefunden.")
    at = m.end(1)
    return dest[:at] + "\n" + new_block + dest[at:]


def main() -> None:
    src_lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
    if len(src_lines) < SLICE_END:
        raise SystemExit(
            f"theater-ha zu kurz: {len(src_lines)} (benötigt {SLICE_END}+)"
        )
    raw = "".join(src_lines[SLICE_START:SLICE_END])
    raw = _brightness_pass(raw)
    order_blocks = _split_root_blocks(raw)
    by_key: dict[str, str] = {}
    for sk, bl in order_blocks:
        by_key[_dest_key(sk)] = _process_one_block(sk, bl)

    dest = DST.read_text(encoding="utf-8")

    for sk, _ in order_blocks:
        dk = _dest_key(sk)
        blk = by_key[dk]
        if not has_block(dest, dk):
            print(f"Einfügen geplant: {dk}")
        else:
            n_dest = replace_block(dest, dk, blk)
            if n_dest == dest:
                print(f"Warnung: ersetze {dk} (kein Delta – Pattern?)")
            else:
                dest = n_dest
            print("OK: ersetzt", dk)

    for after_key, dk in (
        ("alt_theater_streit_phase_3_v2", "alt_theater_streit_phase_4_v2"),
        ("alt_theater_streit_phase_4_v2", "alt_theater_streit_phase_5_v2"),
        ("alt_theater_streit_phase_5_v2", "alt_theater_streit_phase_6_v2"),
        ("alt_theater_gelb_v2", "alt_theater_giftgelb_v2"),
        ("alt_theater_finale_regenbogen", "alt_theater_regen_v2"),
        ("alt_theater_streit_p7_v2", "alt_theater_streit_flash_helper_v2"),
        (
            "alt_theater_streit_flash_helper_v2",
            "alt_theater_streit_chaos_helper_v2",
        ),
        (
            "alt_theater_streit_chaos_helper_v2",
            "alt_theater_streit_naechste_phase_v2",
        ),
    ):
        if not has_block(dest, dk) and has_block(dest, after_key) and dk in by_key:
            try:
                dest = insert_after_key(dest, after_key, by_key[dk])
            except (SystemExit, OSError) as e:
                print("Einfügen fehlt", dk, e)
            else:
                print("Eingefügt:", dk, "nach", after_key)

    DST.write_text(dest, encoding="utf-8")
    logp = DST.parent / "_merge_theater_log.txt"
    try:
        logp.write_text(
            "Fertig. Geschrieben: " + str(DST) + "\n", encoding="utf-8"
        )
    except OSError:
        pass
    print("Fertig. Geschrieben:", DST)


if __name__ == "__main__":
    main()
