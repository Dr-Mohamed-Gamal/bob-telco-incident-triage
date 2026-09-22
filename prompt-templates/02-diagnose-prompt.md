# Find the root cause

**Mode:** Agent (start a **New Task**)

**Context:**

A fix is only safe when you know the cause. The quotes let anyone check the diagnosis before acting on it, and the plain-words summary lets people outside the technical team follow it too. Bob does not change anything yet.

**Prompt:**

```
The balance-service pods keep restarting.
Find the root cause, using only the files in this repository.
Start with a short explanation in plain words, without technical terms, that anyone can follow.
Then give the technical details and the evidence.
Write it to reports/diagnosis.md and change nothing else.
```

**Expected result:**

- In plain words, first: this morning's update needs more memory than the service is allowed to use, so it keeps running out, being stopped and starting again. Giving it the memory the release notes ask for fixes it.
- Root cause, with the technical details: version 1.5.0 needs more memory, but `deploy/deployment.yaml` still has a `64Mi` memory limit. The container is `OOMKilled` (exit code `137`) and restarts.
- Evidence rows quote the exact lines, for example `Reason:       OOMKilled` in `evidence/kubectl-describe-pod-x2k4p.txt`, `memory: usage 65536kB, limit 65536kB` in `evidence/worker-3-kernel.log`, and the memory climbing towards the limit in `evidence/grafana-memory-x2k4p.csv`.
- "Not the cause" lists the failing readiness probe and the slow billing warning. They are symptoms.

**Show the client:** read the plain-words explanation aloud first. Then open `evidence/worker-3-kernel.log` at the line Bob cites, to show the quote is really there.

---
