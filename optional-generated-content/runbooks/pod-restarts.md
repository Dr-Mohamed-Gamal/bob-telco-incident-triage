# Runbook: balance-service pod restarts

## Signs

- One or more `balance-service` pods show `CrashLoopBackOff` or `OOMKilled` in `kubectl get pods`.
- Restart count is climbing and pods never reach `Running 1/1`.

## Check

```
kubectl get pods -n charging -l app=balance-service -o wide
kubectl describe pod <pod> -n charging
kubectl logs <pod> -n charging --previous
kubectl get events -n charging --sort-by=.lastTimestamp
```

Look for in `kubectl describe pod <pod>`:
- `Last State: Terminated` → `Reason: OOMKilled` and `Exit Code: 137` — the pod ran out of memory.
- The `memory` limit under `Limits:` — compare it to the current release notes.

Look for in `kubectl logs … --previous`:
- Lines like `Subscriber cache: N of 180000 records loaded` near the end — the pod was killed mid cache-load.

## Likely cause

A new version of balance-service was deployed without updating the memory limit in `deploy/deployment.yaml`. The subscriber cache introduced in 1.5.0 needs ~150 Mi at peak; if the limit is too low the OS kills the process on every startup.

Check the release notes (`docs/release-notes.md`) for a **Deployment change required** notice and compare the required memory values to what is set in `deploy/deployment.yaml` under `resources.limits.memory`.

## Fix

Update `deploy/deployment.yaml` to the memory values stated in the release notes for the running image version. For 1.5.0:

```yaml
resources:
  requests:
    memory: 192Mi
  limits:
    memory: 256Mi
```

Merge and deploy. Confirm pods reach `Running 1/1` after the rollout.

## Escalate to

Owner team: `charging-platform` (`catalog-info.yaml`).
