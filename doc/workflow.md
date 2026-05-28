# ⚙️ Operational Workflow & Coding Standards

This document establishes the development workflow, coding standards, safety guards, resilient integrations, and caching strategies.

---

## 🔒 Security Practices & Safety Guards

All updates must conform strictly to this checklist:

### 1. SQL Injection Prevention
* **Parameterized Variables:** All SQL statements compiled in `sql_builder.py` must use bound placeholders (e.g. `:status` or `:device_type`). Never concatenate query text with variables.
* **Whitelisted Columns and Operators:** Only substitute whitelisted operators (`gt`, `lt`, `eq`, `gte`, `lte`) or hardcoded column mappings via `.replace()` when utilizing optional clauses.

### 2. Prompt Injection Guard
* **Normalization Scan:** Scans user inputs case-insensitively before passing them to the Gemini model inside [prompt_guard.py](file:///c:/Users/Administrator/OneDrive/Desktop/noc_asssitant_app/network-ai-assistant/backend/app/security/prompt_guard.py).
* **Blocked Signatures:** Blocks instruction override commands, SQL command chains, metadata schema queries, or prompt extraction leaks.
* **Audit Trail Logging:** All blocks are logged as database audit trail records under `error_message` `"BLOCKED:{pattern_type}"`.

---

## ⚡ Caching, Resiliency, & Formatting

### 1. Rolling Caching Strategy
* **30-second TTL:** Queries have a short TTL to keep telemetry fresh while avoiding redundant database requests.
* **Redis Auto-Discovery:** Caches globally via Redis when configured. Falls back to a local memory cache map on dev setups without additional coding.
* **Metadata schema:** The `cache_hit` flag must be set at the root and inside the timing dictionary block.

### 2. Gemini flash Resiliency
* **Custom Retry Loop:** Wraps Gemini requests in a synchronous retry loop trying up to 3 times with progressive sleep delays (`0s` $\rightarrow$ `0.5s` $\rightarrow$ `1.0s`).
* **Format Stripping:** Sanitizes Markdown JSON code blocks (e.g. ````json ... ````) automatically.
* **Failure Boundaries:** Prevents raising raw HTTP 429 or connection exceptions. They are converted into polite `503 Service Unavailable` responses.

### 3. Local Deterministic Response Templates
* **Zero-Latency Formatting:** Database results are formatted to Markdown directly inside `response_templates.py` in **<1ms**, eliminating secondary Gemini calls.
* **Uptime Standard:** Translates seconds to human-readable days/hours/minutes (`Xd Xh Xm`).

---

## 🖥️ Frontend Telemetry & Observability

### 1. Obs-Header Pills
* **Header Indicators:** Always maintain the four system badges in `Header.jsx`: AI ready (green dot), DB status (cyan dot), active User Role text, and performance Latency displaying last successful query duration in milliseconds.
* **Friendly Axios Cards:** Axios interceptors trap all exceptions and translate them into descriptive visual alerts in the chat timeline, avoiding standard alerts or raw stacks.

### 2. Messaging Telemetry
* **Collapsible Timing Badge:** Always mount the collapsible timing pill under assistant messages, mapping intent parsing, validation, database querying, local templates formatting, and total processing delays in milliseconds.

---

## 💻 Coding Standards & Linting

* **Python Backend:**
  * Uses **Ruff** for fast linting, import sorting, and code styling.
  * Enforces a **100-character** maximum line length boundary.
  * Public modules and functions must feature **Google-Style Docstrings**.
  * Use **Pydantic** models to validate all API request/response structures.
* **React Frontend:**
  * Written exclusively in standard **Functional Components** with React Hooks.
  * Uses **ESLint** with active React Hooks rule restrictions.
  * Uses **Tailwind CSS** styling classes to maintain the premium dark-terminal NOC layout.
* **Git Commits:**
  * Enforces standard **Conventional Commit** notation:
    * `feat: ...` for new features or capabilities.
    * `fix: ...` for telemetry bugs or syntax corrections.
    * `docs: ...` for updates to markdown assets.
