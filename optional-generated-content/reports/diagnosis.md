# Diagnosis: balance-service pods keep restarting

**In plain words:** The balance-service was upgraded to a new version that loads a large list of subscribers into memory when it starts up. The new version needs about 150 MB of memory to do this, but the deployment was not updated to give it enough — it was still set to a 64 MB cap from the old version. Every time the service starts, it runs out of its allowed memory while loading that list and the operating system forcibly shuts it down. This happens on every restart, so the service never becomes healthy. The fix is to raise the memory cap in the deployment file to the values the new version requires.

**Root cause:** Version 1.5.0 introduced an in-memory subscriber cache that requires ~150 Mi of memory at peak load. The deployment's memory limit was not updated from the previous 64 Mi, so the Linux OOM killer terminates the Python process every time the cache finishes loading, causing a repeating `OOMKilled` → `CrashLoopBackOff` cycle.

## Evidence

| File:line | Exact text | What it shows |
|---|---|---|
| `evidence/kubectl-describe-pod-x2k4p.txt:17` | `Reason:       OOMKilled` | The last container termination reason is an out-of-memory kill |
| `evidence/kubectl-describe-pod-x2k4p.txt:18` | `Exit Code:    137` | Exit code 137 confirms the process was killed by the OS (SIGKILL from OOM killer) |
| `evidence/kubectl-describe-pod-x2k4p.txt:24–25` | `cpu:     500m` / `memory:  64Mi` | The running memory limit is 64 Mi — unchanged from before the upgrade |
| `evidence/worker-3-kernel.log:2` | `memory: usage 65536kB, limit 65536kB, failcnt 211` | The cgroup hit its 64 Mi limit exactly; the OOM killer was invoked |
| `evidence/worker-3-kernel.log:3` | `Memory cgroup out of memory: Killed process 47730 (python) total-vm:411920kB, anon-rss:64988kB` | The kernel killed the service process for exceeding the memory cgroup limit |
| `evidence/worker-3-kernel.log:5–8` | second OOM kill block at `09:42:31` | The same kill happens again on the next restart, proving this is systematic, not a one-off spike |
| `evidence/grafana-memory-x2k4p.csv:7` | `2026-09-22T09:42:30+04:00,balance-service-7d9f8c6b5d-x2k4p,66060288` | Memory working set reached 63 Mi (≈ 66 060 288 bytes) at the moment of the kill — right at the 64 Mi ceiling |
| `evidence/balance-service-x2k4p-previous.log:4–5` | `Subscriber cache: 120000 of 180000 records loaded` / `Subscriber cache: 170000 of 180000 records loaded` | The service was mid-load of 180 000 records when it was killed — cache load is the memory driver |
| `evidence/kubectl-get-pods.txt:2–3` | both pods in `CrashLoopBackOff`, 13–14 restarts | Both replicas are affected identically, ruling out a node-specific fault |
| `docs/release-notes.md:6–7` | `The cache holds 180000 subscribers and uses about 150Mi of memory at peak. **Deployment change required:** set the memory request to 192Mi and the memory limit to 256Mi.` | The release notes document the new memory requirement and explicitly call out the deployment change that was missed |

## Not the cause

| File:line | Exact text | Why it is not the cause |
|---|---|---|
| `evidence/kubectl-describe-pod-x2k4p.txt:43` | `Readiness probe failed: … connection refused` | Symptom, not cause — the probe fails because the process is already dead or still starting after a kill; nothing is listening on port 8080 as a consequence of the OOM kill |
| `evidence/kubectl-describe-pod-x2k4p.txt:44` | `Back-off restarting failed container balance-service` | Symptom — `BackOff` is Kubernetes throttling restarts after repeated failures; it does not explain why the container fails |
| `evidence/balance-service-x2k4p-previous.log:3` | `Billing API slow response: 1240 ms (threshold 1000 ms)` | A slow external API call during startup; the pod was not killed at this moment and the warning pre-dates the OOM kill by several seconds |

## Fix

In [`deploy/deployment.yaml`](deploy/deployment.yaml) lines 35–37, change the memory `requests` and `limits` to the values stated in [`docs/release-notes.md:7`](docs/release-notes.md):

```yaml
          resources:
            requests:
              cpu: 100m
              memory: 192Mi
            limits:
              cpu: 500m
              memory: 256Mi
```

This fix is ready to merge. There is no live cluster in this environment.
