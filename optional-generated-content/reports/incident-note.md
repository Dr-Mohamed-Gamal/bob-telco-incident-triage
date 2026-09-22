# Incident note: balance-service, Tue 22 Sep 2026

## What happened

At 08:56 on 22 Sep 2026, version 1.5.0 of balance-service was rolled out in the `charging` namespace (`evidence/kubectl-get-events.txt:2`). Both pods entered `CrashLoopBackOff` immediately and had accumulated 13–14 restarts by 09:44 when evidence was captured (`evidence/kubectl-get-pods.txt:2–3`). The pods have not become healthy at any point since the rollout.

## Impact

Both replicas of balance-service (a tier-1 service, `catalog-info.yaml:7`) have been unavailable since 08:56. `<to fill>` customers affected. `<to fill>` support tickets or NOC ticket reference.

## Root cause

Version 1.5.0 introduced an in-memory subscriber cache that loads 180,000 records at startup and requires ~150 Mi of memory at peak (`docs/release-notes.md:5–6`). The deployment memory limit was not updated and remained at 64 Mi (`evidence/kubectl-describe-pod-x2k4p.txt:25`). Each time a pod starts, the OS kills it when memory hits the 64 Mi ceiling (`evidence/worker-3-kernel.log:2–3`), causing `OOMKilled` (exit code 137) and a new restart. The release notes explicitly called out the required deployment change (`docs/release-notes.md:7`), but it was not applied.

## Fix

`deploy/deployment.yaml` has been updated with the values from `docs/release-notes.md:7`:

- Memory request: `64Mi` → `192Mi`
- Memory limit: `64Mi` → `256Mi`

The change is ready to merge. Once deployed, pods will have enough memory to complete the cache load and pass their readiness probe.

## Next steps

- Merge and deploy the updated `deploy/deployment.yaml`.
- Confirm both pods reach `Running 1/1` after the rollout.
- Add a pre-deploy check or CI gate that validates the deployment manifest against the memory requirements in the release notes.
- Owner team: `charging-platform` (`catalog-info.yaml:12`).
