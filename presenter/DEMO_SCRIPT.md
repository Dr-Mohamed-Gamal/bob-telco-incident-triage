# Telco Incident Triage: demo script

For the presenter only. About 15 minutes. Lines in *italics* are what you say.

---

## Before the meeting

1. Open the folder `input-documents` in IBM Bob (File > Open Folder). The top folder in the Explorer must read **INPUT-DOCUMENTS**. If it shows the repository name instead, Bob will not load the rule.
2. Make sure the demo is clean: the Source Control panel shows no changes. If it does, run the reset prompt: `Reset the demo with bash scripts/reset_demo.sh.`
3. Bob is in **Agent** mode (the default). Know where the mode switch is: you need **Ask** for prompts 1 and 3.
4. Expand the `evidence` folder in the Explorer, so the client sees the files.
5. Make the font bigger (Cmd +) and close other tabs.
6. The day before, run all six prompts once and check each one from a terminal with `python3 presenter/verify_step.py <1-6>`. Then reset.
7. Keep screenshots or a recording as a backup, in case the network is slow.

---

## Opening (1 min)

*"Let me show you something every operations team knows. Acme Telco has a service called balance-service. It is what customers use to check their remaining data, minutes and SMS."*

*"It is 9:44 in the morning. An hour ago the team released version 1.5.0 of this service. The new version keeps the subscriber list in memory, to answer faster. Since the release, the service keeps restarting, and customers cannot check their balance."*

*"Acme Telco is a made-up operator, but the problem is real. The on-call engineer saved the evidence in this folder: the kubectl output, the application log, the node's kernel log, and a memory graph from Grafana."*

Point at the `evidence` folder.

*"There is no live cluster here, so nothing we do touches production. Bob works only from these files, the way an engineer would during an incident."*

*"The team's method is written in one rule file. Bob reads it in every task: use only the evidence, quote every claim, and tell causes from symptoms."*

Optional: open `.bob/rules/incident-triage.md` for five seconds.

---

## Prompt 1: What is going on? (2 min)

**Switch to Ask mode.** New Task.

*"First, I just want the picture. I use Ask mode: Bob can read the files, but cannot change anything."*

Type:

```
What is going on with balance-service?
Summarise what the evidence shows: which pods are affected, their status, how many restarts, and since when.
```

While Bob works:

*"Bob is reading the pod list, the describe output and the events. This is the first five minutes of any incident, done in seconds."*

After:

*"Two pods, both in CrashLoopBackOff, 14 and 13 restarts. Both are from the new version, 1.5.0. The old version was scaled down to zero, so nothing is serving traffic. And every fact has its file and line."*

---

## Prompt 2: Find the root cause (3 min)

**Switch back to Agent mode.** New Task.

*"Now the real question: why?"*

Type:

```
The balance-service pods keep restarting.
Find the root cause, using only the files in this repository.
Start with a short explanation in plain words, without technical terms, that anyone can follow.
Then give the technical details and the evidence.
Write it to reports/diagnosis.md and change nothing else.
```

While Bob works:

*"Look at the events: 'Readiness probe failed' again and again. And in the log there is a warning about a slow billing API. Many people would stop there. Let's see what Bob does."*

When `reports/diagnosis.md` opens, read the **In plain words** line aloud first:

*"Here is the answer in one sentence that anyone in the room can follow."* Read Bob's plain-words explanation.

Then the technical version:

*"Root cause: out of memory. Version 1.5.0 loads a subscriber cache at start-up and needs more memory. But the deployment still has a 64 MiB limit. Linux kills the container, exit code 137, and Kubernetes restarts it."*

*"Now the important part. Every line here is a quote from the evidence, with the file and the line number."*

**Show:** open `evidence/worker-3-kernel.log` and point at `memory: usage 65536kB, limit 65536kB`.

*"65536 kilobytes is exactly 64 MiB. Usage equals the limit. The proof is right there, anyone can check it in seconds."*

Then scroll to "Not the cause" in the diagnosis:

*"And Bob explains why the readiness probe and the slow billing warning are symptoms, not the cause. That is what separates a good engineer from a fast guess."*

---

## Prompt 3: Is the second pod the same? (2 min)

**Switch to Ask mode.** New Task.

*"We looked at one pod in detail. What about the second one?"*

Type:

```
Is the second pod failing for the same reason?
Tell me what the evidence proves and what it does not.
```

After:

*"This is my favourite part. Bob says: very likely the same cause. Same replica set, same image, same limits. But not proven. The detailed evidence is for the first pod only, and the second pod runs on another node, worker-5."*

*"And it tells us exactly which command would prove it. It does not claim more than the evidence shows. That is what you want from anyone on your team during an incident."*

---

## Prompt 4: Fix the deployment (2 min)

**Switch back to Agent mode.** New Task.

Type:

```
Fix deploy/deployment.yaml for the root cause in reports/diagnosis.md.
```

While Bob works:

