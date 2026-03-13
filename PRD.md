Event-Driven AI Security & Log Analyzer.

Instead of IT support tickets, this project ingests high-volume infrastructure logs (like simulated firewall drops, server metrics, or login attempts), uses an LLM to detect anomalous patterns or potential threats, and routes the high-priority alerts to a database.

This is a fantastic way to show that you understand underlying cloud network concepts and know exactly how to layer AI on top of them to reduce manual monitoring fatigue. It also specifically incorporates Azure Event Hubs, which was explicitly requested in the job description for handling streaming data.

Here is the blueprint for a project that showcases the same senior-level end-to-end ownership.
Project: Event-Driven AI Security Log Analyzer

The Concept: A streaming data pipeline that ingests simulated server and network logs. An Azure Function reads these logs in batches, passes them to an LLM to act as a "Level 1 Security Analyst" to identify real threats versus background noise, and stores actionable alerts in Cosmos DB.

The Tech Stack:

    Infrastructure as Code: Terraform

    Language: Python (or C#/.NET Core)

    Messaging/Streaming: Azure Event Hubs (designed for high-throughput log ingestion)

    Compute: Azure Functions (Event Hub Trigger)

    Database: Azure Cosmos DB

    AI: OpenAI / Gemini API

    CI/CD: GitHub Actions

Step-by-Step Execution Plan
Phase 1: Infrastructure as Code (Terraform)

This demonstrates you can architect a secure, scalable foundation.

    Create a main.tf to provision:

        A Resource Group.

        An Azure Event Hubs namespace and an Event Hub (the ingestion point).

        An Azure Cosmos DB account and database (the storage point).

        A Linux Azure Function App and its required Storage Account.

    Why this matters: It proves you can build enterprise-grade infrastructure from code, treating deployments as reproducible artifacts.

Phase 2: The Log Generator (The "Mock" Source)

You need data to flow into your system to prove it works.

    Write a standalone Python script that acts as a log generator.

    It should randomly generate JSON log entries (e.g., {"timestamp": "...", "ip": "192.168.1.50", "event": "Failed SSH login", "server": "app-vm-01"}) and push them to your Event Hub.

    Why this matters: It shows you understand how applications emit telemetry and how to interface with Azure's streaming services.

Phase 3: The AI Analyst Pipeline (Azure Function)

This is where the software engineering and prompt engineering merge.

    Build an Azure Function triggered by the Event Hub. As logs stream in, the function processes them in batches.

    The Prompt Engineering: The function bundles a batch of logs and sends them to the LLM with a prompt like: "You are a cloud security analyst. Review this batch of server logs. Identify any patterns that suggest a coordinated attack, unauthorized access, or critical failure. Ignore routine background noise. Return a JSON array of critical alerts containing 'threat_level', 'description', and 'recommended_action'."

    Parse the LLM's JSON response. If the AI identified a threat, the Python code writes that specific threat record into Cosmos DB.

Phase 4: CI/CD and Quality Assurance

Prove your senior developer habits.

    Write unit tests for your Python log parsing and API calling logic.

    Set up a GitHub Actions workflow to run the tests and deploy your Terraform code.