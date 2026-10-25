#!/usr/bin/env python3
"""Read-only mechanical application checks. No network, writes, ATS score or factual verdict."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile


class InputError(ValueError):
    pass


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    text = text.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                                         "–": "-", "—": "-", "‑": "-", "−": "-"}))
    return " ".join(text.split())


def find_anchor(text: str, anchor: str, start: int = 0):
    # Keep technical punctuation meaningful: SQL != NoSQL, C != C++, C# != C++.
    pattern = r"(?<![\w+.#])" + re.escape(normalize(anchor)) + r"(?!(?:[\w+#]|\.\w))"
    return re.search(pattern, text[start:])


def string_list(value, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise InputError(f"{label} must be an array of nonempty strings")
    return value


def limit(value, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InputError(f"{label} must be a positive integer")
    return value


def validate(config: dict) -> None:
    if not isinstance(config, dict) or set(config) - {"files", "answers"}:
        raise InputError("Input must be an object containing files and/or answers")
    if not any(config.get(k) for k in ("files", "answers")):
        raise InputError("At least one file or answer is required")
    for group in ("files", "answers"):
        items = config.get(group, [])
        if not isinstance(items, list):
            raise InputError(f"{group} must be an array")
        for item in items:
            if not isinstance(item, dict):
                raise InputError(f"Each {group} item must be an object")
            allowed = ({"label", "path", "required_text", "forbidden_text", "expected_order",
                        "max_pages", "max_bytes", "expected_sha256"} if group == "files"
                       else {"label", "text", "max_characters", "max_words"})
            if set(item) - allowed:
                raise InputError(f"Unknown {group} fields: {', '.join(sorted(set(item) - allowed))}")
            if "label" in item and (not isinstance(item["label"], str) or not item["label"].strip()):
                raise InputError("label must be nonempty text")
            if group == "files":
                path = item.get("path")
                if not isinstance(path, str) or not Path(path).is_absolute():
                    raise InputError("Every file path must be absolute")
                for field in ("required_text", "forbidden_text", "expected_order"):
                    string_list(item.get(field, []), field)
                if "expected_sha256" in item and not re.fullmatch(r"[0-9a-fA-F]{64}", str(item["expected_sha256"])):
                    raise InputError("expected_sha256 must be a 64-character SHA-256 digest")
                fields = ("max_pages", "max_bytes")
            else:
                if not isinstance(item.get("text"), str):
                    raise InputError("Each answer needs text")
                fields = ("max_characters", "max_words")
            for field in fields:
                if field in item:
                    limit(item[field], field)


def extract_docx(path: Path) -> tuple[str, None, str]:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if "word/document.xml" not in names:
            raise ValueError("DOCX has no document.xml")
        parts = ["word/document.xml"] + sorted(n for n in names if re.fullmatch(r"word/(?:header|footer)\d+\.xml", n))
        for part in parts:
            root = ET.fromstring(archive.read(part))
            for paragraph in root.findall(".//w:p", ns):
                # Word runs may split a name/email across several w:t elements.
                chunks = []
                for node in paragraph.iter():
                    if node.tag == "{" + ns["w"] + "}t":
                        chunks.append(node.text or "")
                    elif node.tag in {"{" + ns["w"] + "}tab", "{" + ns["w"] + "}br"}:
                        chunks.append(" ")
                paragraphs.append("".join(chunks))
    return "\n".join(paragraphs), None, "docx_xml"


def extract_pdf(path: Path) -> tuple[str | None, int | None, str]:
    if importlib.util.find_spec("pypdf") is not None:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise ValueError("PDF is encrypted; automatic decryption is not attempted")
        return "\n".join(page.extract_text() or "" for page in reader.pages), len(reader.pages), "pypdf"
    converter = shutil.which("pdftotext")
    if converter is None:
        return None, None, "unavailable"
    result = subprocess.run([converter, "-enc", "UTF-8", "-layout", str(path), "-"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    if result.returncode:
        raise ValueError("pdftotext could not extract this PDF")
    pages = None
    info = shutil.which("pdfinfo")
    if info:
        metadata = subprocess.run([info, str(path)], capture_output=True, text=True, timeout=30)
        match = re.search(r"^Pages:\s+(\d+)", metadata.stdout, re.MULTILINE)
        if metadata.returncode == 0 and match:
            pages = int(match.group(1))
    return result.stdout, pages, "pdftotext"


PLACEHOLDER = re.compile(
    r"\[(?:your (?:name|email|phone)|company(?: name)?|job title|insert[^\]\n]{0,80}|"
    r"todo|tbd|metric|date|recipient(?: name)?)\]|\{\{\s*[A-Za-z][A-Za-z0-9_ -]{0,60}\s*\}\}",
    re.IGNORECASE,
)


def check_text(text: str, item: dict) -> tuple[list[dict], list[str]]:
    findings = []
    checked = ["extractable_text", "template_placeholders", "replacement_characters"]
    if not text.strip():
        findings.append({"code": "empty_text", "severity": "error"})
    if PLACEHOLDER.search(text):
        findings.append({"code": "template_placeholder", "severity": "error"})
    if "\ufffd" in text or "\x00" in text:
        findings.append({"code": "damaged_text_characters", "severity": "error"})
    normalized = normalize(text)
    for field, missing in (("required_text", True), ("forbidden_text", False)):
        if item.get(field):
            checked.append(field)
        for anchor in item.get(field, []):
            found = find_anchor(normalized, anchor) is not None
            if (missing and not found) or (not missing and found):
                findings.append({"code": "missing_required_text" if missing else "forbidden_text_present",
                                 "severity": "error", "anchor": anchor})
    if item.get("expected_order"):
        checked.append("expected_text_order")
        cursor = 0
        for anchor in item["expected_order"]:
            match = find_anchor(normalized, anchor, cursor)
            if match is None:
                findings.append({"code": "expected_order_not_found", "severity": "error", "anchor": anchor})
                break
            cursor += match.end()
    return findings, checked


def check_file(item: dict) -> dict:
    path = Path(item["path"])
    report = {"label": item.get("label", path.name), "path": str(path), "checked": [],
              "not_checked": [], "findings": []}
    try:
        data = path.read_bytes()
        report["bytes"] = len(data)
        report["sha256"] = hashlib.sha256(data).hexdigest()
        report["checked"] += ["file_readable", "file_hash"]
        if not data:
            report["findings"].append({"code": "empty_file", "severity": "error"})
        if "max_bytes" in item:
            report["checked"].append("file_size_limit")
            if len(data) > item["max_bytes"]:
                report["findings"].append({"code": "file_too_large", "severity": "error", "limit": item["max_bytes"]})
        if "expected_sha256" in item:
            report["checked"].append("expected_file_hash")
            if report["sha256"] != item["expected_sha256"].lower():
                report["findings"].append({"code": "file_hash_changed", "severity": "error"})
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            if not data.startswith(b"%PDF-"):
                raise ValueError("File extension says PDF but its signature does not")
            text, pages, engine = extract_pdf(path)
        elif suffix == ".docx":
            text, pages, engine = extract_docx(path)
        elif suffix in {".txt", ".md"}:
            text, pages, engine = data.decode("utf-8-sig"), None, "utf8"
        else:
            text, pages, engine = None, None, "unsupported_format"
        report["extractor"] = engine
        if text is None:
            report["not_checked"].append("text checks: no supported available extractor")
        else:
            findings, checked = check_text(text, item)
            report["findings"] += findings
            report["checked"] += checked
            report["characters"] = len(text)
        if pages is not None:
            report["page_count"] = pages
        if "max_pages" in item:
            if pages is None:
                report["not_checked"].append("page limit: rendered page count unavailable")
            else:
                report["checked"].append("page_limit")
                if pages > item["max_pages"]:
                    report["findings"].append({"code": "over_page_limit", "severity": "error", "limit": item["max_pages"]})
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, ET.ParseError, subprocess.SubprocessError) as exc:
        report["findings"].append({"code": "file_check_failed", "severity": "error", "reason": str(exc)})
    except Exception as exc:
        # Optional PDF libraries use their own parse exception types.
        report["findings"].append({"code": "extraction_failed", "severity": "error", "reason": type(exc).__name__})
    return report


def audit(config: dict) -> tuple[dict, int]:
    validate(config)
    files = [check_file(item) for item in config.get("files", [])]
    answers = []
    for index, item in enumerate(config.get("answers", []), 1):
        findings, checked = check_text(item["text"], {})
        characters, words = len(item["text"]), len(item["text"].split())
        for key, count in (("max_characters", characters), ("max_words", words)):
            if key in item:
                checked.append(key)
                if count > item[key]:
                    findings.append({"code": key + "_exceeded", "severity": "error", "limit": item[key]})
        answers.append({"label": item.get("label", f"Answer {index}"), "characters": characters,
                        "words": words, "checked": checked, "findings": findings})
    errors = sum(len(item["findings"]) for item in files + answers)
    incomplete = any(item["not_checked"] for item in files)
    code = 1 if errors else 2 if incomplete else 0
    return {"schema_version": 1, "scope": "mechanical_checks_only",
            "status": "issues_found" if errors else "incomplete" if incomplete else "requested_checks_passed",
            "files": files, "answers": answers,
            "not_established": ["factual grounding", "visual layout", "semantic keyword equivalence",
                                "employer ATS acceptance", "hiring likelihood", "upload or submission"]}, code


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.input.read_text(encoding="utf-8"))
        result, code = audit(config)
    except (OSError, ValueError, TypeError) as exc:
        result, code = {"status": "invalid_input", "error": str(exc)}, 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