*"Any bigger number would stop the restarts. 512, a gigabyte, anything. But the right number is not a guess."*

After:

**Show:** the Source Control panel, then the diff of `deploy/deployment.yaml`.

*"Two lines changed. Nothing else. Request 192, limit 256. Where do these numbers come from?"*

**Show:** `docs/release-notes.md`, the line "Deployment change required".

*"From the release notes. The team that built 1.5.0 measured it. Someone just forgot to update the deployment. That is the real root cause, and a very common one."*

*"In a GitOps setup, merging this change is what deploys it. A person reviews it and merges it. Bob does not deploy on its own."*

---

## Prompt 5: Incident note for the NOC (2 min)

New Task, Agent mode.

Type:

```
Write a short incident note for the NOC in reports/incident-note.md.
```

After:

*"What happened, impact, root cause, fix, next steps. The owner team, charging-platform, comes from the service catalogue, not from memory."*

**Show:** the `<to fill>` fields.

*"And look here: customer impact, ticket number. Bob does not have these facts, so it does not invent them. It leaves them for a person. The note says 'ready to merge', not 'resolved', because it is not deployed yet."*

---

## Prompt 6: Runbook for the next shift (2 min)

New Task, Agent mode.

Type:

```
Write a short runbook for the NOC in runbooks/pod-restarts.md.
It should help them spot and fix this problem faster next time.
```

After:

*"Signs, the commands to check, the likely cause, the fix, and who to call. The commands are the same ones the engineer used today."*

*"Today it took us a few minutes with Bob. Next time, the night shift can fix it with this runbook, even without Bob. The knowledge from one incident stays with the team."*

---

## Closing (1 min)

*"So in about fifteen minutes we went from raw evidence to:"*

- *"a root cause, proven with quotes,"*
- *"a two-line fix, with values from the release notes,"*
- *"an incident note, with the gaps left for a person,"*
- *"and a runbook for the next shift."*

*"Three things made this work. One: the team's method is written in one rule file. Two: Bob works from evidence and shows it. Three: people stay in control. Every change is reviewed, and nothing is deployed by Bob."*

*"As a next step, we can do this with your own evidence: a real incident from your team, with your rules."*

---

## If something goes differently

| What happens | What to do and say |
|---|---|
| Bob asks to run a command | Approve it. *"Bob asks before it runs anything."* |
| Bob changes more than the two memory lines | In Source Control, discard the extra change. *"This is why a person reviews every change."* |
| Bob picks a memory value that is not 192/256 | Follow-up prompt: `Use the values from docs/release-notes.md.` *"The release notes are the source, not a guess."* |
| Bob in Ask mode says it cannot write a file | That is expected. *"Ask mode is read-only."* |
| Bob is slow | Talk about the evidence while it works, for example open the Grafana CSV and show the memory climbing to the limit. |
| Something goes wrong and you want to start again | Run the reset prompt, then start from prompt 1. |

---

## Questions the client may ask

**"Can Bob connect to our live cluster?"**
*"Yes. In Agent mode Bob can run commands such as kubectl in a terminal, and it asks for approval first. For this demo we used saved evidence, so nothing touches production."*

**"What if Bob is wrong?"**
*"Every claim has a file and a line, so anyone can check it in seconds. And nothing is deployed without a person reviewing and merging it."*

**"How does Bob know our way of working?"**
*"From the rule file you saw. Your team writes it once: your method, your templates, your escalation teams. Bob reads it in every task."*

**"Can it open a pull request?"**
*"Bob works with Git in the terminal and can connect to GitHub through MCP. We can check how it fits your Git platform."*

**"Where does our data go? Can it run on-premises?"**
*"There is an on-premises option. Let's go through it separately for your environment."*

**"Does it work with our tools: Grafana, OpenShift, our ticketing system?"**
*"Here Bob read a Grafana export, kubectl output and logs as files. Connecting to live tools is possible through MCP. We would look at which tools you use."*

---

## Key facts to remember

| Fact | Value | Where |
|---|---|---|
| Capture time | Tue 22 Sep 2026, 09:44 | `evidence/README.md` |
| Pods | `x2k4p` on worker-3 (14 restarts), `q8m3z` on worker-5 (13 restarts) | `evidence/kubectl-get-pods.txt` |
| Release rollout | 48 minutes before capture, first pod started 08:56:31 | `evidence/kubectl-get-events.txt`, `evidence/kubectl-describe-pod-x2k4p.txt` |
| Cause | `OOMKilled`, exit code `137`, memory limit `64Mi` | `evidence/kubectl-describe-pod-x2k4p.txt` |
| Proof in the kernel log | `usage 65536kB, limit 65536kB` (= 64 MiB) | `evidence/worker-3-kernel.log` |
| Symptoms, not causes | Readiness probe failed; slow billing API warning | events, app log |
| Fix | request `192Mi`, limit `256Mi` | `docs/release-notes.md` |
| Owner team | `charging-platform` | `catalog-info.yaml` |
