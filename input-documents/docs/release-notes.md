# balance-service release notes

## 1.5.0 (2026-09-22)

- New: the subscriber cache is loaded at start-up, so balance lookups no longer call billing for every request.
- The cache holds 180000 subscribers and uses about 150Mi of memory at peak.
- **Deployment change required:** set the memory request to 192Mi and the memory limit to 256Mi.

## 1.4.2 (2026-08-30)

- Subscriber numbers are masked in logs.
