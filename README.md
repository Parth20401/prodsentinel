# ProdSentinel

> **Incident Analysis & Automated Root Cause Detection**

**ProdSentinel** is a production-focused incident analysis platform designed to ingest logs, traces, and metrics from distributed services, correlate failure signals, and generate structured root-cause insights. The system emphasizes correctness, observability, and deterministic reprocessing over black-box inference.

---

## 1. Project Overview

ProdSentinel solves the "alert fatigue" problem by automating the first hour of incident response. Instead of just alerting on a 500 error, ProdSentinel ingests the raw telemetry, correlates it with distributed traces, and uses an agentic AI pipeline directly in the loop to analyze code paths, logs, and state to produce a high-confidence Root Cause Analysis (RCA) report.

Key differentiator: **It does not guess.** It correlates hard signals (Trace IDs, Stack Traces) before asking AI models to reason about them.

## 2. What Problem This Solves

Modern microservices fail in complex ways. A payment failure in Service A might be caused by a timeout in Service B, which was caused by a database lock in Service C. 

**The Challenge:**
- **Fragmented Context:** Logs, metrics, and traces live in different tools.
- **Manual Correlation:** Engineers waste hours manually grepping logs to find the "smoking gun."
- **Noise:** False positives from transient network blips wake engineers up unnecessarily.

**The ProdSentinel Solution:**
- **Unified Ingestion:** One API for all signal types.
- **Automated Correlation:** Deterministic linking of distributed traces.
- **AI Analyst:** An asynchronous worker that "reads" the logs and traces like a senior engineer would, outputting a clear RCA.

## 3. High-Level Architecture

The system is split into three decoupled planes: **Ingestion (Write-Heavy)**, **Analysis (Async/Compute-Heavy)**, and **Visualization (Read-Only)**.

```mermaid
graph TD
    subgraph "Traffic Generation"
        FS[Simulated Microservices] -->|HTTP POST /ingest| API[Backend API]
    end

    subgraph "Ingestion Plane"
        API -->|Validate| Pydantic{Schema}
        Pydantic -->|Valid| DB[(PostgreSQL)]
        API -->|Event Trigger| Redis[(Redis Queue)]
    end

    subgraph "Analysis Plane (Async)"
        Redis -->|Debounce Window| Celery[Celery Worker]
        Celery -->|Fetch Context| DB
        Celery -->|Prompt| Agents[AutoGen + Gemini]
        Agents -->|RCA Report| DB
    end

    subgraph "Visualization Plane"
        DB <-->|Read Only| Frontend[Next.js Dashboard]
    end
```

## 4. End-to-End Data Flow

This flows describes the lifecycle of a `500 Internal Server Error` as it propagates through ProdSentinel.

1.  **Signal Emission**: The `payment-service` encounters a simulated DB timeout. It emits a structured log with `trace_id` and `level: ERROR` to the ProdSentinel Backend.
    *   *Endpoint:* `POST /ingest/logs`
2.  **Ingestion & Triage**: The Backend validates the payload schema.
    *   **Immutability**: The raw log is saved immediately to PostgreSQL `logs` table.
    *   **Smart Trigger**: The system detects `level >= ERROR`. It pushes a task to Redis with the `trace_id`.
3.  **Deduplication (The "Noise Filter")**:
    *   If 50 errors occur for the same `trace_id` within 60 seconds (a "storm"), Redis helps debounce them. Only *one* analysis task is scheduled per trace.
4.  **Asynchronous Analysis**:
    *   The **Celery Worker** picks up the task.
    *   **Context Gathering**: It queries the DB for *all* logs and spans associated with that `trace_id`.
    *   **Agentic Reasoning**: The AutoGen agents (Summarizer & Investigator) review the stack trace and DB latency metrics.
    *   **Conclusion**: They determine "Database Connection Timeout due to saturation."
5.  **Persistence**: The final `AnalysisResult` is written to the database, linked to the Incident.
6.  **Visualization**: The Frontend polls the API and displays the new Incident with the generated RCA report.

## 5. Live Demo

The frontend is deployed as a read-only visualization layer:

