# Write the incident note

**Mode:** Agent (start a **New Task**)

**Context:**

During an incident, the application management team, the next shift and managers need a short update, not logs. The note is usually pasted into the incident ticket or chat channel. Facts Bob cannot know, such as customer impact, are left for a person.

**Prompt:**

```
Write a short incident note for the application management team in reports/incident-note.md.
```

**Expected result:**

- Times, restart counts and versions as they appear in the evidence.
- Owner team `charging-platform`, from `catalog-info.yaml`.
- Customer impact left as `<to fill>`, because the evidence has no customer numbers.
- The fix is described as ready to merge, not as deployed.

**Show the client:** the `<to fill>` fields. Bob leaves facts it cannot find for a person to add.

---
