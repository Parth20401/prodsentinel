# Engineering Issues & Resolutions - prodsentinel-pipeline

This document catalogs the major technical challenges, bugs, and architectural issues encountered during the development and verification of Phase 3: Async Analysis Pipeline.

---

## 1. Celery PermissionError on Windows

- **Issue Summary**: Celery worker fails to start on Windows with `PermissionError: [WinError 5] Access is denied`.
- **Context / When it occurred**: Initialization of the `prodsentinel-pipeline` worker on a Windows OS.
- **Symptoms & Observed Behavior**: The worker process crashed immediately during multi-processing setup.
- **Root Cause Analysis**: Celery's default `prefork` pool uses `fork()` on Unix and `spawn` on Windows, but the `spawn` implementation often conflicts with Python subprocess management on Windows without specific configurations.
- **Resolution / Fix Applied**: Forced the Celery pool to `solo` using `--pool=solo`.
- **Preventive Measures or Lessons Learned**: Always specify the pool type when running Celery on Windows for development.

---

## 2. Broken Alembic Migration Chain

- **Issue Summary**: Database migrations failed due to a missing migration file for a version ID present in the DB.
- **Context / When it occurred**: During Database Migration setup for `Incident` and `AnalysisResult` tables.
- **Symptoms & Observed Behavior**: `alembic upgrade head` failed with "Can't find revision f5ae8e59ef66".
- **Root Cause Analysis**: A "phantom" migration ID was present in the `alembic_version` table without a corresponding Python file (likely due to a mid-generation failure or manual deletion).
- **Resolution / Fix Applied**: Manually updated the `alembic_version` table to the last know "good" revision using a Python script, then re-generated the migration.
- **Preventive Measures or Lessons Learned**: Treat migration files as immutable; if a generation fails, use `alembic current` and `revision --autogenerate` carefully to synchronize.

---

## 3. Celery Asyncio Loop AttributeError

- **Issue Summary**: Worker crashed with `AttributeError: 'NoneType' object has no attribute 'send'` inside `asyncio/proactor_events.py`.
- **Context / When it occurred**: During execution of the `analyze_trace` task.
- **Symptoms & Observed Behavior**: Task received successfully, but failed immediately with a proactor loop error.
- **Root Cause Analysis**: The task was using a global SQLAlchemy `AsyncEngine` while running inside `asyncio.run()`. `asyncio.run()` creates a new event loop, but the global engine was still bound to the initial loop (now closed or different).
- **Resolution / Fix Applied**: Refactored the database module to provide engine factory functions. The task now creates and disposes of a fresh engine for every execution.
- **Preventive Measures or Lessons Learned**: Never share global async resources across `asyncio.run()` lifecycle boundaries in multi-process workers.

---

## 4. Duplicate Analysis (Race Condition)

- **Issue Summary**: Multiple `AnalysisResult` entries were created for a single `trace_id`.
- **Context / When it occurred**: End-to-end verification with rapid-fire failure logs.
- **Symptoms & Observed Behavior**: Two nearly simultaneous Celery tasks were queued, resulting in duplicate AI runs and database records.
- **Root Cause Analysis**: 
    1. **Backend Isolation**: In-memory deduplication failed because Uvicorn ran multiple worker processes.
    2. **Race Condition**: The `trace_id` was marked as "triggered" *after* the async `send_task` call, allowing a second request to slip through the check.
- **Resolution / Fix Applied**: 
    1. Implemented **distributed deduplication** using Redis `SETNX` (via `redis.set(nx=True)`).
    2. Moved the "mark as triggered" step to be atomic and *before* the task queuing.
- **Preventive Measures or Lessons Learned**: Use Redis for distributed state in web servers. Always mark a state as "in-progress" *before* starting an expensive async operation.

---

## 5. Enum Attribute Logic Error

- **Issue Summary**: Task failed with `AttributeError: type object 'IncidentStatus' has no attribute 'HIGH'`.
- **Context / When it occurred**: Persistence phase of the analysis task.
- **Symptoms & Observed Behavior**: AI analysis succeeded, but the database write failed.
- **Root Cause Analysis**: A logical typo where `IncidentStatus` (Open/Closed) was used instead of `IncidentSeverity` (High/Medium/Low).
- **Resolution / Fix Applied**: Corrected the reference to `IncidentSeverity.HIGH`.
- **Preventive Measures or Lessons Learned**: Use IDE autocomplete and type-checking (mypy) to catch enum mismatches early.

---

## 6. SQLAlchemy Connection Pool Warning

- **Issue Summary**: Logs showed `SAWarning: The garbage collector is trying to clean up non-checked-in connection`.
- **Context / When it occurred**: After task completion.
- **Symptoms & Observed Behavior**: Warning messages about connection termination in the worker terminal.
- **Root Cause Analysis**: The default `QueuePool` was holding idle connections associated with a closed asyncio loop (since we use internal loop cycling).
- **Resolution / Fix Applied**: Switched to `NullPool` for the pipeline service to ensure connections are closed immediately and never pooled across task boundaries.
- **Preventive Measures or Lessons Learned**: Use `NullPool` for ephemeral/short-lived event loops to avoid connection leak warnings.