🔗 **Live UI**: [ProdSentinel Dashboard](https://prodsentinel.vercel.app/)

Incidents are not triggered from the UI. Failures originate from external services and propagate through the ingestion and analysis pipeline before appearing in the dashboard. This tries to mirror real-world observability systems.

## 6. Reproducing a Failure

To prove the system's determinism, you can spin up the local stack and generate real traffic.

**Prerequisites:** Docker, Python 3.12+

1.  **Start the Stack**:
    The "Stack" refers to the core infrastructure (PostgreSQL, Redis), the Backend API, and the Pipeline Workers.
    ```bash
    docker-compose up -d
    ```
2.  **Start the Traffic Generators**:
    We use simulated microservices to generate realistic traffic patterns.
    ```bash
    # In a new terminal
    ./run_hybrid_agents.bat
    ```
3.  **Simulate Traffic**:
    The `fake-payment` service has a deterministic failure trigger. Sending `fail-pay` in the `order_id` will force an error.
    ```bash
    # Trigger a deterministic payment failure
    curl -X POST http://localhost:8004/pay/order-fail-pay-123
    ```
4.  **Observations**:
    - Watch the backend logs: `docker logs -f prodsentinel-backend`
    - See the task picked up by Celery.
    - View the result in the local DB or Live UI.


## 7. Configuration (.env)

Each service requires specific environment variables. Create a `.env` file in the respective service directories.

### `prodsentinel-backend/.env`
```ini
# Application
LOG_LEVEL=INFO

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/prodsentinel

# Broker (Redis)
REDIS_URL=redis://localhost:6379/0
```

### `prodsentinel-pipeline/.env`
```ini
# Database & Broker (Must match backend)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/prodsentinel
REDIS_URL=redis://localhost:6379/0

# AI Configuration (Gemini)
GOOGLE_API_KEY=<your_key_here>
```

### `prodsentinel-fake-services/.env`
```ini
# Target Backend URL
PRODSENTINEL_URL=http://localhost:8000
```

### `prodsentinel-frontend/.env` (Optional)
If running locally via Vite.
```ini
# API Base URL
VITE_API_URL=http://localhost:8000
```

## 8. Service Endpoints

A breakdown of the key APIs across the ProdSentinel ecosystem.

### **Backend Service (Port 8000)**
The central nervous system.
- `POST /ingest/logs`: Accepts structured logs.
- `POST /ingest/traces`: Accepts distributed trace spans.
- `POST /ingest/metrics`: Accepts numeric metrics.
- `GET /query/signals`: Search raw telemetry.
- `GET /query/incidents`: Retrieve detected incidents.
- `GET /query/incidents/{id}/analysis`: Fetch the AI-generated Root Cause Analysis.

### **Pipeline Service**
- **Worker**: Does not expose HTTP endpoints; consumes tasks from Redis.
- **Management API (Port 8001)**: `POST /debug/analyze/{trace_id}` (Manual Trigger).

### **Simulated Services ("Traffic Generators")**
- **Payment Service (Port 8004)**: `POST /pay/{order_id}` - Simulates payment processing (Source of failures).
- **Inventory Service (Port 8002)**: `GET /inventory/{item_id}` - Called by Payment Service.
- **API Gateway (Port 8003)**: Routes requests to Payment/Inventory.

## 9. Design Decisions & Tradeoffs

> [!NOTE]
> We prioritized data integrity and system stability over real-time processing speed.

| Decision | Tradeoff | Rationale |
| :--- | :--- | :--- |
| **Async Analysis Pipeline** | Latency (~10s delay) | **Backpressure Handling**. In a massive outage, we do not want the analysis engine to crash the ingestion service. Queuing allows us to smooth out spikes. |
| **Immutable Log Storage** | Storage Cost | **Auditability**. We never modify raw logs. If the AI makes a mistake, we can re-run the analysis on the original data. |
| **Read-Only Frontend** | UX Friction | **Security**. The dashboard is for observability, not control. Separation of concerns prevents "fat-finger" operational errors from a viewing interface. |
| **Fire-and-Forget Telemetry** | Potential Data Loss | **Performance**. The simulators use `asyncio.create_task` to send logs. If the logging fails, it shouldn't crash the main user transaction. |
| **Middleware Tracing** | Framework Locking | **Consistency**. We implemented a custom `request_context_middleware` to guarantee `trace_id` appears in every log line, ensuring 100% correlation. |
| **Deterministic Failure Injection** | Test Rigidity | **Reproducibility**. Using special IDs (e.g., `fail-pay`) allows us to run exact integration tests instead of relying on flaky random failures. |

## 9. What This Is Not

*   **Not a Replacement for Datadog/Splunk**: ProdSentinel is an *analysis* layer, not a long-term data warehouse. It focuses on the "hot path" of incident response.
*   **Not a Remediation Tool**: It will tell you *what* is wrong, but it will not restart your servers (yet). Automatic remediation requires a higher level of trust.
