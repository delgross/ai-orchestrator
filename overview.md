# Antigravity AI System - Code Review & Quality Assessment

## 1. Goal + Key Constraints

**Goal:** Build a robust, self-healing AI agent platform that safely executes tools via MCP servers, maintains sovereign memory in SurrealDB, and provides reliable chat/streaming interfaces with automatic failover and observability.

**Constraints:**
- **Time:** Startup sequence must complete within 30-60 seconds (currently ~25s)
- **Scope:** Multi-service architecture (Agent Runner, Router, RAG, Memory) with 18+ MCP servers
- **Environment:** Darwin/macOS with Python 3.12+, SurrealDB, Ollama, FastAPI
- **Runtime:** 24/7 operation with graceful degradation
- **Language:** Python async-first architecture
- **Deployment:** Local development with cloud model fallback
- **Regulatory:** No HIPAA/PII compliance requirements identified
- **Contracts:** Must not break Router auth (currently failing internal calls)

## 2. Context Snapshot

**System Type:** Multi-service AI agent orchestrator with MCP tool ecosystem  
**Critical Flows:** Chat → Nexus → Engine → Tool Selection → MCP Execution → Response Streaming  
**Primary Users:** End users via chat interface, developers via admin APIs  
**Runtime Targets:** Local Ollama models (fast path), cloud models (governed path)  
**Current Pain Signals:**
- Router auth deadlock causing 30s hydration hangs
- Circuit breaker failures disabling weather/brave-search MCP servers
- High process count (1074) indicating resource leaks
- Memory server stability issues during startup
- Missing environment variables causing degraded mode

## 3. What Matters / Unknowns

**What Matters Most (Ranked):**
1. **System availability** - 24/7 operation with graceful degradation
2. **Tool execution safety** - MCP server reliability and circuit breaker effectiveness
3. **Memory persistence** - SurrealDB sovereignty and transaction safety
4. **Streaming performance** - Low-latency chat responses
5. **Observability** - Unified tracking across all components

**Unknowns Blocking Certainty:**
- Root cause of Router auth token propagation failure
- Long-term memory server stability under load
- MCP server failure patterns and recovery effectiveness
- Impact of high process count on system performance

**Assumptions (Explicit):**
- System runs on single macOS machine with sufficient resources
- Network connectivity is generally available but may be intermittent
- Users accept degraded functionality when services fail

## 4. Architecture & Boundaries

**High-Level Component Map:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Router        │    │  Agent Runner   │    │     RAG         │
│   (Port 5455)   │◄──►│   (Port 5460)   │◄──►│   (Port 5555)   │
│                 │    │                 │    │                 │
│ • Auth Gateway  │    │ • Nexus Pattern │    │ • Vector Search │
│ • Load Balance │    │ • Tool Selection│    │ • Document Ing. │
│ • Rate Limit   │    │ • MCP Orchestr. │    │ • Chunking      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   SurrealDB     │    │   Ollama        │
│   (Web UI)      │    │   (Port 8000)   │    │                 │
│                 │    │                 │    │ • Local Models  │
│ • Chat Stream   │    │ • Sovereign Mem │    │ • Embeddings    │
│ • System Status │    │ • MCP Config    │    │ • Fast Path     │
│ • Admin Panel   │    │ • Episode Store │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Ownership/Module Boundaries:**
- `agent_runner/` - Core orchestration logic
- `router/` - Authentication and load balancing
- `common/` - Shared utilities and logging
- `config/` - Configuration management
- `rag_server.py` - Vector search and document processing

**Coupling Risks & Hidden Dependencies:**
- **Tight coupling:** Router auth token required for internal calls but not propagated
- **Shared state:** Global ServiceRegistry creates implicit dependencies
- **Process coupling:** Subprocess lifecycle management (RAG server, MCP servers)

**Data/Control Flow (Critical Paths):**
1. **Chat Flow:** User Input → Nexus Triggers → Engine Tool Selection → MCP Execution → Response Streaming
2. **Memory Flow:** Tool Results → Memory Server → Vector Indexing → RAG Retrieval → Context Hydration

**Single Points of Failure:**
- **SurrealDB** - Complete memory loss if database fails
- **Router Auth** - Currently broken, causing hydration hangs
- **Service Registry** - Global state management bottleneck

