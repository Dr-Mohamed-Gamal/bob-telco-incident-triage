# Implementation Journey: [Telco Incident Triage]

This demo shows how IBM Bob helps an on-call engineer find why pods keep restarting, fix the deployment, and write the incident note and a runbook, using saved `kubectl` output and logs.

The whole demo is driven by short prompts in Bob, in plain language.

**Date added:** [09/22/2026]  
**Duration:** 15 min  
**Mode(s) Used:** *Ask* and *Agent* modes (both built in)

## Initial Goal

Acme Telco is a fictional mobile operator. One of its services is `balance-service`: the application behind the app and the website that shows mobile subscribers their remaining data, minutes and SMS.

This morning the team released **version 1.5.0** of `balance-service`, replacing version 1.4.2. According to its release notes, the new version keeps the subscriber list in memory, so balance checks no longer call the billing system every time. Since the release, the service keeps restarting (its pods, the running copies of the application, never stay up), and balance checks fail.

The on-call engineer saved the `kubectl` output and logs in the service's deployment repository. Find the root cause, prove it, fix it, and tell the application management team (the team that runs and supports the application in production). No cluster is needed, and there is nothing to install.

---

## Step-by-Step Process

Every step is a prompt in Bob. Start each prompt in a **New Task**. Two prompts are questions, asked in **Ask** mode, which can read files but not change them. The others run in **Agent** mode, the default.

### Step 1: Open the repository in Bob

Open the [input-documents](input-documents) folder in IBM Bob (File > Open Folder). The top folder in the Explorer must read **INPUT-DOCUMENTS**, so Bob loads the rule and writes its reports in the right place.

| Folder or file | Contents |
|---|---|
| `evidence/` | What the on-call engineer saved: `kubectl` output (`.txt`), the app log and the node's kernel log (`.log`), a Grafana memory export (`.csv`), and a README with the command behind each file |
| `deploy/deployment.yaml` | The Kubernetes deployment |
| `docs/release-notes.md` | What changed in version 1.5.0 |
| `catalog-info.yaml` | The owner team and the tier |

Bob also reads one rule, [.bob/rules/incident-triage.md](input-documents/.bob/rules/incident-triage.md), in every task. It holds the on-call team's method: use only the files, quote every claim, tell causes from symptoms, take values from the release notes, and leave unknown facts for a person.

### Step 2: What is going on?

**Why this step:** In the first minutes of an incident, the team needs the facts before anyone guesses: what is broken, how badly, and since when. Ask mode only reads files, so nothing can change while you look.

**Prompt** (Ask mode, New Task):

```text
What is going on with balance-service?
Summarise what the evidence shows: which pods are affected, their status, how many restarts, and since when.
```

Details and expected result: [01-overview-prompt.md](prompt-templates/01-overview-prompt.md)

**Outcome:**

Two pods from the new 1.5.0 rollout, both in `CrashLoopBackOff`, with 14 and 13 restarts. Each fact names the file and line it comes from.

**Show the client:** raw `kubectl` output, logs and metrics become a short, sourced summary in seconds.

### Step 3: Find the root cause

**Why this step:** A fix is only safe when you know the cause. The quotes let anyone check the diagnosis before acting on it, and the plain-words summary lets people outside the technical team follow it too.

**Prompt** (Agent mode, New Task):

```text
The balance-service pods keep restarting.
Find the root cause, using only the files in this repository.
Start with a short explanation in plain words, without technical terms, that anyone can follow.
Then give the technical details and the evidence.
Write it to reports/diagnosis.md and change nothing else.
```

Details and expected result: [02-diagnose-prompt.md](prompt-templates/02-diagnose-prompt.md)

**Outcome:**

The diagnosis starts in plain words: this morning's update needs more memory than the service is allowed to use, so it keeps running out and restarting. Then the technical details: version 1.5.0 loads a subscriber cache at start-up, the deployment still has a `64Mi` limit, so the container is `OOMKilled` (exit code `137`). Every claim quotes the exact line it comes from. The failing readiness probe and a slow billing warning are listed as symptoms, not causes.

**Show the client:** read the plain-words explanation first, so everyone in the room follows. Then open a file Bob quotes, such as `evidence/worker-3-kernel.log`, to show the evidence is really there.

### Step 4: Is the second pod failing for the same reason?

**Why this step:** Evidence is often incomplete. Before acting, the team needs to know what is proven, what is only likely, and what to check next.

**Prompt** (Ask mode, New Task):

```text
Is the second pod failing for the same reason?
Tell me what the evidence proves and what it does not.
```

Details and expected result: [03-second-pod-prompt.md](prompt-templates/03-second-pod-prompt.md)

**Outcome:**

The second pod is from the same replica set and keeps restarting, so the same cause is likely. But the detailed output, the logs and the metrics cover the first pod only, and the second pod runs on another node (`worker-5`). So `OOMKilled` is not proven for it. Bob names the command that would prove it.

**Show the client:** Bob does not claim more than the evidence shows.

### Step 5: Fix the deployment

**Why this step:** The fix should change only what the cause needs, with the values the service team measured. A small change is easy to review, safe to merge and easy to roll back.

