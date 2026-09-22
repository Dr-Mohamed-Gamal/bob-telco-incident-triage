# Incident evidence: balance-service restarts

Captured by the on-call engineer on Tue 22 Sep 2026 at 09:44 +0400, cluster `prod-1`, namespace `charging`.

| File | How it was captured |
|---|---|
| `kubectl-get-pods.txt` | `kubectl get pods -n charging -l app=balance-service -o wide` |
| `kubectl-describe-pod-x2k4p.txt` | `kubectl describe pod balance-service-7d9f8c6b5d-x2k4p -n charging` |
| `kubectl-get-events.txt` | `kubectl get events -n charging --sort-by=.lastTimestamp` |
| `balance-service-x2k4p-previous.log` | `kubectl logs balance-service-7d9f8c6b5d-x2k4p -n charging --previous` |
| `worker-3-kernel.log` | `journalctl -k --since "09:30" --until "09:44"` on node `worker-3` |
| `grafana-memory-x2k4p.csv` | Grafana panel "Memory working set", pod `balance-service-7d9f8c6b5d-x2k4p`, 09:35 to 09:44, exported as CSV. Missing times mean no container was running. |
