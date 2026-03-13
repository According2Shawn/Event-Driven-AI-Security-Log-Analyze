# Event-Driven AI Security Log Analyzer

A serverless, event-driven pipeline that ingests security logs in real-time, analyzes them with AI, and stores actionable threat alerts — all deployed to Azure using Infrastructure as Code.

## Overview

This project simulates a real-world Security Operations Center (SOC) pipeline:

1. A **Log Generator** script produces mock security telemetry (firewall events, SSH attempts, SQL injection patterns) and streams them into **Azure Event Hubs**.
2. An **Azure Function** triggers on each batch of logs, filters out noise, and sends suspicious entries to the **OpenAI API** for threat classification.
3. Confirmed threats are written to **Azure Cosmos DB** as structured alerts.
4. The entire infrastructure is provisioned via **Terraform** and deployed automatically through **GitHub Actions**.

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────┐
│ Log Generator│────▶│ Azure Event Hubs  │────▶│  Azure Function  │────▶│  Cosmos DB   │
│  (Python)    │     │  (Ingestion)      │     │  (AI Processing) │     │  (Alerts)    │
└──────────────┘     └──────────────────┘     └──────────────────┘     └──────────────┘
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │  OpenAI API  │
                                               │  (Analysis)  │
                                               └──────────────┘
```

## Tech Stack

| Layer           | Technology             | Purpose                              |
|-----------------|------------------------|--------------------------------------|
| Ingestion       | Azure Event Hubs       | High-throughput log streaming        |
| Processing      | Azure Functions (Python) | Serverless event-driven compute    |
| AI              | OpenAI API (GPT-4o)    | Threat classification                |
| Storage         | Azure Cosmos DB        | NoSQL alert storage                  |
| Infrastructure  | Terraform              | Infrastructure as Code               |
| CI/CD           | GitHub Actions         | Automated deployment pipeline        |
| Identity        | Managed Identities     | Passwordless RBAC authentication     |

## Security Highlights

- **Zero hardcoded credentials** — Managed Identities handle all service-to-service auth
- **Least Privilege** — The GitHub Actions Service Principal is scoped to a single Resource Group
- **RBAC over Connection Strings** — The Function App uses role assignments, not passwords, to access Event Hubs and Cosmos DB

---

## Learning Guide

This section breaks down the architectural decisions behind each component. Use it to understand not just *what* was built, but *why* each choice was made.

### Why Event-Driven (Not Batch)?

Security threats require near real-time detection. A batch job running every hour leaves a 59-minute window for an attacker to operate undetected. Event-driven architectures process data the instant it arrives.

**Trade-off:** Batch processing is simpler and cheaper for non-time-sensitive workloads (monthly reports, data warehousing). For security monitoring, the latency is unacceptable.

### Why Azure Event Hubs (Not Service Bus)?

Event Hubs is a **firehose** — built for ingesting millions of events per second. It acts as a "shock absorber" between the log sources and the processing function, buffering spikes so downstream services aren't overwhelmed.

**Trade-off:** Azure Service Bus provides richer routing, dead-letter queues, and exactly-once delivery. These features matter for financial transactions but add unnecessary cost and latency for telemetry data where occasional duplicates are tolerable.

### Why Azure Functions (Not VMs or Kubernetes)?

Azure Functions on the Consumption Plan (Y1) scale from zero to thousands of instances automatically. When idle, compute cost is $0.00.

**Trade-off:** Virtual Machines run 24/7 and require OS patching, SSH key management, and manual scaling. Kubernetes (AKS) is powerful but introduces significant operational overhead. Both are overkill for a stateless log processing script.

### Why Python (Not C# or Node.js)?

Python is the dominant language in AI/ML, cybersecurity tooling, and data processing. The OpenAI SDK, Azure SDKs, and data manipulation libraries are all first-class citizens in the Python ecosystem.

**Trade-off:** C# is native to Azure and offers better raw performance. Java provides strong enterprise tooling. However, both require significantly more boilerplate code for the same functionality.

### Why Cosmos DB (Not SQL)?

Security logs and AI responses have variable JSON structures. A NoSQL document database accepts any valid JSON without requiring schema migrations. Adding a new field like `threat_score` tomorrow requires zero database changes.

**Trade-off:** Relational databases (Azure SQL) excel at enforcing strict data relationships (Orders → Customers → Products). For independent, schema-variable log alerts, that rigidity becomes a liability.

### Why Terraform (Not Azure Portal or Bicep)?

Terraform treats infrastructure as versionable, reviewable code. It's cloud-agnostic — the same workflow applies to AWS, GCP, or Azure.

**Trade-off:** ARM Templates and Bicep are Microsoft's native IaC tools with tighter Azure integration and zero-day feature support. However, learning them locks your skills to a single cloud provider. Terraform is the industry standard across all major clouds.

### Why Managed Identities (Not Connection Strings)?

Connection strings are permanent passwords. If one leaks in a Git commit, the associated resource is compromised until it's manually rotated. Managed Identities eliminate this risk entirely — Azure handles authentication using short-lived tokens behind the scenes.

**Trade-off:** Managed Identities only work within the Azure ecosystem. For external services (like the OpenAI API), traditional API keys are still required.

### Why GitHub Actions CI/CD?

Automating deployment eliminates human error and enforces consistency. Every push to `main` triggers the exact same Terraform workflow in a clean environment.

**Trade-off:** Running Terraform locally gives faster feedback during development. GitHub Actions adds a ~2 minute overhead per run. The consistency and auditability gains far outweigh the wait time for production deployments.