## 5. Code Quality & Correctness

**Code Health Issues (Top 5):**
1. **Massive main.py** (1080 lines) - Startup orchestration logic is monolithic
2. **Complex async orchestration** - Multiple race conditions in startup sequence
3. **Global state management** - ServiceRegistry creates tight coupling
4. **Inconsistent error handling** - Mix of try/catch, circuit breakers, and fail-open patterns
5. **Configuration drift** - Multiple config sources (DB, YAML, env vars) without sync guarantees

**Complexity Hotspots/Churn Areas:**
- `agent_runner/main.py` - 1080 lines of startup logic
- `agent_runner/engine.py` - Tool selection and routing logic
- `agent_runner/executor.py` - MCP server orchestration
- `agent_runner/memory_server.py` - Database operations

**Error Handling & Invariants:**
- **Strengths:** Circuit breaker pattern for MCP servers, transaction safety in memory operations
- **Weaknesses:** Fail-open budget system, inconsistent error propagation, missing rollback on startup failures

**Input Validation & Contracts:**
- **Strong:** Pydantic models for API contracts, Sentinel security for command execution
- **Weak:** Missing validation for config loading, no schema validation for memory operations

**Orphaned/Dead Code Candidates:**
- `lazy_mcp_loader.py.disabled` - Disabled but not removed
- Multiple commented-out code blocks in main.py startup sequence
- Unused imports and legacy configuration paths

## 6. Kludges, Tech Debt, and Simplification

**Suspected Kludges (Symptom → Likely Cause):**
- **Router Auth Bypass** → Missing token propagation in internal calls
- **Direct Ollama Routing** → Workaround for Router latency issues
- **Background Process Management** → Complex lifecycle management for RAG/MCP subprocesses
- **Configuration Override Logic** → Multiple config sources with unclear precedence

**Simplify by Removing/Merging:**
- **Duplicate Config Loading** - Consolidate DB vs disk config logic
- **Multiple HTTP Clients** - State has persistent client but startup creates new ones
- **Redundant Health Checks** - Background internet check + startup validation
- **Complex Startup Phases** - Merge some of the 7-step startup sequence

**Replace Ad-Hoc with Standard Patterns:**
- **Global Service Registry** → Dependency injection container
- **Async Queue Multiplexing** → Structured async event system
- **Subprocess Lifecycle** → Process supervisor pattern

**Migration Plan to Remove Safely:**
1. **Phase 1:** Consolidate configuration management (1 week)
2. **Phase 2:** Implement proper dependency injection (2 weeks)
3. **Phase 3:** Simplify startup orchestration (1 week)
4. **Phase 4:** Standardize error handling patterns (1 week)

## 7. Performance, Latency, and Resource Profile

**Likely Latency Sources (CPU/Mem/IO/Network/Lock Contention):**
- **Database Queries** - SurrealDB vector searches during context hydration (30s hangs)
- **MCP Discovery** - Sequential server discovery during startup (45s timeouts)
- **Process Spawning** - RAG server and MCP subprocess creation
- **Memory Operations** - Schema validation and transaction safety checks

**N+1 / Query Patterns / Indexing Concerns:**
- **MCP Tool Loading** - No caching of tool definitions between restarts
- **Memory Indexing** - Tool re-indexing on every startup
- **Config Loading** - Multiple DB queries for configuration

**Caching Opportunities and Cache Invalidation Risks:**
- **Tool Definitions** - Cache MCP tool schemas with invalidation on server changes
- **Configuration** - Persistent config cache with file/DB sync
- **Vector Embeddings** - Pre-computed embeddings for common queries

**Concurrency/Async Pitfalls:**
- **Race Conditions** - Multiple async tasks in startup without proper coordination
- **Deadlocks** - Potential blocking calls in async context (subprocess management)
- **Starvation** - Background tasks competing with main request processing

**Cost Drivers (Cloud/DB/Egress/Compute):**
- **API Calls** - External MCP servers (Tavily, Perplexity, etc.)
- **Database** - SurrealDB storage and vector operations
- **Compute** - Local Ollama inference + cloud model fallbacks

## 8. Reliability & Resilience

