#!/usr/bin/env python3
"""Check that a report only quotes what the files really say.

For the presenter. Run from a terminal:

    python3 presenter/check_quotes.py reports/diagnosis.md

For every table row that starts with `path:line` (or a range such as `path:24-25`), the
file and the lines must exist, and every text in backticks in the next column must be on
those lines. An ellipsis (... or \u2026) inside a quote stands for text left out.
Numbers that appear in none of the source files are reported as warnings.
Exit code: 0 = PASS, 1 = FAIL, 2 = cannot run. Standard library only.
"""

import re
import sys
from pathlib import Path

SOURCES = ("evidence", "docs", "deploy", "catalog-info.yaml")
ROW = re.compile(r"^\|\s*`?([\w./-]+):(\d+)(?:\s*[\u2013-]\s*(\d+))?`?\s*\|([^|]*)\|")
NUMBER = re.compile(r"(?<![\w.:-])(\d+(?:\.\d+)?)(?:ms|m|Mi|Gi|Ki|kB|MB|s)?(?![\w.])")
LINE_REF = re.compile(r"\blines?\s+\d+(?:\s*[\u2013-]\s*\d+)?|:\d+(?:\s*[\u2013-]\s*\d+)?")
LIST_MARKER = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")  # "- ", "* ", "1. " at the start of a line
THOUSANDS = re.compile(r"(?<=\d)[ ,\u202f\u00a0](?=\d{3}\b)")


def normalise(text):
    return re.sub(r"\s+", " ", text).strip()


def quote_found(quote, text):
    """True if the quote is in the text. An ellipsis stands for any text left out."""
    parts = [normalise(p) for p in re.split(r"\u2026|\.\.\.", quote) if normalise(p)]
    pattern = ".*?".join(re.escape(p) for p in parts)
    return bool(parts) and re.search(pattern, normalise(text)) is not None


def source_numbers(root):
    text = []
    for name in SOURCES:
        path = root / name
        files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
        for f in files:
            text.append(f.read_text(encoding="utf-8"))
    return set(re.findall(r"\d+(?:\.\d+)?", "\n".join(text)))


def check(root, report):
    problems, warnings, quotes = [], [], 0
    lines = report.read_text(encoding="utf-8").splitlines()
    known = source_numbers(root)
    for number, line in enumerate(lines, 1):
        m = ROW.match(line.strip())
        if m:
            quotes += 1
            path, first = m.group(1), int(m.group(2))
            last = int(m.group(3)) if m.group(3) else first
            target = root / path
            if not target.is_file():
                problems.append("line %d: %s does not exist" % (number, path))
                continue
            file_lines = target.read_text(encoding="utf-8").splitlines()
            if not 1 <= first <= last <= len(file_lines):
                problems.append("line %d: %s has %d lines, not %s" % (number, path, len(file_lines), m.group(0).split("|")[1].strip()))
                continue
            cited = " ".join(file_lines[first - 1:last])
            bare = " ".join(LIST_MARKER.sub("", l) for l in file_lines[first - 1:last])
            texts = re.findall(r"`([^`]+)`", m.group(4))
            if not texts:
                problems.append("line %d: no quote in backticks for %s" % (number, path))
            for quote in texts:
                if not (quote_found(quote, cited) or quote_found(quote, bare)):
                    where = "%s:%d" % (path, first) if first == last else "%s:%d-%d" % (path, first, last)
                    problems.append("line %d: `%s` is not on %s, which says `%s`" % (number, quote, where, normalise(cited)[:160]))
            continue
        if line.startswith("#"):
            continue
        line = THOUSANDS.sub("", LINE_REF.sub(" ", line))
        for n in NUMBER.findall(line):
            if n not in known:
                warnings.append("line %d: the number %s is in none of the source files" % (number, n))
    return problems, warnings, quotes


def main():
    if len(sys.argv) != 2:
        print("Usage: check_quotes.py <report.md>")
        sys.exit(2)
    root = Path(__file__).resolve().parents[1] / "input-documents"
    report = root / sys.argv[1]
    if not report.is_file():
        print("QUOTE CHECK: FAIL (%s not found)" % report)
        sys.exit(1)
    problems, warnings, quotes = check(root, report)
    if quotes == 0:
        problems.append("no quotes found (rows must start with | file:line | `exact text` |)")
    for p in problems:
        print("FAIL  " + p)
    for w in warnings:
        print("WARN  " + w)
    if problems:
        print("QUOTE CHECK: FAIL (%d problems, %d warnings)" % (len(problems), len(warnings)))
        sys.exit(1)
    print("QUOTE CHECK: PASS (%d quotes checked, %d warnings)" % (quotes, len(warnings)))


if __name__ == "__main__":
    main()
