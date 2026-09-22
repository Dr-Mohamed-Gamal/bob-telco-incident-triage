# What is going on?

**Mode:** Ask (start a **New Task**)

**Context:**

In the first minutes of an incident, the team needs the facts before anyone guesses: what is broken, how badly, and since when. Ask mode only reads files, so nothing can change while you look.

**Prompt:**

```
What is going on with balance-service?
Summarise what the evidence shows: which pods are affected, their status, how many restarts, and since when.
```

**Expected result:**

- Two pods, `balance-service-7d9f8c6b5d-x2k4p` and `balance-service-7d9f8c6b5d-q8m3z`, both `CrashLoopBackOff`, with 14 and 13 restarts.
- Both are from the new version 1.5.0 rollout. The first pod started at `08:56:31` on 22 Sep 2026, and the old replica set was scaled down to 0.
- Each fact comes with the file and line it is from.

**Show the client:** how quickly Bob turns raw `kubectl` output, logs and metrics into a short, sourced summary.

---