**Failure Modes (Timeouts/Retries/Partial Outages):**
- **MCP Server Failures** - Circuit breaker pattern with auto-disable
- **Database Connection** - Degraded mode when SurrealDB unavailable
- **Network Issues** - Background connectivity monitoring
- **Process Crashes** - Subprocess lifecycle management

**Backpressure / Queue Behavior:**
- **System Event Queue** - Asyncio.Queue for system alerts
- **Request Queuing** - No explicit backpressure in chat endpoints
- **Memory Operations** - No rate limiting on database queries

**Idempotency & Retry Safety:**
- **Strong:** Database operations with transaction safety
- **Weak:** API endpoints lack idempotency keys
- **Missing:** Retry logic for failed external API calls

**Rate Limiting / Quotas:**
- **Implemented:** Basic circuit breaker pattern for MCP servers
- **Missing:** User-level rate limiting, API quotas

**Fallback Behavior When Dependencies Fail:**
- **Database:** Degraded mode without memory features
- **MCP Servers:** Auto-disable with circuit breaker
- **Router:** Direct Ollama routing bypass
- **Network:** Local-only model operation

## 9. Security & Supply Chain

**AuthN/AuthZ Review Points:**
- **Router Authentication:** Token-based but broken for internal calls
- **API Endpoints:** No authentication on agent runner endpoints
- **MCP Servers:** No authentication between agent and MCP servers

**Secrets Handling:**
- **Environment Variables** - API keys stored in env vars and database
- **Config Files** - Sensitive data in YAML configs
- **Runtime** - Secrets passed to subprocesses via environment

**Injection Vectors / Unsafe Deserialization / SSRF / etc:**
- **Command Injection:** Sentinel security for shell commands (good)
- **SQL Injection:** SurrealDB parameterized queries (good)
- **SSRF:** MCP server URLs not validated
- **Deserialization:** JSON parsing without schema validation

**Dependency Risk (Vulns/Licenses/Transitive Bloat):**
- **Dependencies:** 27 Python packages including FastAPI, httpx, pydantic
- **MCP Servers:** External subprocesses with various licenses
- **Licenses:** Mix of MIT, Apache, and proprietary licenses
- **Vulnerabilities:** No dependency scanning visible

**Build Provenance, SBOM, Signing, Minimal Images:**
- **Missing:** No SBOM generation, no build signing
- **Container Images:** No containerization visible
- **Minimal Images:** Large Python environment with many dependencies

## 10. Data Model, Privacy, and Compliance

**Schema Constraints & Integrity:**
- **SurrealDB Schema:** fact, episode, mcp_server tables
- **Constraints:** Basic table definitions but no foreign key relationships
- **Integrity:** Transaction safety but no referential integrity

**Migration Safety + Rollback Compatibility:**
- **Migrations:** No visible migration system
- **Rollback:** No rollback procedures documented
- **Versioning:** No database versioning strategy

**Retention/TTL/Deletion:**
- **Episodes:** No TTL or retention policies visible
- **Facts:** No cleanup procedures for old knowledge
- **Logs:** Log rotation configured but no retention limits

**PII Classification & Handling:**
- **Data Types:** Chat history, tool results, user preferences
- **PII Risk:** Location data, API usage patterns
- **Handling:** No explicit PII classification or masking

**Audit Trails / Access Logging:**
- **Logging:** Basic application logging with logfire integration
- **Audit:** No audit trails for sensitive operations
- **Access:** No access logging for API calls

## 11. APIs & Compatibility

**Public Contracts and Consumers:**
- **Router API (5455):** Chat completions, authentication
- **Agent Runner API (5460):** Admin controls, health metrics
- **Internal APIs:** MCP server protocol, memory server HTTP

**Versioning Strategy:**
- **Missing:** No API versioning visible
- **OpenAPI:** Generated spec exists but no versioning

**Backward Compatibility Risks:**
- **High:** No versioning means breaking changes affect all consumers
- **Internal:** MCP protocol changes could break tool compatibility

**Validation (Schemas, Types, OpenAPI):**
- **Pydantic:** Used for request/response validation
- **OpenAPI:** Generated from FastAPI routes
- **MCP:** Protocol validation through MCP library

## 12. Configuration & Feature Flags

**Config Management Risks (Drift/Env Parity):**
- **Multiple Sources:** DB, YAML files, environment variables
- **Sync Issues:** No guarantee of consistency between sources
- **Drift:** Configuration can become out of sync

