#!/usr/bin/env python3
"""
product-qa gate: makes the product-qa post-build pass non-optional.

  product-qa-gate.py snapshot   (UserPromptSubmit) record the repo's code state at turn start
  product-qa-gate.py check      (Stop) if code changed this turn and no QA verdict was given,
                                block the stop once and tell Claude to run the QA pass

Code change = the git working tree / HEAD changed (non-doc files), or, outside git, an
Edit/Write/MultiEdit/NotebookEdit on a code file this turn. A verdict = a line like
"**Verdict:** READY" (READY / CONDITIONAL / NOT READY / INSUFFICIENT INFORMATION).
Fails open: any error lets Claude stop normally.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

# Plugin installs get a private data dir; manual installs keep state next to the script.
STATE_DIR = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
DOC_EXT = (".md", ".mdx", ".txt", ".rst")
VERDICT = re.compile(r"Verdict:?\**:?\s*\**\s*(READY|CONDITIONAL|NOT READY|INSUFFICIENT INFORMATION)", re.I)
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def git(cwd, *args):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=20)
    return r.stdout if r.returncode == 0 else None


def fingerprint(cwd):
    """Hash of HEAD + non-doc tracked diff + untracked non-doc files (name, size, mtime)."""
    if git(cwd, "rev-parse", "--is-inside-work-tree") is None:
        return None
    exclude = [f":(exclude)*{e}" for e in DOC_EXT]
    h = hashlib.sha256()
    h.update((git(cwd, "rev-parse", "HEAD") or "").encode())
    h.update((git(cwd, "diff", "HEAD", "--", ".", *exclude) or "").encode())
    root = (git(cwd, "rev-parse", "--show-toplevel") or cwd).strip()
    for f in sorted((git(cwd, "ls-files", "--others", "--exclude-standard", "--", ".", *exclude) or "").splitlines()):
        try:
            st = os.stat(os.path.join(root, f))
            h.update(f"{f}:{st.st_size}:{st.st_mtime_ns}".encode())
        except OSError:
            pass
    return h.hexdigest()


def state_path(session_id):
    return os.path.join(STATE_DIR, f"{re.sub(r'[^A-Za-z0-9_-]', '_', session_id)}.json")


def turn_entries(transcript_path):
    """Transcript entries since the last real user prompt (not tool results)."""
    try:
        with open(transcript_path) as f:
            entries = [json.loads(l) for l in f if l.strip()]
    except (OSError, ValueError):
        return []
    start = 0
    for i, e in enumerate(entries):
        if e.get("type") != "user":
            continue
        content = (e.get("message") or {}).get("content")
        if isinstance(content, str) or (isinstance(content, list) and any(b.get("type") == "text" for b in content if isinstance(b, dict))):
            start = i
    return entries[start:]


def blocks(entries, kind):
    for e in entries:
        if e.get("type") != "assistant":
            continue
        for b in (e.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == kind:
                yield b


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    data = json.load(sys.stdin)
    session = data.get("session_id") or "unknown"
    cwd = data.get("cwd") or os.getcwd()

    if mode == "snapshot":
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(state_path(session), "w") as f:
            json.dump({"cwd": cwd, "fingerprint": fingerprint(cwd)}, f)
        return

    if mode != "check" or data.get("stop_hook_active"):
        return  # already nudged once this turn: never loop

    entries = turn_entries(data.get("transcript_path") or "")
    try:
        with open(state_path(session)) as f:
            before = json.load(f)
    except (OSError, ValueError):
        before = {}

    changed = False
    if before.get("fingerprint") and before.get("cwd") == cwd:
        changed = fingerprint(cwd) != before["fingerprint"]
    if not changed:  # outside git, or snapshot missing: fall back to this turn's edit tools
        for b in blocks(entries, "tool_use"):
            path = str((b.get("input") or {}).get("file_path") or (b.get("input") or {}).get("notebook_path") or "")
            if b.get("name") in EDIT_TOOLS and path and not path.endswith(DOC_EXT) and "/.claude/" not in path:
                changed = True
                break
    if not changed:
        return

    text = (data.get("last_assistant_message") or "") + "\n" + "\n".join(b.get("text", "") for b in blocks(entries, "text"))
    if VERDICT.search(text):
        return

    print(json.dumps({
        "decision": "block",
        "reason": (
            "product-qa gate: code changed this turn but no QA verdict was given. Before finishing, run the "
            "product-qa skill's post-build pass (Mode A): scope the change, risk-rank it, run the project's "
            "tests/type-check/lint/build, close the highest-risk gaps, then report in the post-build format "
            "ending with a line '**Verdict:** READY / CONDITIONAL / NOT READY / INSUFFICIENT INFORMATION'. "
            "Scale it to the change: for a pure styling tweak one or two lines plus the Verdict line is enough."
        ),
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail open
