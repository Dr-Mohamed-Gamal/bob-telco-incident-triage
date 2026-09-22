# Incident triage rules

These rules apply in every mode. They describe how the on-call team finds why a Kubernetes service is failing, from saved `kubectl` output and logs.

## Facts only

1. Use only the files in `evidence/`, `docs/`, `deploy/` and `catalog-info.yaml`. There is no live cluster.
2. Every claim needs a quote: `file:line` and the exact text of that line. If something is not in the files, write "Not in the evidence". Do not guess.
3. Never say a command worked unless you show what it printed.
4. Never edit `.bob/`, `evidence/`, `docs/`, `scripts/` or `catalog-info.yaml`.
5. Stop when the task is done. Do not start the next step until the user asks.
6. Do not commit, push or create branches.
7. When you answer a question, say what the evidence proves and what is only likely. For anything not proven, name the file or the command that would prove it.

## Cause or symptom?

These are usually **symptoms**, not causes:

- `CrashLoopBackOff` and `BackOff`: Kubernetes waits before restarting a container that keeps stopping.
- `Readiness probe failed ... connection refused`: nothing is listening yet, often because the container is starting or was just killed.
- Warnings in the logs from before the container stopped.

To find the **cause**, look at why the container stopped: `Last State`, `Reason`, `Exit Code` and the last log lines. `OOMKilled` with exit code `137` means the container used more memory than its limit.

List the signals that are not the cause, with a quote and one sentence on why.

## Fixing

- Change only what the cause needs. Keep the YAML style of the file.
- Take values from `docs/` (for example the release notes). Never pick a value from memory.
- There is no cluster here. Say that the fix is ready to merge, not that it is deployed or that the incident is resolved.

## Runbook template (`runbooks/<name>.md`)

```markdown
# Runbook: <service> <problem>

## Signs
## Check
## Likely cause
## Fix
## Escalate to
```

- Under Check, use only the commands listed in `evidence/README.md`. You may replace a pod or node name with `<pod>` or `<node>`.
- Escalate to the owner team from `catalog-info.yaml`.
- Keep it short enough to follow during a night shift.

## Reset

To reset the demo, run `bash scripts/reset_demo.sh`. Never use other git commands to reset.

## Diagnosis template (`reports/diagnosis.md`)

```markdown
# Diagnosis: <service> <what is failing>

**In plain words:** <two or three short sentences>

**Root cause:** <one or two sentences, with the technical details>

## Evidence

| File:line | Exact text | What it shows |
|---|---|---|
| evidence/kubectl-describe-pod-x2k4p.txt:17 | `Reason:       OOMKilled` | <one sentence> |

## Not the cause

| File:line | Exact text | Why it is not the cause |
|---|---|---|

## Fix

<what to change, and the file:line the values come from>
```

- **In plain words** uses everyday language that anyone in the company can follow. No technical terms such as pod, container, Kubernetes, `OOMKilled`, exit code or MiB. Say what went wrong, why, and what fixes it.
- In the tables, copy the exact text of the line inside backticks. You may leave out spaces at the start of the line, shorten a long line with `…`, or cite a range of lines such as `file:24–25`.

## Incident note template (`reports/incident-note.md`)

```markdown
# Incident note: <service>, <date from the evidence>

## What happened
## Impact
## Root cause
## Fix
## Next steps
```

- Take times, counts and versions from the evidence, as written there. Do not work out durations or percentages.
- The owner team comes from `catalog-info.yaml`.
- The evidence has no customer numbers. Under Impact, describe what the evidence shows and write `<to fill>` for customer impact. Also write `<to fill>` for ticket numbers and names.
