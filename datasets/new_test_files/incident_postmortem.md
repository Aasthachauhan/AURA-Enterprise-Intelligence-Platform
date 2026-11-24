# Post-Mortem: SEV-1 Database Replication Lag & Aurora Cluster Failover
**Date of Incident:** 2026-11-18  
**Incident Commander:** Principal SRE Lead  
**Impacted Services:** Core Transaction API, Vector Embedding Pipeline, Knowledge Graph Sync  
**Total Downtime / Degraded Operations:** 24 minutes  

---

## 1. Executive Summary
On November 18, 2026, at 14:12 UTC, a transient network partition between AWS us-east-1a and us-east-1b caused an abrupt spike in Aurora PostgreSQL replication lag, exceeding the 2500ms safety threshold. The automated failover mechanism promoted the replica in us-east-1c to primary. During the 90-second promotion window, API writes encountered HTTP 503 errors. Full automated recovery occurred at 14:36 UTC without transaction loss.

## 2. Root Cause Analysis (5 Whys)
1. **Why did API write calls fail?** The primary database instance transitioned to read-only during failover promotion.
2. **Why did failover trigger?** The replication lag watchdog detected a 3200ms lag exceeding the 2500ms health check threshold.
3. **Why did replication lag spike?** High-volume batch re-indexing of 50,000 PDF documents saturated the I/O bus during an unexpected network packet drop.
4. **Why was batch ingestion uncapped?** The background document ingestion worker did not have exponential backoff or write rate-limiting enabled.
5. **Why was rate-limiting absent?** Ingestion pipeline v1 assumed dedicated Aurora read-replicas for batch embedding generation.

## 3. Preventive Action Items & SLAs
- **ACT-01 (P0):** Implement token-bucket rate limiter (50 docs/min) on ingestion queue workers. *Owner: Platform Eng | Status: In Progress*
- **ACT-02 (P0):** Route all vector embedding read queries exclusively to dedicated read-replicas. *Owner: Data Eng | Status: Completed*
- **ACT-03 (P1):** Increase replication lag tolerance window from 2.5s to 5.0s during peak hours. *Owner: SRE | Status: Completed*
- **ACT-04 (P2):** Configure automated Slack pager alerting when replication lag exceeds 1000ms. *Owner: DevOps | Status: Completed*
