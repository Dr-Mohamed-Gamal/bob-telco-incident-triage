# Fix the deployment

**Mode:** Agent (start a **New Task**)

**Context:**

The fix should change only what the cause needs, with the values the service team measured. A small change is easy to review, safe to merge and easy to roll back.

**Prompt:**

```
Fix deploy/deployment.yaml for the root cause in reports/diagnosis.md.
```

**Expected result:**

- Memory request `192Mi` and memory limit `256Mi`, as `docs/release-notes.md` asks for version 1.5.0.
- Nothing else in the file changes.

**Show the client:** the change in the Source Control panel. Only the two memory lines changed, and the values match `docs/release-notes.md`.

---