**Prompt** (Agent mode, New Task):

```text
Fix deploy/deployment.yaml for the root cause in reports/diagnosis.md.
```

Details and expected result: [04-fix-prompt.md](prompt-templates/04-fix-prompt.md)

**Outcome:**

Memory request `192Mi` and limit `256Mi`, the values the release notes ask for. Nothing else in the file changes.

**Show the client:** the change in the Source Control panel. Only the two memory lines changed.

### Step 6: Write the incident note

**Why this step:** During an incident, the application management team, the next shift and managers need a short update, not logs. The note is usually pasted into the incident ticket or chat channel. Facts Bob cannot know, such as customer impact, are left for a person.

**Prompt** (Agent mode, New Task):

```text
Write a short incident note for the application management team in reports/incident-note.md.
```

Details and expected result: [05-incident-note-prompt.md](prompt-templates/05-incident-note-prompt.md)

**Outcome:**

A note with what happened, the impact, the root cause, the fix and the next steps. Times and counts come from the evidence and the owner team from `catalog-info.yaml`. The fix is described as ready to merge, not as deployed.

**Show the client:** the `<to fill>` fields, such as customer impact. Bob leaves facts it cannot find for a person to add.

### Step 7: Write a runbook for the application management team

**Why this step:** Next time, the night shift should recognise this problem in minutes, with or without Bob. The runbook keeps what was learned in this incident with the team.

**Prompt** (Agent mode, New Task):

```text
Write a short runbook for the application management team in runbooks/pod-restarts.md.
It should help them spot and fix this problem faster next time.
```

Details and expected result: [06-runbook-prompt.md](prompt-templates/06-runbook-prompt.md)

**Outcome:**

A runbook with the signs, the `kubectl` commands to check them, the likely cause, the fix, and the team to call (`charging-platform`).

**Show the client:** the know-how from one incident is written down for the next shift.

### Reset (after the meeting)

**Why this step:** Puts everything back as it was, so the demo can run again.

**Prompt** (Agent mode, New Task):

```text
Reset the demo with bash scripts/reset_demo.sh.
```

Details and expected result: [07-reset-prompt.md](prompt-templates/07-reset-prompt.md)

This puts the repository back to its starting state for the next demo.

> [!TIP]
> Before the meeting, read the talk track in [presenter/DEMO_SCRIPT.md](presenter/DEMO_SCRIPT.md) and rehearse with the checks in [presenter/](presenter). They are not part of the demo.

---

## Key Decisions

### Decision 1: Evidence you can check

**Context:**

An incident has many signals. Some are causes, most are symptoms.

**Choice Made:**

The rule asks for a quote, with `file:line`, for every claim, and a "Not the cause" list.

**Rationale:**

Anyone can open the cited line and see the evidence, so the team can trust the diagnosis before acting on it.

### Decision 2: Values from the release notes

**Context:**

Any memory limit above the real need stops the restarts, so it is easy to pick a number that "works".

**Choice Made:**

The rule says to take values from `docs/` and to change only what the cause needs.

**Rationale:**

The team that built version 1.5.0 measured its memory use. Their numbers are the right ones to deploy.

### Decision 3: A person owns what the files do not show

**Context:**

The evidence shows what happened in the cluster, but not how many customers were affected or who approved the release.

**Choice Made:**

The rule tells Bob to write `<to fill>` for customer impact, ticket numbers and names, and to describe the fix as ready to merge.

**Rationale:**

The note is honest about what is known. A person adds the business facts and decides when to deploy.

### Decision 4: One rule, built-in modes, short prompts

**Context:**

A demo is easier to follow and to repeat when it has few moving parts.

**Choice Made:**

Bob's built-in Ask and Agent modes, one rule file, and six short prompts. The reset uses a fixed script, so no git commands are made up on the spot.

**Rationale:**

The audience watches one tool from start to finish, and the demo can be repeated as often as needed.

---

### Challenge 1: Symptoms that look like causes

**Issue:**

The events are full of `Readiness probe failed` and `BackOff`, and the logs show a slow billing API. Each looks like a reason for the failure.

**Solution:**

The rule explains how to tell a cause from a symptom: look at why the container stopped (`Last State`, `Exit Code`, the last log lines).

**Learning:**

Write the team's troubleshooting know-how down where Bob reads it, so every engineer, and Bob, follows the same method.

### Challenge 2: A fix is not a deployment

**Issue:**

There is no cluster in the demo, so the fix cannot be tested live.

**Solution:**

The rule says to describe the fix as ready to merge, not as deployed. In a GitOps setup, merging the change is what deploys it.

**Learning:**

Say what was checked, and what still needs a person.

---

## Final Outcome

**What was achieved:**
- A sourced summary of the incident in seconds
- A root cause proven with quotes from the evidence, with the symptoms ruled out
- A one-line fix with values from the release notes
- A clear line between what the evidence proves and what is only likely
- An incident note for the application management team, with `<to fill>` where a person must add facts
- A runbook, so the next shift can fix the same problem faster

The output of a real run, with review notes, is in [optional-generated-content](optional-generated-content).
