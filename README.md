# Case Study 1: The 400TB Hybrid Data Dilemma & FinOps Optimization

## Executive Summary

This case study presents an enterprise-scale migration strategy for moving 400TB of unstructured data from an on-premises NetApp AFF cluster to Amazon FSx for NetApp ONTAP while satisfying two competing business mandates:

### Operations Mandate

* Near-Zero Downtime
* 4-Hour Cutover Window
* Predictable Rollback
* No Impact to Global Engineering Teams

### FinOps Mandate

* Avoid Lift-and-Shift
* Reduce Long-Term Storage Costs
* Eliminate Premium SSD Usage for Cold Data
* Optimize Total Cost of Ownership (TCO)

The proposed solution uses a hybrid architecture combining NetApp SnapMirror, AWS DataSync, Amazon FSx for ONTAP, and Amazon S3 Glacier to achieve both objectives.

---

# Business Problem

Current Environment:

* 400TB NetApp AFF Storage
* 300+ Volumes
* SMB and NFS Workloads
* On-Premises Data Center

Challenges:

1. Migration must complete with near-zero downtime.
2. Approximately 60% of data has not been accessed for more than three years.
3. FinOps has rejected a traditional lift-and-shift migration.
4. Production risk must remain extremely low.

---

# Architecture Overview

The architecture classifies data into Hot, Warm, and Cold tiers before migration.

```text
400TB Source Data
        │
        ▼
Metadata Classification
        │
 ┌──────┼──────┐
 ▼      ▼      ▼

Hot    Warm    Cold
80TB   80TB    240TB

 ▼      ▼       ▼

SnapMirror
        │
        ▼

FSx SSD
Capacity Tier

Cold Data
        │
        ▼

DataSync
        │
        ▼

S3 Glacier Deep Archive
```

---

# Data Classification Strategy

## Hot Data

Definition:

* Accessed within last 12 months
* Active Engineering Workloads
* Performance Sensitive

Storage Destination:

Amazon FSx for ONTAP SSD Tier

Estimated Size:

80TB

---

## Warm Data

Definition:

* Accessed between 1 and 3 years
* Compliance Records
* Historical Projects
* Occasional Retrieval

Storage Destination:

Amazon FSx for ONTAP Capacity Pool Tier

Estimated Size:

80TB

---

## Cold Data

Definition:

* No access for more than 3 years
* Archive Data
* Long-Term Retention

Storage Destination:

Amazon S3 Glacier Deep Archive

Estimated Size:

240TB

---

# Why Not Lift-and-Shift?

Traditional Approach:

```text
400TB
  │
  ▼
FSx SSD
```

Estimated Cost:

~$624,000/year

Problems:

* Expensive
* No Data Lifecycle Optimization
* Violates FinOps Requirements

---

# Recommended Hybrid Strategy

```text
Hot Data
    │
    ▼
FSx SSD

Warm Data
    │
    ▼
Capacity Pool Tier

Cold Data
    │
    ▼
Glacier Deep Archive
```

Estimated Cost:

~$160,000/year

Estimated Savings:

~$464,000/year

Cost Reduction:

~74%

---

# SnapMirror vs DataSync Decision Analysis

## SnapMirror Strengths

* Block-Level Replication
* Snapshot Consistency
* Fast Incremental Updates
* Near-Zero Downtime
* Predictable Cutover
* Fast Rollback

Limitations:

* No File Filtering
* Replicates Entire Volumes

---

## DataSync Strengths

* File-Level Filtering
* Last Access Time Filtering
* Direct Glacier Archiving
* FinOps Optimization

Limitations:

* Slower Final Sync
* Less Predictable Cutover
* File-by-File Processing

---

# Architectural Verdict

Use Both.

### SnapMirror

Used For:

* Hot Data
* Warm Data

Reason:

Operational Reliability

---

### DataSync

Used For:

* Cold Data

Reason:

Cost Optimization

---

# Network & Bandwidth Analysis

Dataset:

400TB

Migration Window:

5 Days

## 1 Gbps

Transfer Time:

~37 Days

Result:

Not Feasible

---

## 5 Gbps

Transfer Time:

~7.4 Days

Result:

High Risk

---

## 10 Gbps

Transfer Time:

~3.7 Days

Result:

Feasible

---

## 20 Gbps

Transfer Time:

~1.8 Days