**Flag Lifecycle (Creation → Rollout → Cleanup):**
- **Missing:** No feature flag management system
- **Ad-hoc:** Configuration flags without lifecycle management

**Kill Switches / Safe-Mode Options:**
- **Implemented:** Circuit breakers for MCP servers
- **Missing:** System-wide kill switches, safe mode

**Default Settings and Foot-guns:**
- **Budget System:** Fail-open on budget errors (unsafe default)
- **Command Execution:** Disabled by default (safe)
- **Auth:** Router auth enabled but not working internally

## 13. Testing & Verification Quality

**Current Coverage Gaps (Unit/Integration/E2e):**
- **Unit Tests:** Basic test files exist but coverage unknown
- **Integration:** No visible integration test suite
- **E2E:** No end-to-end test automation

**Property/Fuzz Tests Where Useful:**
- **Missing:** No property-based or fuzz testing
- **Useful For:** MCP server protocol validation, config parsing

**Golden Tests/Contract Tests:**
- **Missing:** No contract tests for API compatibility
- **Golden Tests:** No snapshot testing visible

**Load/Perf Tests and What They Should Measure:**
- **Missing:** No load testing infrastructure
- **Should Measure:** Chat response latency, MCP server throughput, memory query performance

**CI Failures or Flaky Tests:**
- **Unknown:** No CI system visible in codebase
- **Local Testing:** pytest configuration exists but no CI pipeline

## 14. Operational Readiness

**Observability (Metrics/Logs/Traces Coverage for Critical Paths):**
- **Logging:** Comprehensive logging with logfire integration
- **Metrics:** Health monitoring and circuit breaker telemetry
- **Traces:** Logfire provides distributed tracing
- **Gaps:** No metrics collection, no alerting system

**SLOs/SLIs Alignment + Alert Quality:**
- **Missing:** No SLO definitions or SLI measurements
- **Health Checks:** Basic health endpoints exist

**Runbooks/On-Call Playbooks:**
- **Missing:** No runbooks or incident response procedures
- **Documentation:** Basic operational docs in ED/ directory

**Incident Response Hooks:**
- **Kill Switches:** Circuit breaker auto-disable
- **Rollback:** No automated rollback procedures

**Chaos Testing / Game Days:**
- **Missing:** No chaos engineering or game day procedures

## 15. Plan (3--7 Steps)

1. **Fix Router Auth Deadlock** (Week 1) - Propagate ROUTER_AUTH_TOKEN to internal calls to resolve hydration hangs
2. **Consolidate Configuration Management** (Week 1-2) - Create single source of truth for config with proper sync
3. **Implement Dependency Injection** (Week 2-3) - Replace ServiceRegistry with proper DI container
4. **Add Comprehensive Testing** (Week 3-4) - Unit tests, integration tests, and basic load testing
5. **Standardize Error Handling** (Week 4) - Consistent error patterns across all components
6. **Add Observability Infrastructure** (Week 5) - Metrics collection, alerting, and runbooks
7. **Security Audit & Hardening** (Week 6) - Review secrets handling, add API authentication, validate dependencies

## 16. Options (Always A/B/C)

**A) Fastest Safe Containment (Stabilize Now)**
- **What to do:** Fix Router auth token propagation, disable failing MCP servers, add basic monitoring
- **Pros:** Quick stability improvement, reduces immediate pain signals
- **Cons:** Doesn't address architectural issues, temporary fixes
- **Risks:** Continued tech debt accumulation, harder future changes

**B) Root-Cause Fix (Correctness + Durability)**
- **What to do:** Complete architecture refactor with proper DI, consolidate config, add comprehensive testing
- **Pros:** Long-term maintainability, eliminates core issues, future-proof
- **Cons:** Longer timeline, higher risk of regression
- **Risks:** Extended instability during refactor, resource intensive

**C) Subtractive Simplification (Remove to Improve)**
- **What to remove/merge:** Eliminate Router auth complexity (direct routing only), remove MCP server orchestration complexity, simplify startup sequence
- **Pros:** Faster, reduces complexity, focuses on core chat functionality
- **Cons:** Loses multi-model routing and tool ecosystem features
- **Risks:** Feature regression, user impact if advanced features are needed

