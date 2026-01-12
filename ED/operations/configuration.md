# Configuration Management (The Authority)

**Antigravity** follows the **Authority Chain** pattern for configuration. This solves the "Split Brain" problem where the `.env` file, the runtime variables, and the database disagree on the truth.

**Source**: `ai/agent_runner/config_manager.py`

---

## 1. The Authority Hierarchy

1.  **Sovereign Memory (SurrealDB)**: The **Single Source of Truth**. If a value exists here, it overrides everything else.
2.  **Runtime State (`state.config`)**: The active configuration in RAM (cached from DB).
3.  **Disk (`config/`, `.env`)**: The **Backup/Cold Storage**. Used for bootstrapping and disaster recovery.

---

## 2. Synchronization Logic

At startup, `ConfigManager.check_and_sync_all()` reconciles these layers.

### Phase 3 Sync Optimization (Fast-Path)

To prevent slow startups caused by reading every config file and hashing it (MD5), the system uses **mtime (Modification Time)** caching.

1.  **Check mtime**: `os.path.getmtime(file)`.
2.  **Compare**: Check `meta:file_mtime` in DB.
3.  **Fast Path**: If mtime matches, **SKIP** content read.
4.  **Slow Path**: If mtime differs:
    *   Compute MD5 hash of file content.
    *   Compare with `meta:file_hash` in DB.
    *   If hash differs -> **Ingest** file into DB (Update Truth).
    *   Update `meta:file_mtime` and `meta:file_hash`.

### Bi-Directional Sync

- **Ingest**: Disk -> DB (Startup).
- **Persist**: Runtime Change -> DB + Disk (Runtime).
    *   When the user changes the model via the UI, `set_config_value` updates the DB *and* writes back to `config.yaml` or `system_config.json`, keeping the backup in sync.

---

## 3. Managing Secrets

Secrets (API Keys) are handled carefully:

- **Sources**: `.env` file or `os.environ`.
- **Logic**:
    *   Secrets are ingested into the `config_state` table in SurrealDB (encrypted at rest if DB supports it, otherwise plain text in this version).
    *   When `ConfigManager` updates a secret, it patches the `.env` file in place using regex, preserving comments and structure where possible.

---

## 4. File Mapping

| Config Type | Source File | DB Table |
| :--- | :--- | :--- |
| **System** | `system_config.json` | `config_state` |
| **Models** | `config/config.yaml` | `config_state` |
| **Secrets** | `.env` | `config_state` |
| **MCP** | `config/mcp.yaml` | `mcp_server` |

Note: `mcp.yaml` is special; it populates the `mcp_server` table directly.