Result:

Recommended

---

# Cutover Strategy

## T-24 Hours

Reduce DNS TTL

```text
86400 Seconds
        ↓
300 Seconds
```

Purpose:

Accelerate DNS Propagation

---

## T-4 Hours

Freeze Writes

Applications enter read-only mode.

---

## T-3 Hours

Final SnapMirror Update

Synchronize remaining deltas.

---

## T-2 Hours

Break SnapMirror

Convert destination to read-write.

---

## T-1 Hour

Switch DNS and DFS Namespace

Redirect client traffic.

---

## T0

Production Live on FSx

Validate:

* Read Operations
* Write Operations
* SMB Access
* NFS Mounts

---

# Go / No-Go Criteria

All conditions must be GREEN.

Validation Requirements:

* SnapMirror Healthy
* Replication Lag < 30 Minutes
* Final Transfer Success
* FSx Healthy
* SVM Online
* LIF Online
* DNS Updated
* Client Test Mount Successful
* Monitoring Active

If any RED condition exists:

NO-GO

---

# Rollback Strategy

If cutover fails:

1. Disable FSx Access
2. Restore DNS Records
3. Reconnect DFS Namespace
4. Re-enable NetApp Exports
5. Resume Client Access
6. Re-establish SnapMirror

Target Recovery Metrics:

RPO = 0

RTO < 30 Minutes

---

# Data Integrity Validation Strategy

The solution avoids a full 400TB re-read.

## Layer 1

SnapMirror Validation

Checks:

* Block-Level Integrity
* Transfer Health
* Replication Status

---

## Layer 2

Metadata Validation

Checks:

* Inode Counts
* File Counts
* Folder Counts
* Capacity Usage

---

## Layer 3

Statistical Sampling

Checks:

* SHA-256 Validation
* Random Sample Verification
* Recently Modified Data

---

## Validation Runtime

Layer 1:

Continuous

Layer 2:

< 5 Minutes

Layer 3:

< 15 Minutes

Total:

< 20 Minutes

---

# Automation Proposal

## Option Selected

Automation Option 2

SnapMirror Pre-Cutover Health Validation Engine

Purpose:

Validate 300+ volumes simultaneously before migration cutover.

---

# Validation Checks

For Every Volume:

* SnapMirror State
* Replication Lag
* Last Snapshot Transfer
* Destination Volume Health
* SVM Readiness
* LIF Readiness

---

# RAG Decision Framework

GREEN

Ready for Cutover

---

AMBER

Review Required

---

RED

Cutover Blocked

---

# Decision Engine

Any RED

→ NO-GO

No RED + Any AMBER

→ CONDITIONAL GO

All GREEN

→ GO

---

# Scalability Considerations

Current Scope:

* 300 Volumes
* 400TB

Future Scale:

* 1000+ Volumes
* Multi-Cluster
* Multi-Region

Potential Enhancements:

* AWS Step Functions
* EventBridge
* Lambda
* DynamoDB
* Grafana Dashboards
* CloudWatch Metrics

---

# Risk Assessment

| Risk                  | Mitigation                |
| --------------------- | ------------------------- |
| Replication Failure   | SnapMirror Monitoring     |
| Network Failure       | Direct Connect Redundancy |
| DNS Propagation Delay | TTL Reduction             |
| Data Corruption       | Multi-Layer Validation    |
| Cutover Failure       | Rollback Runbook          |
| Storage Cost Growth   | Tiered Data Strategy      |

---

# Business Outcomes

## Operations

✓ Near-Zero Downtime

✓ Predictable Cutover

✓ Fast Rollback

✓ Enterprise Resilience

---

## FinOps

✓ ~74% Cost Reduction

✓ ~$464K Annual Savings

✓ Cold Data Elimination from SSD

✓ Optimized Storage Lifecycle

---

# Final Recommendation

The recommended architecture is a hybrid migration model using SnapMirror for operationally critical Hot and Warm data and AWS DataSync for Cold Data archiving.

This approach simultaneously satisfies:

* Near-Zero Downtime Requirements
* 4-Hour Cutover Constraints
* FinOps Cost Optimization Goals
* Enterprise Resilience Standards
* Long-Term Storage Lifecycle Management

Result:

A scalable, resilient, and cost-optimized migration architecture that reduces annual storage costs by approximately 74% while maintaining business continuity.