## 17. Verify (Success Signals + Fallback)

**Success Signals (Measurable):**
- Startup time < 30 seconds consistently
- Zero hydration hangs or auth failures
- All MCP servers healthy (circuit breaker closed)
- Memory server stability > 99.9% uptime
- Chat response latency < 2 seconds P95

**How to Validate (Steps):**
1. Monitor startup logs for clean completion without warnings
2. Load test chat endpoints with concurrent users
3. Verify MCP server health via circuit breaker status
4. Check memory server connectivity and query performance
5. Review logs for error patterns and failure modes

**Fallback/Rollback if Not Working:**
- **Immediate:** Revert Router auth changes, restore direct routing bypass
- **Partial:** Disable problematic MCP servers, enable degraded mode
- **Full:** Restore from backup if system becomes unstable

## 18. Prevent Recurrence

**Process Changes:**
- **Code Reviews:** Require architecture review for core component changes
- **Design Docs:** ADRs required for significant architectural changes
- **Testing:** Automated tests required for all core components

**Guardrails:**
- **Static Analysis:** Add mypy for type checking, pylint for code quality
- **CI Pipeline:** Automated testing, linting, and security scanning
- **Performance Budgets:** Maximum startup time, response latency limits
- **Dependency Scanning:** Automated vuln scanning and license compliance

**Documentation Updates:**
- **Architecture Docs:** Update ED/ documentation with new patterns
- **Runbooks:** Create incident response and operational procedures
- **API Docs:** Versioned API documentation with deprecation notices

**Debt Register + Cleanup Cadence:**
- **Monthly Reviews:** Technical debt assessment and prioritization
- **Quarterly Cleanup:** Dedicated sprints for tech debt reduction
- **Automated Alerts:** Code quality metrics and technical debt tracking

## 19. Risk Register (Top Items)

**Risk: Router Auth Deadlock | Impact: High | Likelihood: High | Mitigation: Fix token propagation | Owner: Dev Team | Due: Week 1 | Verification: No more hydration hangs**
**Risk: Memory Server Instability | Impact: High | Likelihood: Medium | Mitigation: Add connection pooling and retry logic | Owner: Dev Team | Due: Week 2 | Verification: >99.9% uptime**
**Risk: Configuration Drift | Impact: Medium | Likelihood: High | Mitigation: Single config source with validation | Owner: Dev Team | Due: Week 1 | Verification: Config audit passes**
**Risk: MCP Server Failures | Impact: Medium | Likelihood: Medium | Mitigation: Improve circuit breaker logic and health checks | Owner: Dev Team | Due: Week 2 | Verification: <5% server failures**
**Risk: Security Vulnerabilities | Impact: High | Likelihood: Low | Mitigation: Dependency scanning and secrets audit | Owner: Dev Team | Due: Week 3 | Verification: Clean security scan**

## 20. Appendix: Evidence

**Repos/Branches Reviewed:** Local Antigravity workspace (/Users/bee/Sync/Antigravity/ai)
**Files/Modules Inspected (Representative List):**
- `agent_runner/main.py` - Core startup orchestration
- `agent_runner/engine.py` - Tool selection and routing
- `agent_runner/memory_server.py` - Database operations
- `agent_runner/nexus.py` - Input processing and triggers
- `ED/architecture/*.md` - System architecture docs

**Commands Run (Build/Test/Lint/Bench):**
- File size analysis (find/wc commands)
- Linter error checking (read_lints)
- Code pattern analysis (grep for TODO/security patterns)

**Logs/Metrics/Traces Consulted:**
- `agent_runner.log` - Recent startup logs and errors
- `current_health.json` - System health status
- `recent_work_audit.md` - Recent changes and known issues

**Dependency Inventories Used:**
- `pyproject.toml` - Python dependencies and versions
- `agent_runner/requirements.txt` - Additional requirements

**Known Missing Artifacts:**
- Complete test suite execution results
- Performance benchmarks under load
- Security vulnerability scan results
- CI/CD pipeline configuration

**Confidence Level + Why:** High confidence in architectural assessment (reviewed core components and docs), Medium confidence in specific performance metrics (no load testing data), Low confidence in security posture (no vulnerability scanning performed). Analysis based on code inspection, logs, and documentation review.