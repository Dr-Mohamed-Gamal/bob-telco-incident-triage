# Write a runbook for the NOC

**Mode:** Agent (start a **New Task**)

**Context:**

Next time, the night shift should recognise this problem in minutes, with or without Bob. The runbook keeps what was learned in this incident with the team.

**Prompt:**

```
Write a short runbook for the NOC in runbooks/pod-restarts.md.
It should help them spot and fix this problem faster next time.
```

**Expected result:**

- Sections: Signs, Check, Likely cause, Fix, Escalate to.
- The Check section uses the commands from `evidence/README.md`, such as `kubectl describe pod <pod> -n charging` and `journalctl -k` on the node.
- It explains how `OOMKilled` and exit code `137` point to a memory limit, and that the release notes give the right values.
- Escalate to `charging-platform`, the owner team in `catalog-info.yaml`.

**Show the client:** the team's know-how is now written down, from one incident, in a few seconds.

---
