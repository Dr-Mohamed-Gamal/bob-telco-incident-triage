#!/usr/bin/env python3
"""For the presenter, to rehearse before the meeting. Not shown to the client.

Checks Bob's work after each prompt with fixed rules. Run from a terminal, with the
number of the prompt you just ran:

    python3 presenter/verify_step.py 1    after "What is going on?" (Ask mode)
    python3 presenter/verify_step.py 2    after the diagnosis
    python3 presenter/verify_step.py 3    after "Is the second pod failing...?" (Ask mode)
    python3 presenter/verify_step.py 4    after the fix
    python3 presenter/verify_step.py 5    after the incident note
    python3 presenter/verify_step.py 6    after the runbook

Compares with the main branch (or HEAD if main does not have this demo).
Exit code: 0 = PASS, 1 = FAIL, 2 = cannot run. Standard library only.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import check_quotes  # noqa: E402

PROTECTED = (".bob/", "evidence/", "docs/", "scripts/", "catalog-info.yaml")
EXPECTED_MEMORY = {"requests": "192Mi", "limits": "256Mi"}  # docs/release-notes.md, version 1.5.0
FILES_BY_PROMPT = {  # the file each prompt may add or change (Ask-mode prompts change nothing)
    2: "reports/diagnosis.md",
    4: "deploy/deployment.yaml",
    5: "reports/incident-note.md",
    6: "runbooks/pod-restarts.md",
}
NOTE_SECTIONS = ("what happened", "impact", "root cause", "fix", "next steps")
RUNBOOK_SECTIONS = ("signs", "check", "likely cause", "fix", "escalate")
JARGON = ("pod", "pods", "container", "kubernetes", "k8s", "oomkilled", "crashloopbackoff", "exit code",
          "137", "cgroup", "mib", "64mi", "192mi", "256mi", "yaml", "replica", "kubectl", "probe")
failed = False


def result(ok, message):
    global failed
    failed |= not ok
    print("  %s  %s" % ("PASS" if ok else "FAIL", message))


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


def changed_files(base):
    tracked = git("diff", "--name-only", "--relative", base, "--", ".").split()
    untracked = git("ls-files", "--others", "--exclude-standard", "--", ".").split()
    return set(tracked) | set(untracked)


MEMORY_UNITS = {"": 1, "k": 10**3, "M": 10**6, "G": 10**9, "Ki": 2**10, "Mi": 2**20, "Gi": 2**30}


def memory_bytes(value):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(k|M|G|Ki|Mi|Gi)?", value or "")
    return float(m.group(1)) * MEMORY_UNITS[m.group(2) or ""] if m else None


def resource_values(text):
    """Read resources.requests/limits from block-style YAML: {("limits", "memory"): "256Mi", ...}."""
    stack, values = [], {}
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        content = raw.strip()
        if content.startswith("- "):
            indent, content = indent + 2, content[2:]
        m = re.match(r"([\w./-]+):\s*(.*)$", content)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip().strip("\"'")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = [k for _, k in stack] + [key]
        if len(path) >= 3 and path[-3] == "resources" and path[-2] in ("requests", "limits"):
            values[(path[-2], key)] = value
        if value == "":
            stack.append((indent, key))
    return values


def section(lines, title):
    """Lines under a '## title' heading, up to the next heading."""
    out, inside = [], False
    for line in lines:
        if line.startswith("#"):
            inside = line.lstrip("#").strip().lower().startswith(title)
            continue
        if inside:
            out.append(line)
    return out


def check_fix(base):
    values = resource_values(Path("deploy/deployment.yaml").read_text(encoding="utf-8"))
    for kind, expected in EXPECTED_MEMORY.items():
        actual = values.get((kind, "memory"))
        ok = memory_bytes(actual) == memory_bytes(expected)
        result(ok, "memory %s is %s (release notes: %s)" % (kind, actual, expected))
    diff = git("diff", "-U0", base, "--", "deploy/deployment.yaml").splitlines()
    edits = [l[1:] for l in diff if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    others = [e.strip() for e in edits if not re.match(r"^\s*memory:\s*\S+\s*$", e)]
    result(not others, "only memory lines changed in deploy/deployment.yaml"
           + ("" if not others else ": also changed %s" % others))


def kubectl_commands(text):
    """The first two words after `kubectl` in each command, e.g. 'describe pod'."""
    return {" ".join(m.split()[:2]) for m in re.findall(r"kubectl\s+([a-z-]+\s+[a-z-]+)", text)}


def check_diagnosis():
    report = Path("reports/diagnosis.md")
    if not report.is_file():
        result(False, "reports/diagnosis.md exists")
        return
    problems, warnings, quotes = check_quotes.check(Path("."), report)
    result(not problems and quotes > 0, "%d quotes checked against the files" % quotes)
    for p in problems:
        print("        " + p)
    for w in warnings:
        print("  WARN  " + w)
    text = report.read_text(encoding="utf-8")
    plain = next((l for l in text.splitlines() if l.lower().startswith("**in plain words")), "")
    jargon = sorted({w for w in JARGON if re.search(r"\b%s\b" % re.escape(w), plain, re.I)})
    result(bool(plain), "starts with an explanation in plain words")
    result(plain and not jargon, "the plain-words explanation has no technical terms"
           + ("" if not jargon else ": %s" % jargon))
    cause = next((l for l in text.splitlines() if l.lower().startswith("**root cause")), "")
    result(bool(re.search(r"oomkilled|memory", cause, re.I)), "root cause names the memory limit (OOMKilled)")
    result(bool(re.search(r"\|\s*`[^`]*OOMKilled[^`]*`", text)), "the OOMKilled line is quoted as evidence")
    not_cause = " ".join(section(text.splitlines(), "not the cause"))
    result(bool(re.search(r"readiness|billing", not_cause, re.I)),
           "symptoms (readiness probe, slow billing) are listed as not the cause")


def check_note():
    note = Path("reports/incident-note.md")
    if not note.is_file():
        result(False, "reports/incident-note.md exists")
        return
    lines = note.read_text(encoding="utf-8").splitlines()
    titles = [l.lstrip("#").strip().lower() for l in lines if l.startswith("## ")]
    missing = [s for s in NOTE_SECTIONS if not any(t.startswith(s) for t in titles)]
    result(not missing, "all note sections present" + ("" if not missing else ": missing %s" % missing))
    result("charging-platform" in "\n".join(lines), "owner team from catalog-info.yaml (charging-platform)")
    result("<to fill>" in "\n".join(section(lines, "impact")), "customer impact left as <to fill>")
    problems, warnings, _ = check_quotes.check(Path("."), note)
    result(not problems, "every quote in the note is on the cited line")
    for p in problems:
        print("        " + p)
    for w in warnings:
        print("  WARN  " + w)


def check_runbook():
    runbook = Path("runbooks/pod-restarts.md")
    if not runbook.is_file():
        result(False, "runbooks/pod-restarts.md exists")
        return
    text = runbook.read_text(encoding="utf-8")
    lines = text.splitlines()
    titles = [l.lstrip("#").strip().lower() for l in lines if l.startswith("## ")]
    missing = [s for s in RUNBOOK_SECTIONS if not any(t.startswith(s) for t in titles)]
    result(not missing, "all runbook sections present" + ("" if not missing else ": missing %s" % missing))
    result("OOMKilled" in text, "explains the OOMKilled sign")
    result("charging-platform" in "\n".join(section(lines, "escalate")), "escalates to charging-platform")
    evidence = "\n".join(p.read_text(encoding="utf-8") for p in sorted(p for p in Path("evidence").iterdir() if p.is_file()))
    extra = sorted(kubectl_commands(text) - kubectl_commands(evidence))
    result(not extra, "only kubectl commands from the evidence" + ("" if not extra else ": also kubectl %s" % extra))
    problems, warnings, _ = check_quotes.check(Path("."), runbook)
    result(not problems, "every quote in the runbook is on the cited line")
    for p in problems:
        print("        " + p)
    for w in warnings:
        print("  WARN  " + w)


def main():
    step = sys.argv[1] if len(sys.argv) == 2 else ""
    if step not in ("1", "2", "3", "4", "5", "6"):
        print("Usage: verify_step.py <prompt number 1-6>")
        sys.exit(2)
    step = int(step)
    os.chdir(HERE.parents[1] / "input-documents")
    if subprocess.run(["git", "ls-files", "--error-unmatch", "catalog-info.yaml"], capture_output=True).returncode:
        print("These checks need a git clone of the demo repository (not a ZIP download).")
        sys.exit(2)
    base = "main" if subprocess.run(["git", "cat-file", "-e", "main:./catalog-info.yaml"],
                                    capture_output=True).returncode == 0 else "HEAD"
    changed = changed_files(base)
    allowed = {f for n, f in FILES_BY_PROMPT.items() if n <= step}

    print("== Guardrails (compared with %s)" % base)
    touched = sorted(f for f in changed if f.startswith(PROTECTED))
    result(not touched, "evidence, docs, rules, scripts and catalog unchanged" + ("" if not touched else ": %s" % touched))
    extra = sorted(changed - allowed)
    result(not extra, "only the files for the prompts so far changed" + ("" if not extra else ": also %s" % extra))

    print("== Prompt %d" % step)
    if step in (1, 3):
        print("  ----  Ask mode: no files change. Read the answer: every fact should name its file and line.")
    if step >= 2:
        check_diagnosis()
    if step >= 4:
        check_fix(base)
    if step >= 5:
        check_note()
    if step >= 6:
        check_runbook()

    print()
    print("VERIFY PROMPT %d: %s" % (step, "FAIL" if failed else "PASS"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
