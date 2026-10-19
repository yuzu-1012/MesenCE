#!/usr/bin/env python3
"""Helpers for MesenCE localization XML files.

Usage:
    python3 tools/localization/xmltool.py init zh-CN
    python3 tools/localization/xmltool.py stats zh-CN
    python3 tools/localization/xmltool.py check zh-CN
    python3 tools/localization/xmltool.py merge zh-CN

The English file (resources.en.xml) is the source of truth for keys.
Translated files must contain exactly the same keys; missing keys fall back
to English at runtime, but `check` reports them so translators can see gaps.
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCALIZATION_DIR = ROOT / "UI" / "Localization"
SOURCE = LOCALIZATION_DIR / "resources.en.xml"

PLACEHOLDER_RE = re.compile(r"\{(\d+)")


def target_path(code: str) -> Path:
    return LOCALIZATION_DIR / f"resources.{code}.xml"


def parse(path: Path) -> ET.ElementTree:
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(path, parser=parser)
    return tree


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def collect(root: ET.Element) -> dict[tuple[str, ...], ET.Element]:
    """Return a flat key -> element mapping for the parts we translate."""
    keys: dict[tuple[str, ...], ET.Element] = {}

    for message in root.findall("./Messages/Message"):
        keys[("message", message.get("ID", ""))] = message

    for enum in root.findall("./Enums/Enum"):
        enum_id = enum.get("ID", "")
        for value in enum.findall("Value"):
            keys[("enum", enum_id, value.get("ID", ""))] = value

    for form in root.findall("./Forms/Form"):
        form_id = form.get("ID", "")
        for control in form.findall("Control"):
            keys[("control", form_id, control.get("ID", ""))] = control

    return keys


def placeholders(text: str) -> list[str]:
    return PLACEHOLDER_RE.findall(text or "")


def load(code: str) -> tuple[ET.ElementTree, ET.Element, dict[tuple[str, ...], ET.Element]]:
    path = target_path(code)
    if not path.exists():
        raise SystemExit(f"Missing translation file: {path}")
    tree = parse(path)
    root = tree.getroot()
    return tree, root, collect(root)


def cmd_init(args: argparse.Namespace) -> int:
    path = target_path(args.code)
    if path.exists() and not args.force:
        raise SystemExit(f"{path} already exists; use --force to overwrite")
    tree = parse(SOURCE)
    ET.indent(tree, space="\t")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    print(f"Created {path.relative_to(ROOT)} from {SOURCE.name}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    en_root = parse(SOURCE).getroot()
    en = collect(en_root)
    _, _, target = load(args.code)

    missing = sorted(set(en) - set(target))
    extra = sorted(set(target) - set(en))

    translated = 0
    unchanged = 0
    for key, element in target.items():
        source_element = en.get(key)
        if source_element is None:
            continue
        if (element.text or "") != (source_element.text or ""):
            translated += 1
        else:
            unchanged += 1

    total = len(en)
    percent = (translated / total * 100.0) if total else 0.0
    print(f"{args.code}: {translated}/{total} translated ({percent:.1f}%), {unchanged} untranslated")
    if missing:
        print(f"  missing keys: {len(missing)}")
    if extra:
        print(f"  extra keys:   {len(extra)}")

    def section(prefix: str) -> tuple[int, int]:
        count = 0
        done = 0
        for key, element in target.items():
            if key[0] != prefix or key not in en:
                continue
            count += 1
            if (element.text or "") != (en[key].text or ""):
                done += 1
        return done, count

    for prefix in ("control", "enum", "message"):
        done, count = section(prefix)
        print(f"  {prefix:7s}: {done}/{count}")

    return 0


def cmd_check(args: argparse.Namespace) -> int:
    en_root = parse(SOURCE).getroot()
    en = collect(en_root)
    target_tree, target_root, target = load(args.code)
    del target_tree, target_root

    errors: list[str] = []
    warnings: list[str] = []

    missing = sorted(set(en) - set(target))
    extra = sorted(set(target) - set(en))
    if missing:
        errors.append(f"{len(missing)} missing keys")
        for key in missing[:10]:
            errors.append("  missing: " + "/".join(key))
    if extra:
        errors.append(f"{len(extra)} extra keys")
        for key in extra[:10]:
            errors.append("  extra: " + "/".join(key))

    for key, element in target.items():
        source_element = en.get(key)
        if source_element is None:
            continue
        expected = placeholders(source_element.text or "")
        actual = placeholders(element.text or "")
        if expected != actual:
            errors.append(f"placeholder mismatch: {'/'.join(key)}: {expected} != {actual}")
        if not (element.text or "").strip():
            warnings.append(f"empty text: {'/'.join(key)}")

    for warning in warnings[:20]:
        print("WARN " + warning)
    if len(warnings) > 20:
        print(f"WARN ... {len(warnings) - 20} more")

    for error in errors:
        print("ERROR " + error)

    if errors:
        return 1
    print(f"{args.code}: OK ({len(target)} keys)")
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    tree, root, target = load(args.code)
    en = collect(parse(SOURCE).getroot())

    added = 0
    for key, source_element in en.items():
        if key in target:
            continue
        if key[0] == "message":
            parent = root.find("./Messages")
            assert parent is not None
            new_element = ET.SubElement(parent, "Message", {"ID": key[1]})
        elif key[0] == "enum":
            parent = root.find(f"./Enums/Enum[@ID='{key[1]}']")
            if parent is None:
                parent = ET.SubElement(root.find("./Enums"), "Enum", {"ID": key[1]})  # type: ignore[arg-type]
            new_element = ET.SubElement(parent, "Value", {"ID": key[2]})
        else:
            parent = root.find(f"./Forms/Form[@ID='{key[1]}']")
            if parent is None:
                parent = ET.SubElement(root.find("./Forms"), "Form", {"ID": key[1]})  # type: ignore[arg-type]
            new_element = ET.SubElement(parent, "Control", {"ID": key[2]})
        new_element.text = source_element.text
        added += 1

    if added:
        ET.indent(tree, space="\t")
        tree.write(target_path(args.code), encoding="utf-8", xml_declaration=True)
    print(f"{args.code}: added {added} missing keys")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a translated file from the English source")
    init.add_argument("code", help="language code, e.g. zh-CN")
    init.add_argument("--force", action="store_true", help="overwrite an existing file")
    init.set_defaults(func=cmd_init)

    stats = sub.add_parser("stats", help="show translation progress")
    stats.add_argument("code")
    stats.set_defaults(func=cmd_stats)

    check = sub.add_parser("check", help="validate keys and placeholders")
    check.add_argument("code")
    check.set_defaults(func=cmd_check)

    merge = sub.add_parser("merge", help="add new English keys to a translation")
    merge.add_argument("code")
    merge.set_defaults(func=cmd_merge)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
