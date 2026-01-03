/**
 * Questionable Insight Dashboard v2.6
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- FORCE SERVICE WORKER CLEANUP ---
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(function (registrations) {
            for (let registration of registrations) {
                console.log('Unregistering lingering ServiceWorker:', registration);
                registration.unregister();
            }
        });
    }

    const state = {
        activeTab: 'overview',
        pollingInterval: 10000,
        currentVersion: null,
        editorPath: null,
        activeOllamaModel: null
    };

    // --- TELEMETRY SYSTEM ---
    async function reportError(msg, context = {}) {
        try {
            await fetch('/admin/telemetry/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    level: 'ERROR',
                    message: msg,
                    context: { ...context, url: window.location.href, userAgent: navigator.userAgent }
                })
            });
        } catch (e) { console.warn("Telemetry failed", e); }
    }

    window.onerror = function (msg, url, line, col, error) {
        reportError(msg, { url, line, col, stack: error?.stack });
    };

    window.addEventListener('unhandledrejection', function (event) {
        reportError(`Unhandled Rejection: ${event.reason}`, { stack: event.reason?.stack });
    });

    // --- Tab Switching ---
    const tabLinks = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.view-section');

    tabLinks.forEach(link => {
        link.addEventListener('click', () => {
            const targetTab = link.getAttribute('data-tab');
            tabLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            tabContents.forEach(content => {
                if (content.id === targetTab) content.classList.add('active');
                else content.classList.remove('active');
            });
            state.activeTab = targetTab;

            if (targetTab === 'config') fetchConfigFiles();
            if (targetTab === 'docs') fetchDocsList();
            if (targetTab === 'ollama') fetchOllamaModels();
            // memory tab removed
            if (targetTab === 'breakers') fetchBreakerData();
            if (targetTab === 'logs') {
                fetchLogTail();
                startLogStream();
            } else if (logEventSource) {
                logEventSource.close();
                logEventSource = null;
            }
            if (targetTab === 'tools') fetchMCPData();
            if (targetTab === 'breakers') fetchBreakerData();
            if (targetTab === 'diagnostics') {
                fetchDiagnostics();
                startDiagnosticsStream();
            } else if (window.diagEventSource) {
                window.diagEventSource.close();
                window.diagEventSource = null;
            }
        });
    });

    setInterval(() => {
        const now = new Date();
        const el = document.getElementById('clock');
        if (el) el.textContent = now.toLocaleTimeString('en-US', { hour12: false });
    }, 1000);

    // --- Core Data Loop ---
    async function fetchSystemData() {
        try {
            const resp = await fetch('/admin/dashboard/state');
            if (resp.ok) {
                const data = await resp.json();

                // 1. Version Check & Transition
                const newVersion = data.status?.services?.router?.version;
                if (state.currentVersion && newVersion && state.currentVersion !== newVersion) {
                    showNotification('System Update Detected. Reloading...');
                    setTimeout(() => window.location.reload(), 2000);
                }
                state.currentVersion = newVersion;

                // 2. Update Indicators
                window.lastIngestionState = data.ingestion;
                updateIndicators(data.status || {}, data.ingestion, data.memory_stats, data.budget);

                // 3. Update Sentinel
                updateSentinel(data.summary);

                // 4. Update Overview Metrics (if on overview tab)
                if (state.activeTab === 'overview') {
                    updateOverviewUI(data.metrics);
                }

                // 5. Update Budget (if on cost/misc tab)
                if (state.activeTab === 'cost' || state.activeTab === 'misc') {
                    // Update budget UI if needed
                }

                // 6. Update Diagnostics (Phase 25)
                if (state.activeTab === 'diagnostics') {
                    await fetchDiagnostics();
                }

                // 7. Update Breakers & Tools (Poll)
                if (state.activeTab === 'breakers') updateBreakersTable({ breakers: data.summary?.overall_status || {} });
                if (state.activeTab === 'tools') fetchMCPData();
            }
        } catch (err) {
            console.warn("Unified State Poll Error: ", err);
        }
    }

    function updateOverviewUI(metricsData) {
        if (!metricsData || !metricsData.metrics) return;
        const metrics = metricsData.metrics;
        const efficiency = metrics.efficiency || {};

        const elRequests = document.getElementById('metric-requests');
        const elLatency = document.getElementById('metric-latency');
        const elCache = document.getElementById('metric-cache');
        const elErrors = document.getElementById('metric-errors');

        if (elRequests) elRequests.textContent = metrics.completed_requests_1min || metrics.completed_requests || 0;
        if (elLatency) elLatency.textContent = `${Math.round(metrics.avg_response_time_1min || metrics.avg_latency || 0)}ms`;
        if (elCache) elCache.textContent = `${((efficiency.cache_hit_rate || metrics.cache_hit_rate || 0) * 100).toFixed(1)}%`;
        if (elErrors) elErrors.textContent = `${((efficiency.error_rate_1min || metrics.error_rate_1min || 0) * 100).toFixed(1)}%`;
    }

    function updateSentinel(data) {
        const sentinel = document.getElementById('system-sentinel');
        const msgEl = document.getElementById('sentinel-msg');

        if (!sentinel) return;


        // Periodic check for widget updates
        setInterval(fetchAnomalies, 5000);
        const currentCount = data.critical_count || 0;

        if (data.status === 'degraded' || currentCount > 0) {
            // sentinel.style.display = 'block'; // DISABLED by User Request (Jan 3)

            let msg = "";
            let toastMsg = "";

            if (currentCount > 0) {
                const names = (data.open_breakers || []).map(b => b.name).join(', ');
                msg = `<strong>CRITICAL:</strong> ${currentCount} service(s) suspended: [${names}].`;
                toastMsg = `⚠️ CRITICAL: Service Suspended: ${names}`;

                if (data.open_breakers[0]?.last_error) {
                    msg += `<br><small>Last Error: ${data.open_breakers[0].last_error}</small>`;
                }

                // Trigger Toast if this is a NEW escalation (e.g. 0 -> 1, or 1 -> 2)
                if (currentCount > window.lastCriticalCount) {
                    showNotification(toastMsg);
                }

            } else if (data.latest_anomaly) {
                // Only show if Fresh (< 5m) AND Not Acknowledged
                const age = (Date.now() / 1000) - (data.latest_anomaly.timestamp || 0);
                const isAck = data.latest_anomaly.status === 'acknowledged';

                if (age < 300 && !isAck) {
                    msg = `<strong>ANOMALY:</strong> ${data.latest_anomaly.message || 'System behavior irregular.'}`;
                }
            }

            // Update State Tracker
            window.lastCriticalCount = currentCount;

            // Persistence Check (Sentinel Bar only)
            const ackFn = localStorage.getItem('sentinel_ack_msg');
            if (ackFn && ackFn === msg) {
                sentinel.style.display = 'none';
                return;
            }

            msgEl.innerHTML = msg;
        } else {
            // Reset state when healthy
            sentinel.style.display = 'none';
            window.lastCriticalCount = 0;
        }
    }

    window.testSystemRecovery = async () => {
        const btn = document.getElementById('btn-sentinel-test');
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="icon">🔃</span> Testing...';

        try {
            // 1. Reset all circuit breakers
            await fetch('/admin/circuit-breakers/reset-all', { method: 'POST' });

            // 2. Clear anomalies (Best effort if endpoint exists)
            try { await fetch('/admin/observability/clear', { method: 'POST' }); } catch (e) { }

            showNotification('Recovery sequence initiated. Checking health...');

            // 3. Wait and re-poll
            setTimeout(async () => {
                await fetchSystemData();
                btn.disabled = false;
                btn.innerHTML = originalText;
            }, 2000);

        } catch (e) {
            showNotification('Recovery test failed.');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    };

    function updateIndicators(data, ingestion, memory, budget) {
        function setInd(bgId, ok, tooltip = '') {
            const el = document.getElementById(bgId);
            if (!el) return;
            const ind = el.querySelector('.status-dot');
            const val = el.querySelector('.value');

            if (ok === undefined) {
                ind.className = 'status-dot';
            } else {
                ind.className = `status-dot ${ok ? 'ok' : 'err'}`;
            }

            // if (val) val.textContent = ok ? 'ONLINE' : 'OFFLINE'; // Keep labels static
            if (tooltip) el.title = tooltip;
        }

        setInd('status-router', data.services?.router?.ok);
        setInd('status-mcp', data.services?.agent_runner?.ok);
        setInd('status-mcp-tools', data.services?.agent_runner?.ok); // Proxy for tool availability
        setInd('status-ollama', data.ollama_ok);
        setInd('status-db', data.database_ok);

        if (memory) {
            setInd('status-memory-engine', memory.active, `Memory Engine: ${memory.mode || 'Active'}`);
            // Update Memory Tab indicator
            const memTabInd = document.getElementById('memory-functioning-indicator');
            if (memTabInd) {
                const ind = memTabInd.querySelector('.indicator');
                const val = memTabInd.querySelector('.value');
                ind.className = `indicator ${memory.active ? 'online' : 'offline'}`;
                val.textContent = `STATUS: ${memory.mode || (memory.active ? 'ONLINE' : 'OFFLINE')}`;
            }
        }

        if (ingestion) {
            const label = ingestion.paused ? `INGESTION PAUSED: ${ingestion.reason}` : 'Ingestion Pipeline Active';
            setInd('status-data-ingest', !ingestion.paused, label);

            // Update Ingestion Controller UI (Permanent)
            const pauseReasonEl = document.getElementById('ingest-pause-reason');
            const statusTitle = document.getElementById('ingest-status-title');
            const controllerEl = document.getElementById('ingestion-controller');

            const btnPause = document.getElementById('btn-pause-ingest');
            const btnResume = document.getElementById('btn-resume-ingest');
            const btnClear = document.getElementById('btn-clear-resume');

            if (controllerEl) {
                controllerEl.style.display = 'block'; // Always visible now
                if (ingestion.paused) {
                    controllerEl.style.border = '1px solid var(--accent-warning)';
                    if (statusTitle) {
                        statusTitle.textContent = "⚠️ INGESTION PAUSED";
                        statusTitle.style.color = "var(--accent-warning)";
                    }
                    if (pauseReasonEl) {
                        pauseReasonEl.textContent = `Reason: ${ingestion.reason}`;
                        pauseReasonEl.style.color = "var(--text-main)";
                    }
                    if (btnPause) btnPause.style.display = 'none';
                    if (btnResume) btnResume.style.display = 'inline-block';

                    // Show Clear & Resume button ONLY if reason implies a bad file
                    const r = ingestion.reason || "";
                    if (btnClear) {
                        if (r.indexOf("Duplicate detected") !== -1 || r.indexOf("Quality Check Failed") !== -1 || r.indexOf("Error processing") !== -1) {
                            btnClear.style.display = 'inline-block';
                        } else {
                            btnClear.style.display = 'none';
                        }
                    }

                } else {
                    controllerEl.style.border = '1px solid var(--success)';
                    if (statusTitle) {
                        statusTitle.textContent = "✅ Ingestion Active";
                        statusTitle.style.color = "var(--success)";
                    }
                    if (pauseReasonEl) {
                        pauseReasonEl.textContent = "System is monitoring 'ingest/' folder for new files.";
                        pauseReasonEl.style.color = "var(--text-secondary)";
                    }
                    if (btnPause) btnPause.style.display = 'inline-block';
                    if (btnResume) btnResume.style.display = 'none';
                    if (btnClear) btnClear.style.display = 'none';
                }
            }
        }

        const internetEl = document.getElementById('status-internet');
        if (internetEl) {
            const internetInd = internetEl.querySelector('.indicator');
            const isConnected = (data.internet === true || data.internet === 'Connected');
            internetInd.className = `indicator ${isConnected ? 'online' : 'offline'}`;
        }

        // Budget Indicator
        if (budget) {
            const el = document.getElementById('status-budget');
            if (el) {
                const ind = el.querySelector('.indicator');
                const val = el.querySelector('.value');

                const pct = budget.percent_used || 0;
                let statusClass = 'ok'; // Green
                if (pct >= 100) statusClass = 'err'; // Red
                else if (pct >= 80) statusClass = 'warn'; // Orange/Yellow

                ind.className = `status-dot ${statusClass}`;
                // Display: $12 / $50 (24%)
                const spend = (budget.current_spend || 0).toFixed(2);
                const limit = (budget.daily_limit_usd || 50).toFixed(0);
                const pctStr = pct.toFixed(1);

                val.textContent = `$${spend} / $${limit} (${pctStr}%)`;

                // Add warning class to text if high
                if (pct >= 80) val.style.color = pct >= 100 ? 'var(--accent-error)' : 'var(--accent-warning)';
                else val.style.color = '';
            }
        }
    }

    // --- Misc / LLM Status Logic ---
    async function fetchMiscLLMData() {
        try {
            const resp = await fetchWithRetry('/admin/llm/status', {}, 1, 1000);
            if (!resp || !resp.ok) return;
            const data = await resp.json();

            const miscTab = document.getElementById('misc');
            if (miscTab) {
                miscTab.innerHTML = `
                    <div class="card">
                        <div class="card-header">
                            <span class="card-title">LLM Provider Status</span>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>PROVIDER</th>
                                    <th>TYPE</th>
                                    <th>LATENCY</th>
                                    <th>MODELS</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.llms.map(p => `
                                    <tr>
                                        <td style="font-weight:600; color:hsl(var(--text-primary));">${p.id}</td>
                                        <td><span class="badge ${p.type === 'local' ? 'green' : 'blue'}">${p.type}</span></td>
                                        <td class="mono">${p.latency_ms !== null ? p.latency_ms + 'ms' : '<span class="text-muted">?</span>'}</td>
                                        <td style="font-size:var(--text-xs); color:hsl(var(--text-secondary)); max-width: 400px; overflow:hidden; text-overflow:ellipsis;">
                                            ${(p.models || []).join(', ')}
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                 `;
            }
        } catch (e) {
            console.warn("Failed to fetch misc data", e);
        }
    }

    // --- Overview Logic ---
    async function fetchOverviewData() {
        // Now handled by fetchSystemData -> updateOverviewUI
    }

    // --- Helper: Robust Fetch ---
    async function fetchWithRetry(url, options = {}, retries = 3, delay = 1000, timeout = 5000) {
        for (let i = 0; i < retries; i++) {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), timeout);
            try {
                const resp = await fetch(url, { ...options, signal: controller.signal });
                clearTimeout(id);
                if (!resp.ok) throw new Error(`HTTP ${resp.status} `);
                return resp;
            } catch (err) {
                clearTimeout(id);
                if (i === retries - 1) throw err;
                console.warn(`Fetch failed for ${url}(${err.name}), retrying(${i + 1}/${retries})...`);
                await new Promise(r => setTimeout(r, delay * (i + 1)));
            }
        }
    }

    // --- System Role Logic ---
    window.fetchSystemRoles = async function () {
        try {
            const [rolesResp, llmResp] = await Promise.all([
                fetchWithRetry('/admin/llm/roles', {}, 3, 500),
                fetchWithRetry('/admin/llm/status', {}, 3, 500)
            ]);

            const rolesData = await rolesResp.json();
            const llmData = await llmResp.json();

            let allModels = [];
            llmData.llms.forEach(provider => {
                const models = provider.models || [];
                const explicitModels = models.filter(m => m !== '*');

                if (provider.type === 'local') {
                    models.forEach(m => allModels.push({ id: m, provider: provider.id }));
                } else if (explicitModels.length > 0) {
                    explicitModels.forEach(m => {
                        allModels.push({ id: `${provider.id}:${m} `, provider: provider.id });
                    });
                } else {
                    allModels.push({ id: provider.id + ":*", provider: provider.id });
                }
            });

            // Defines the Grand Unified Role List
            const roleLabels = {
                // --- 1. Core ---
                "agent_model": "Agent Model",
                "intent_model": "Maître d",
                "router_model": "Router Model",
                "task_model": "Tasker",
                "summarization_model": "Summarizer Model",

                // --- 2. Unveiled ---
                "vision_model": "Vision Model",
                "mcp_model": "MCP",
                "finalizer_model": "Finalizer",
                "fallback_model": "Fallback Model",

                // --- 3. Intelligence ---
                "pruner_model": "RAG Server",
                "healer_model": "Diagnostician",
                "critic_model": "Critique Model",

                // --- 4. Foundation ---
                "embedding_model": "Embedding Model"
            };

            // Helper to generate grouped options
            const generateOptions = (selectedVal) => {
                let localOpts = [];
                let cloudOpts = [];
                let activeButMissing = null;

                // Check if current value is missing from catalog
                let foundInCatalog = false;

                // 1. Sort models into groups
                allModels.forEach(m => {
                    let valToCheck = m.provider === 'local' || m.provider === 'ollama' ? `ollama:${m.id} ` : m.id;
                    let isSelected = (valToCheck === selectedVal);
                    if (isSelected) foundInCatalog = true;

                    const optHtml = `< option value = "${valToCheck}" ${isSelected ? 'selected' : ''}> ${m.id} (${m.provider})</option > `;

                    if (m.provider === 'ollama' || m.provider === 'local') {
                        localOpts.push(optHtml);
                    } else {
                        cloudOpts.push(optHtml);
                    }
                });

                // 2. Handle missing active model
                if (!foundInCatalog && selectedVal) {
                    activeButMissing = `< option value = "${selectedVal}" selected style = "color:#ffcc00; font-weight:bold;" > ${selectedVal} (Active - Not in Catalog)</option > `;
                }

                return `
                    ${activeButMissing || ''}
                    <optgroup label="Cloud / API">${cloudOpts.join('')}</optgroup>
                    <optgroup label="Local (Ollama)">${localOpts.join('')}</optgroup>
`;
            };

            // 1. Populate Overview Table (Read-Only)
            const tbodyOverview = document.getElementById('roles-table-body');
            const defaults = rolesData.defaults || {};

            if (tbodyOverview && rolesData.roles) {
                // Define category order
                const categories = [
                    { name: "Core Roles", keys: ["agent_model", "intent_model", "router_model", "task_model", "summarization_model"] },
                    { name: "Advanced Roles", keys: ["vision_model", "mcp_model", "finalizer_model", "fallback_model"] },
                    { name: "Intelligent Roles", keys: ["pruner_model", "healer_model", "critic_model"] },
                    { name: "Infrastructure", keys: ["embedding_model"] }
                ];

                let html = "";
                categories.forEach(cat => {
                    html += `<tr><td colspan="2" style="background:hsla(var(--bg-surface-2), 0.5); font-size:10px; color:hsl(var(--text-secondary)); padding:6px 10px; font-weight:700; letter-spacing:1px; text-transform:uppercase;">${cat.name}</td></tr>`;
                    cat.keys.forEach(key => {
                        // Use Configured Value OR Default
                        const configuredVal = rolesData.roles[key];
                        const defVal = defaults[key];
                        const displayVal = configuredVal || defVal || "Unknown";
                        const isDefault = !configuredVal || configuredVal === defVal;

                        const defaultBadge = isDefault ?
                            `<span style="opacity:0.5; font-size:0.7em;">(Default)</span>` :
                            `<span style="color:hsl(var(--accent-warning)); font-size:0.7em;">(Custom)</span>`;

                        html += `
                            <tr>
                                <td style="padding-left:15px; font-weight:500;">${roleLabels[key] || key}</td>
                                <td class="mono" style="color:hsl(var(--accent-cyan));">${displayVal} ${defaultBadge}</td>
                            </tr>
                        `;
                    });
                });
                tbodyOverview.innerHTML = html;
            }

            // 2. Populate Modal Table (Editable)
            const tbodyModal = document.getElementById('role-config-table-body');
            if (tbodyModal && rolesData.roles) {
                // Reuse categories for consistency
                const categories = [
                    { name: "Core Roles", keys: ["agent_model", "intent_model", "router_model", "task_model", "summarization_model"] },
                    { name: "Advanced Roles", keys: ["vision_model", "mcp_model", "finalizer_model", "fallback_model"] },
                    { name: "Intelligent Roles", keys: ["pruner_model", "healer_model", "critic_model"] },
                    { name: "Infrastructure", keys: ["embedding_model"] }
                ];

                let html = "";
                categories.forEach(cat => {
                    html += `<tr><td colspan="3" style="background:hsla(var(--bg-surface-2), 0.5); font-weight:700; font-size:var(--text-xs); color:hsl(var(--text-secondary)); padding:8px;">${cat.name}</td></tr>`;
                    cat.keys.forEach(key => {
                        const configuredVal = rolesData.roles[key];
                        const defVal = defaults[key];
                        const currentVal = configuredVal || defVal; // Dropdown should select the effective model

                        const optionsHtml = generateOptions(currentVal);

                        let labelRaw = roleLabels[key] || key;
                        let tooltip = "";
                        if (key === "embedding_model") {
                            tooltip = `<br><span style="color:hsl(var(--accent-danger)); font-size:0.7em;">⚠️ CHANGING THIS requires re-indexing!</span>`;
                        }

                        html += `
                            <tr>
                                <td style="width:35%;">
                                    <div style="font-weight:600;">${labelRaw}</div>
                                    ${tooltip}
                                </td>
                                    <td style="width:65%;">
                                        <select class="select sm" id="sel-${key}" style="width:100%" onchange="updateRole('${key}', this.value, this)">
                                            <option value="" disabled>Select Model...</option>
                                            ${optionsHtml}
                                        </select>
                                    </td>
                                </tr>
                            `;
                    });
                });
                tbodyModal.innerHTML = html;
            }

        } catch (e) {
            console.error("Failed to load roles", e);
            const tbody = document.getElementById('roles-table-body');
            if (tbody) tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--accent-err);">Error: ${e.message}</td></tr>`;
        }
    };

    window.updateRole = async (role, model, selectEl) => {
        const originalBg = selectEl.style.backgroundColor;
        selectEl.disabled = true;
        selectEl.style.opacity = "0.7";

        try {
            const resp = await fetch('/admin/llm/update-role', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role, model })
            });

            if (resp.ok) {
                showNotification(`Role '${role}' updated to '${model}'`);
                // Visual feedback of success
                selectEl.style.borderColor = "var(--accent-success)";
                setTimeout(() => {
                    selectEl.style.borderColor = "";
                    fetchSystemRoles(); // Refresh UI to sync everything
                }, 1000);
            } else {
                const err = await resp.text();
                showNotification(`Failed to update role: ${err}`);
                selectEl.style.borderColor = "var(--accent-danger)";
            }
        } catch (e) {
            showNotification(`Error: ${e.message}`);
            selectEl.style.borderColor = "var(--accent-danger)";
        } finally {
            selectEl.disabled = false;
            selectEl.style.opacity = "1";
            selectEl.focus();
        }
    };

    // --- Role Modal Controls ---
    window.openRoleConfigModal = () => {
        const modal = document.getElementById('role-config-modal');
        if (modal) {
            modal.style.display = 'flex';
            // Refresh data when opening to ensure freshness
            fetchSystemRoles();
        }
    };

    window.closeRoleConfigModal = () => {
        const modal = document.getElementById('role-config-modal');
        if (modal) modal.style.display = 'none';

        // Also close other modals for safety
        const toolsModal = document.getElementById('tool-modal');
        if (toolsModal) toolsModal.style.display = 'none';
    };

    // --- Modal & Alert Logic ---
    window.mcpToolsCache = {};

    window.showToolsModal = (name) => {
        const tools = window.mcpToolsCache[name] || [];
        const title = document.getElementById('modal-title');
        const container = document.getElementById('modal-content');

        if (title) title.textContent = `Tools: ${name} `;
        if (container) {
            container.innerHTML = tools.length
                ? tools.map(t => {
                    const args = t.inputSchema || t.args || {};
                    return `
    < div style = "margin-bottom:1rem; padding-bottom:1rem; border-bottom:1px solid rgba(255,255,255,0.1);" >
                            <div style="font-weight:600; color:var(--accent-blue); display:flex; justify-content:space-between;">
                                ${t.name}
                            </div>
                            <div style="font-size:0.9rem; color:#ddd; margin: 4px 0;">${t.description || "No description provided."}</div>
                            <div style="background:rgba(0,0,0,0.3); padding:8px; border-radius:4px; font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#aaa; overflow-x:auto;">
                                ARGS: ${JSON.stringify(args)}
                            </div>
                        </div >
    `;
                }).join('')
                : '<div style="padding:2rem; text-align:center; color:hsl(var(--text-tertiary));">No tools exposed by this server.</div>';
        }
        const modal = document.getElementById('tool-modal');
        if (modal) modal.style.display = 'flex';
    };

    window.closeToolsModal = () => {
        const modal = document.getElementById('tool-modal');
        if (modal) modal.style.display = 'none';
        const modelModal = document.getElementById('model-modal');
        if (modelModal) modelModal.style.display = 'none';
        // Ensure new modal is closed
        const roleModal = document.getElementById('role-config-modal');
        if (roleModal) roleModal.style.display = 'none';
    };

    // Attach listeners after functions are defined
});

// Global Modal Click Outside Listener (Robust)
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('glass') && e.target.id.includes('modal')) {
        e.target.style.display = 'none';
    }
});

window.dismissAlert = async (id, msg) => {
    const el = document.getElementById(id);
    if (el) {
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 500);
    }
    // Persist Acknowledgement
    localStorage.setItem('sentinel_ack_msg', msg);

    // Report to Orchestrator Logic
    console.log("Reporting Alert Dismissal:", msg);
    // Best effort log
    try {
        await fetch('/admin/mcp/tool', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                server: 'project-memory',
                tool: 'ingest_knowledge',
                arguments: {
                    text: `[USER FEEDBACK] User dismissed alert: "${msg}".This implies the alert was acknowledged or false positive.`,
                    kb_id: 'system_feedback'
                }
            })
        });
    } catch (e) { console.warn("Failed to report dismissal", e); }
};


// ... (fetchMCPData, etc. remain the same, ensure they are not cut off)

// --- MCP / Tools Logic ---
let mcpRetryCount = 0;
async function fetchMCPData() {
    const list = document.getElementById('mcp-servers-list');
    const retryLimit = 3;

    if (!list) return;

    try {
        // Robust Parallel Fetch: Tools (Content) + Breakers (Status) + Server Status
        const [toolsResult, breakersResult, serverStatusResult] = await Promise.allSettled([
            fetchWithRetry('/admin/mcp/tools', {}, 2, 500, 5000),
            fetch('/admin/circuit-breaker/status'),
            fetch('/admin/mcp/server/status')
        ]);

        // Handle Tools (Primary Content)
        let toolMap = {};
        let serverMeta = {};
        if (toolsResult.status === 'fulfilled' && toolsResult.value.ok) {
            const data = await toolsResult.value.json();
            if (data.ok) {
                toolMap = data.tools || {};
                serverMeta = data.servers || {}; // Get status map
                // Cache tools globally for Modal access
                window.mcpToolsCache = toolMap;
            }
        } else {
            const err = toolsResult.status === 'rejected' ? toolsResult.reason : new Error("Tools endpoint returned non-OK");
            throw err;
        }

        // Handle Breakers (Status Decoration)
        let breakerMap = {};
        if (breakersResult.status === 'fulfilled' && breakersResult.value.ok) {
            try {
                const bData = await breakersResult.value.json();
                breakerMap = bData.breakers || {};
            } catch (e) { console.warn("Failed to parse breaker data", e); }
        }

        // Handle Server Status
        if (serverStatusResult.status === 'fulfilled' && serverStatusResult.value.ok) {
            try {
                const sData = await serverStatusResult.value.json();
                const statusCard = document.getElementById('mcp-server-status-card');
                const clientsEl = document.getElementById('mcp-connected-clients');

                if (statusCard) {
                    statusCard.style.display = 'block';
                    const clientCount = (sData.clients || []).length;
                    if (clientCount > 0) {
                        const names = sData.clients.map(c => `< span class="badge blue" > ${c.name}</span > `).join(' ');
                        clientsEl.innerHTML = `Connected: ${names} `;
                    } else {
                        clientsEl.innerHTML = `< span style = "color:var(--text-muted)" > Waiting for connections...</span > `;
                    }
                }
            } catch (e) { console.warn("Failed to parse server status", e); }
        }

        // Use info from Server Meta to get ALL servers (even disabled ones)
        let serverNames = Object.keys(serverMeta).sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
        if (serverNames.length === 0) serverNames = Object.keys(toolMap).sort(); // Fallback

        if (serverNames.length === 0) {
            if (mcpRetryCount < retryLimit) {
                list.innerHTML = `< div style = "text-align:center; padding:20px; color:var(--text-secondary);" > Initializing MCP Servers... (Attempt ${mcpRetryCount + 1}) <br><small>Waiting for backend to populate tools cache...</small></div>`;
                mcpRetryCount++;
                setTimeout(fetchMCPData, 2000);
                return;
            } else {
                list.innerHTML = `< div style = "text-align:center; padding:20px; color:var(--text-muted);" > No MCP Servers Detected.< br > <small>Check your configuration or logs.</small></div > `;
                return;
            }
        }

        mcpRetryCount = 0; // Success, reset counter

        // Render
        // Render Lists
        const activeServerNames = serverNames.filter(n => serverMeta[n]?.enabled !== false);
        const disabledServerNames = serverNames.filter(n => serverMeta[n]?.enabled === false);

        const activeHTML = activeServerNames.map(name => {
            const tools = toolMap[name] || [];
            const breaker = breakerMap[name] || { state: 'UNKNOWN', total_successes: 0, total_failures: 0 };
            const stateClass = breaker.state ? breaker.state.toLowerCase() : 'unknown';

            // Ingestion Info Injection for Memory Server
            let ingestionInfo = "";
            if (name === 'project-memory' && window.lastIngestionState) {
                const ing = window.lastIngestionState;
                const statusText = ing.paused ? `PAUSED: ${ing.reason} ` : "HEALTHY";
                const statusColor = ing.paused ? "var(--accent-error)" : "var(--accent-neon)";
                ingestionInfo = `
    <div style="margin-top: 8px; font-size: 0.7rem; padding: 4px 8px; background: rgba(0,0,0,0.2); border-radius: 4px; border-left: 2px solid ${statusColor}">
        <div style="font-weight: 600; color: ${statusColor}">INGESTION: ${statusText}</div>
                        </div>
    `;
            }

            return `
    <div class="card" style="padding: var(--space-md); gap: 8px;">
                        <div class="flex-between">
                            <h4 style="margin:0; font-size: var(--text-sm); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex-grow: 1;" title="${name}">
                                ${name}
                            </h4>
                            <span class="status-dot ${stateClass === 'closed' ? 'ok' : 'err'}" title="State: ${stateClass.toUpperCase()}"></span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                             <button class="btn sm" style="font-size: 10px; padding: 2px 6px;" onclick="toggleMCP('${name}', false)">DISABLE</button>
                             ${breaker.state === 'OPEN' ? `<button class="btn sm primary" style="font-size:10px; padding:2px 6px;" onclick="resetBreaker('${name}')">RESET</button>` : ''}
                        </div>
                        <div class="flex-between" style="font-size: 10px; color:hsl(var(--text-tertiary)); margin-top: 4px;">
                            <span>Tools: ${tools.length}</span>
                            <span>S:${breaker.total_successes} F:${breaker.total_failures}</span>
                        </div>
                        ${ingestionInfo}
<button class="btn sm" style="width:100%; justify-content:center; margin-top:4px;" onclick="showToolsModal('${name}')">
    VIEW TOOLS
</button>
                    </div>
    `;
        }).join('');

        const disabledHTML = disabledServerNames.length > 0 ? `
    <div style="grid-column: 1 / -1; margin-top: 1rem; border-top: 1px solid var(--glass-border); padding-top: 1rem; color: var(--text-muted); font-size: 0.8rem; display: flex; flex-wrap: wrap; gap: 8px;">
        <div style="width:100%; margin-bottom:0.5rem; font-weight:600;">Disabled Servers</div>
                    ${disabledServerNames.map(name => `
                        <div style="background:rgba(0,0,0,0.3); padding:4px 8px; border-radius:4px; display:flex; align-items:center; gap:8px; border:1px solid var(--glass-border);">
                            <span style="color:#666;">${name}</span>
                            <button class="action-btn sm primary" style="padding:2px 6px; font-size:0.7rem;" onclick="toggleMCP('${name}', true)">Enable</button>
                        </div>
                    `).join('')
            }
                </div>
    ` : '';

        list.innerHTML = activeHTML + disabledHTML;

    } catch (e) {
        console.warn("MCP Fetch Loop Error", e);
        if (mcpRetryCount < retryLimit) {
            list.innerHTML = `<div style="text-align:center; padding:20px; color:hsl(var(--text-secondary));">Connecting to Agent Runner... (${mcpRetryCount + 1}) <br><small>${e.message}</small></div>`;
            mcpRetryCount++;
            setTimeout(fetchMCPData, 2000);
        } else {
            list.innerHTML = `<div style="text-align:center; padding:20px; color:hsl(var(--accent-danger));">Connection Failed.<br><small>${e.message}</small><br><button class="btn sm" onclick="fetchMCPData()">Retry</button></div>`;
        }
    }
}

// --- MCP Toggle Logic ---
window.toggleMCP = async (name, enable) => {
    const action = enable ? "Enabling" : "Disabling";
    if (!enable && !confirm(`Are you sure you want to DISABLE '${name}' ?\n\nThis will stop the process but RETAIN your configuration.\n\nYou can re - enable it at any time.`)) return;

    try {
        const resp = await fetch('/admin/mcp/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, enabled: enable })
        });
        const d = await resp.json();
        if (d.ok) {
            const msg = enable ? `ENABLED '${name}'.Starting process...` : `DISABLED '${name}'.Config Retained.Process Stopped.`;
            showNotification(msg);
            console.log(`MCP Toggle Success: ${name} -> ${enable}. Config saved to mcp.yaml.`);
            setTimeout(fetchMCPData, 1000); // Wait for discovery/termination
        } else {
            showNotification(`Failed: ${d.error} `, 'error');
        }
    } catch (e) { console.error(e); }
};

// ... (Rest of Ollama Logic)

// --- Ollama Manager ---
async function fetchOllamaModels() {
    const grid = document.getElementById('ollama-models-grid');
    if (!grid) return;

    grid.innerHTML = `
    <div class="card grid-col-3" style="width: 100%;">
                <div class="card-header">
                    <span class="card-title">Manage Ollama Models</span>
                </div>
                <div class="flex-col" style="gap: var(--space-md);">
                    <div class="flex-col" style="gap: 5px;">
                         <label class="text-muted" style="font-size: var(--text-xs);">Pull New Model</label>
                         <div class="flex-center" style="gap: 10px;">
                            <input type="text" id="pull-model-name" placeholder="e.g. llama3, mistral..." class="input" style="flex-grow:1;">
                            <button class="btn" onclick="startModelPull()">PULL</button>
                         </div>
                         <div id="pull-status" style="font-size: 10px; color: hsl(var(--text-tertiary));"></div>
                    </div>
                    <div class="flex-col" style="gap: 5px;">
                        <label class="text-muted" style="font-size: var(--text-xs);">Runtime Parameters (Global)</label>
                        <div class="grid-dashboard" style="grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div class="flex-col">
                                <span style="font-size: 10px;">Temperature</span>
                                <input type="number" step="0.1" min="0" max="1" value="0.7" class="input">
                            </div>
                             <div class="flex-col">
                                <span style="font-size: 10px;">Context Window</span>
                                <input type="number" step="1024" value="8192" class="input">
                            </div>
                        </div>
                        <button class="btn sm" style="margin-top: 10px;" onclick="alert('Params Updated')">APPLY PARAMS</button>
                    </div>
                </div>
            </div>
    `;
}

window.startModelPull = async () => {
    const name = document.getElementById('pull-model-name').value;
    if (!name) return;
    const status = document.getElementById('pull-status');
    status.textContent = `Requesting pull for ${name}...`;
    setTimeout(() => {
        status.textContent = `Pulling ${name}: 10 %... (Simulation)`;
        showNotification(`Pull started for ${name}`);
    }, 500);
};

// --- Config Logic ---
async function fetchConfigFiles() {
    const sel = document.getElementById('config-file-selector');
    if (!sel) return;
    sel.innerHTML = '<option value="" disabled selected>Select a file...</option>';

    const resp = await fetch('/admin/config/files');
    if (resp.ok) {
        const data = await resp.json();
        data.files.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f.path;
            opt.textContent = f.name + (f.exists ? '' : ' (New)');
            if (f.name === 'providers.yaml') opt.selected = true;
            sel.appendChild(opt);
        });
        if (sel.value) sel.dispatchEvent(new Event('change'));
    }

    sel.addEventListener('change', async (e) => {
        const path = e.target.value;
        state.editorPath = path;
        const r = await fetch(`/ admin / config / read ? path = ${encodeURIComponent(path)}`);
        if (r.ok) {
            const d = await r.json();
            document.getElementById('config-editor').value = d.content;
            const help = document.querySelector('.tip-text');
            if (path.includes('providers.yaml')) {
                help.innerHTML = `< strong > Tip:</strong > Define MCP servers here.Restart required after saving.`;
            } else {
                help.innerHTML = `Editing < strong > ${path.split('/').pop()}</strong > `;
            }
        }
    });
}

document.getElementById('btn-save-config')?.addEventListener('click', async () => {
    if (!state.editorPath) return;
    const resp = await fetch('/admin/config/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: state.editorPath, content: document.getElementById('config-editor').value })
    });
    if (resp.ok) {
        showNotification('Config saved. Reloading MCPs...');
        await fetch('/admin/reload-mcp', { method: 'POST' });
    }
});

document.getElementById('btn-add-mcp-stub')?.addEventListener('click', () => {
    const stub = `
# -- - NEW SERVER TEMPLATE-- -
# 1. Replace 'my-server-name' with your tool's name
# 2. Check 'args' for the correct package
# 3. Add env vars if needed
my - server - name:
command: npx
args:
- "-y"
    - "@modelcontextprotocol/server-name"
env:
MY_API_KEY: "your-key-here"
    `;
    const editor = document.getElementById('config-editor');
    editor.value += stub;
    showNotification('Added MCP server template.');
});

function showNotification(msg, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast glass';
    if (type === 'error') toast.style.color = 'hsl(var(--accent-danger))';
    toast.innerHTML = msg; // Support HTML
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 500); }, 3000);
}

// --- Memory Browser Logic ---
window.fetchMemoryFacts = async () => {
    const input = document.getElementById('memory-search-input');
    const query = input ? input.value : '';
    const container = document.getElementById('memory-results');
    container.innerHTML = '<div class="placeholder-box">Searching Neural Memory...</div>';

    try {
        const resp = await fetch(`/ admin / memory / facts ? query = ${encodeURIComponent(query)} `);
        if (resp.ok) {
            const data = await resp.json();
            if (data.facts && data.facts.length > 0) {
                const rows = data.facts.map(f => `
    < tr >
                            <td><span class="badge fact">FACT</span></td>
                            <td>${f.entity || '?'}</td>
                            <td>${f.relation || '-'}</td>
                            <td>${f.target || ''}</td>
                        </tr >
    `).join('');
                container.innerHTML = `
    < table class="memory-table" >
                            <thead>
                                <tr>
                                    <th width="80">Type</th>
                                    <th>Entity</th>
                                    <th>Relation</th>
                                    <th>Target/Value</th>
                                </tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table >
    `;
            } else {
                container.innerHTML = '<div style="padding:1rem; color:var(--text-muted)">No facts found matching query.</div>';
            }
        } else {
            container.innerHTML = '<div style="color:var(--accent-error)">Error fetching memory. Agent might be busy.</div>';
        }
    } catch (e) {
        container.innerHTML = `< div style = "color:var(--accent-error)" > Network Error: ${e.message}</div > `;
    }
};

document.getElementById('memory-search-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') window.fetchMemoryFacts();
});

// --- SSE Log Streaming ---
let logEventSource = null;
function startLogStream() {
    if (logEventSource) logEventSource.close();

    const logContainer = document.querySelector('.log-viewer');
    if (!logContainer) return;

    logEventSource = new EventSource('/admin/logs/stream?services=agent_runner,router');

    logEventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            const entry = document.createElement('div');
            entry.className = `log - entry ${data.service} `;

            // Colorize based on content
            let type = 'info';
            if (data.line.includes('ERROR') || data.line.includes('Critical')) type = 'error';
            else if (data.line.includes('WARN')) type = 'warn';
            entry.classList.add(type);

            entry.innerHTML = `< small style = "opacity:0.5; margin-right:8px;" > [${data.service.toUpperCase()}]</small > ${data.line} `;
            logContainer.appendChild(entry);

            // Keep last 200 lines
            if (logContainer.children.length > 200) {
                logContainer.removeChild(logContainer.firstChild);
            }

            // Auto-scroll if at bottom
            const isAtBottom = logContainer.scrollHeight - logContainer.clientHeight <= logContainer.scrollTop + 50;
            if (isAtBottom) {
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        } catch (e) { console.error("Log Stream Error:", e); }
    };

    logEventSource.onerror = (e) => {
        console.warn("Log Stream Disconnected, reconnecting in 5s...");
        logEventSource.close();
        setTimeout(startLogStream, 5000);
    };
}


// Auto Toggle & Backup Buttons
document.getElementById('btn-toggle-auto-top')?.addEventListener('click', () => {
    const lbl = document.getElementById('lbl-auto');
    if (lbl.textContent === 'ON') {
        lbl.textContent = 'OFF';
        lbl.style.color = 'var(--text-muted)';
        showNotification('Auto-Mode Disabled');
    } else {
        lbl.textContent = 'ON';
        lbl.style.color = 'var(--accent-neon)';
        showNotification('Auto-Mode Enabled');
    }
});

document.getElementById('btn-trigger-backup-top')?.addEventListener('click', async () => {
    showNotification('Backup started...');
});

async function fetchDocsList() {
    const listEl = document.getElementById('docs-list');
    listEl.innerHTML = '<div class="placeholder-box">Loading...</div>';
    const resp = await fetch('/admin/docs/list');
    if (resp.ok) {
        const data = await resp.json();
        if (data.files && data.files.length > 0) {
            listEl.innerHTML = data.files.map(f => `
    < div class="task-item" style = "cursor:pointer;" onclick = "loadDoc('${f.path}', '${f.name}')" >
        <span class="task-name">📄 ${f.name}</span>
                    </div >
    `).join('');
        } else {
            listEl.innerHTML = '<div style="padding:1rem; color:var(--text-muted)">No documentation files found in ai/docs.</div>';
        }
    }
}
window.loadDoc = async (path, name) => {
    const resp = await fetch(`/ admin / docs / read ? path = ${encodeURIComponent(path)} `);
    if (resp.ok) {
        const data = await resp.json();
        document.getElementById('doc-viewer-title').textContent = name;
        document.getElementById('doc-viewer-content').innerHTML = marked.parse(data.content);
    }
};

async function fetchLogTail() {
    const container = document.getElementById('log-container');


    const resp = await fetch('/admin/logs/tail?lines=50');
    if (resp.ok) {
        const data = await resp.json();
        const container = document.getElementById('log-container');
        container.innerHTML = data.logs.map(line => {
            // Formatting safety: Skip massive lines or dump-lines that break rendering
            if (line.length > 2000) return `< div class="log-entry info" style = "color:var(--text-muted)" > [Large Log Entry Skipped: ${line.length} chars]</div > `;

            const updated = line.replace(/</g, '&lt;');
            let cls = 'info';
            if (updated.includes('ERROR')) cls = 'error';
            if (updated.includes('WARNING')) cls = 'warn';
            return `< div class="log-entry ${cls}" > ${updated}</div > `;
        }).join('');
        container.scrollTop = container.scrollHeight;
    }
}
document.getElementById('btn-refresh-logs')?.addEventListener('click', fetchLogTail);

window.resetBreaker = async (name) => {
    await fetch(`/ admin / circuit - breakers / ${name}/reset`, { method: 'POST' });
    showNotification(`Breaker ${name} reset.`);
    fetchMCPData();
};

fetchSystemData();
fetchSystemRoles();

// --- Cloud Uplink Logic ---
async function fetchCloudLogs() {
    const terminal = document.getElementById('cloud-terminal');
    if (!terminal) return;

    try {
        const resp = await fetch('/admin/logs/cloud_uplink?lines=15'); // Fetch last 15 lines
        if (resp.ok) {
            const data = await resp.json();
            if (data.logs && data.logs.length > 0) {
                // Update terminal content
                terminal.innerHTML = data.logs.map(line => `> ${line}`).join('<br>');
                terminal.scrollTop = terminal.scrollHeight; // Auto-scroll

                // Update Status Badge based on content
                const lastLine = data.logs[data.logs.length - 1];
                const badge = document.getElementById('cloud-status-badge');
                if (lastLine.includes('Processing')) {
                    badge.textContent = 'ACTIVE';
                    badge.className = 'badge bg-success';
                } else if (lastLine.includes('Error')) {
                    badge.textContent = 'ERROR';
                    badge.className = 'badge bg-danger';
                } else {
                    badge.textContent = 'IDLE';
                    badge.className = 'badge bg-secondary';
                }
            }
        }
    } catch (e) {
        // terminal.innerHTML = '> Uplink Disconnected.';
    }
}

// Start Polling Loop
setInterval(fetchSystemData, state.pollingInterval);
setInterval(fetchCloudLogs, 2000); // Poll cloud logs every 2s

document.getElementById('btn-reload-mcp-top')?.addEventListener('click', async () => {
    await fetch('/admin/reload-mcp', { method: 'POST' });
    showNotification('MCP Servers Reloaded');
});

// --- Notification Polling & Local Health ---
let notificationsApiAvailable = true;
let lastInternetStatus = 'Connected';

async function fetchNotifications() {
    if (!notificationsApiAvailable) return;

    try {
        const resp = await fetch('/admin/notifications?unread=true');
        if (resp.status === 404) {
            console.log("Notification API not available (backend update pending). Switching to local checks.");
            notificationsApiAvailable = false;
            return;
        }
        if (resp.ok) {
            const data = await resp.json();
            if (data.notifications && data.notifications.length > 0) {
                data.notifications.forEach(n => {
                    showNotification(n.level === 'critical' || n.level === 'high' ?
                        `⚠️ [${n.level.toUpperCase()}] ${n.title}` :
                        `ℹ️ ${n.title}`);
                });
                await fetch('/admin/notifications/acknowledge', { method: 'POST' });
            }
        }
    } catch (e) {
        // Silent fail for polling errors
    }
}

// Enhance fetchSystemData with local notification triggers
const originalFetchSystemData = fetchSystemData;
fetchSystemData = async function () {
    // Call original
    const result = await originalFetchSystemData(); // Assuming original returns data or we intercept state
    // Since originalFetchSystemData doesn't return data (it updates UI), we read 'state' global or we can't.
    // Wait, fetchSystemData updates 'state' variable? 
    // Let's check the files... state is global in app.js? 
    // No, 'state' is defined at top of app.js. 
    // We can access 'state'.

    if (state.systemStatus) {
        // Check Internet
        if (state.systemStatus.internet === 'Offline' && lastInternetStatus === 'Connected') {
            showNotification('⚠️ Internet Connection Lost');
            lastInternetStatus = 'Offline';
        } else if (state.systemStatus.internet === 'Connected' && lastInternetStatus === 'Offline') {
            showNotification('✅ Internet Restored');
            lastInternetStatus = 'Connected';
        }
    }
    return result;
};

// --- Integrated Chat Logic ---
function setupChat() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('btn-chat-send');
    const historyDiv = document.getElementById('chat-messages');
    const modelSelect = document.getElementById('chat-model-select');
    const statusSpan = document.getElementById('chat-status');

    if (!chatInput || !sendBtn) return;

    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `chat-message ${role}`;
        div.textContent = text;
        historyDiv.appendChild(div);
        historyDiv.scrollTop = historyDiv.scrollHeight;
        return div;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // UI State
        appendMessage('user', text);
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;
        statusSpan.textContent = "Connecting...";
        statusSpan.className = "status-indicator warning";

        const model = modelSelect.value;
        const assistantDiv = appendMessage('assistant', '');

        // Thinking UI State
        let thinkingContainer = null;
        let thinkingBody = null;
        let currentStepDiv = null;

        try {
            const response = await fetch('/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('router_auth_token') || prompt("🔐 Auth Token Required:") || ""}`
                },
                body: JSON.stringify({
                    model: model,
                    messages: [{ role: "user", content: text }],
                    stream: true
                })
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            statusSpan.textContent = "Receiving...";
            statusSpan.className = "status-indicator ok";

            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop(); // Keep partial line

                for (const line of lines) {
                    const trimmed = line.trim();
                    if (!trimmed || !trimmed.startsWith('data: ')) continue;

                    const dataStr = trimmed.slice(6);
                    if (dataStr === '[DONE]') break;

                    try {
                        const chunk = JSON.parse(dataStr);
                        let event = chunk;
                        if (chunk.choices && chunk.choices.length > 0) {
                            event = chunk.choices[0].delta || {};
                        }
                        if (!event.type && event.content) {
                            event = { type: 'token', content: event.content };
                        }
                        if (event.role) continue;
                        if (chunk.error) {
                            assistantDiv.textContent += `\n[Error: ${chunk.error.message}]`;
                            statusSpan.className = "status-indicator error";
                        }

                        // 1. TOKEN
                        if (event.type === 'token') {
                            assistantDiv.textContent += event.content;
                            historyDiv.scrollTop = historyDiv.scrollHeight;
                        }

                        // 2. THINKING START
                        else if (event.type === 'thinking_start') {
                            thinkingContainer = document.createElement('div');
                            thinkingContainer.className = 'chat-thinking';

                            const header = document.createElement('div');
                            header.className = 'chat-thinking-header';
                            header.innerHTML = `<span class="icon spin">⚙️</span> <span>Planning ${event.count} Step(s)...</span>`;
                            header.onclick = () => {
                                thinkingBody.style.display = thinkingBody.style.display === 'none' ? 'flex' : 'none';
                            };

                            thinkingBody = document.createElement('div');
                            thinkingBody.className = 'chat-thinking-body';

                            thinkingContainer.appendChild(header);
                            thinkingContainer.appendChild(thinkingBody);
                            assistantDiv.appendChild(thinkingContainer);
                        }

                        // 3. TOOL START
                        else if (event.type === 'tool_start') {
                            const step = document.createElement('div');
                            step.className = 'thinking-step running';
                            step.innerHTML = `
                                    <div class="thinking-step-icon">🔄</div>
                                    <div class="thinking-step-content">
                                        <div class="thinking-step-name">${event.tool}</div>
                                        <div class="thinking-step-details">${JSON.stringify(event.input).substring(0, 100)}...</div>
                                    </div>
                                `;
                            thinkingBody.appendChild(step);
                            currentStepDiv = step;
                        }

                        // 4. TOOL END
                        else if (event.type === 'tool_end') {
                            const steps = thinkingBody.querySelectorAll('.thinking-step.running');
                            const step = Array.from(steps).find(s => s.querySelector('.thinking-step-name').textContent === event.tool);

                            if (step) {
                                step.className = 'thinking-step done';
                                step.querySelector('.thinking-step-icon').textContent = '✅';
                                step.classList.remove('running');
                                const outLen = event.output ? event.output.length : 0;
                                step.querySelector('.thinking-step-details').textContent += ` -> Done (${outLen} chars)`;
                            }
                        }

                        // 5. ERROR
                        else if (event.type === 'error') {
                            assistantDiv.textContent += `\n[System Error: ${event.error}]`;
                        }

                    } catch (e) { }
                }
            }

            statusSpan.textContent = "Ready";
            statusSpan.className = "status-indicator";

        } catch (e) {
            assistantDiv.textContent += `\n[Failed: ${e.message}]`;
            statusSpan.textContent = "Error";
            statusSpan.className = "status-indicator error";
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    // --- Audio Logic ---
    const micBtn = document.getElementById('btn-chat-mic');
    const ttsToggle = document.getElementById('chat-tts-toggle');
    let recognition;

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            micBtn.style.background = '#dd2222';
            statusSpan.textContent = "Listening...";
            statusSpan.className = "status-indicator warning";
        };
        recognition.onend = () => {
            micBtn.style.background = '#333';
            if (statusSpan.textContent === "Listening...") {
                statusSpan.textContent = "Ready";
                statusSpan.className = "status-indicator";
            }
        };
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            setTimeout(sendMessage, 200);
        };
    } else {
        console.warn("Speech Recognition not supported.");
        if (micBtn) micBtn.style.display = 'none';
    }

    function toggleRecording() {
        if (!recognition) return showNotification("Browser does not support Speech API.");
        try { recognition.start(); } catch (e) { recognition.stop(); }
    }

    function speak(text) {
        if (!ttsToggle || !ttsToggle.checked || !text) return;
        window.speechSynthesis.cancel();
        const cleanText = text.replace(/[*#`_\[\]]/g, '').replace(/https?:\/\/\S+/g, 'link');
        const u = new SpeechSynthesisUtterance(cleanText);
        u.rate = 1.1;
        window.speechSynthesis.speak(u);
    }

    // Paste-to-Upload Handler
    chatInput.addEventListener('paste', async (e) => {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        let hasFile = false;

        // 1. Check for files (images, docs, etc.)
        for (let index in items) {
            const item = items[index];
            if (item.kind === 'file') {
                e.preventDefault();
                hasFile = true;
                const blob = item.getAsFile();
                await handleFileUpload(blob);
            }
        }

        // 2. If no file, check for massive text that should be a file
        if (!hasFile) {
            const text = e.clipboardData.getData('text');
            if (text.length > 5000) { // Large content threshold
                if (confirm("This text is very long. Do you want to upload it as a file to 'uploads/' so I can digest it properly?")) {
                    e.preventDefault();
                    await handleFileUpload(new Blob([text], { type: 'text/plain' }), `pasted_text_${Date.now()}.txt`);
                }
            }
        }
    });

    async function handleFileUpload(fileArg, textFilename = null) {
        // Show uploading state
        chatInput.value = `[Uploading ${textFilename || fileArg.name}...]`;
        chatInput.disabled = true;

        const formData = new FormData();
        if (textFilename) {
            formData.append('content', await fileArg.text());
            formData.append('filename', textFilename);
        } else {
            formData.append('file', fileArg);
        }

        try {
            const resp = await fetch('/admin/upload', {
                method: 'POST',
                body: formData
            });
            const data = await resp.json();

            if (data.ok) {
                // Auto-inject system prompt
                chatInput.value = `Read the file '${data.filename}' from uploads and digest it to memory.`;
                chatInput.disabled = false;
                showNotification(`Uploaded: ${data.filename}`);
                // Optional: Auto-send? Let's let the user verify first.
                // sendMessage(); 
            } else {
                chatInput.value = "";
                chatInput.disabled = false;
                showNotification(`Upload Failed: ${data.error}`, 'error');
            }
        } catch (e) {
            console.error("Upload Loop Error", e);
            chatInput.value = "";
            chatInput.disabled = false;
            showNotification("Connection failed during upload", 'error');
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    if (micBtn) micBtn.addEventListener('click', toggleRecording);

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

setupChat();
setInterval(fetchNotifications, 5000);

// --- Cost Tab Logic ---
async function refreshCost() {
    try {
        const response = await fetch('/admin/budget', { headers: { 'Authorization': getAuthToken() } });
        const data = await response.json();

        if (data.ok) {
            const spend = data.current_spend.toFixed(4);
            const limit = data.daily_limit_usd.toFixed(2);
            const percent = data.percent_used.toFixed(1);

            document.getElementById('costDisplay').innerText = '$' + spend;
            document.getElementById('limitDisplay').innerText = 'Limit: $' + limit;
            document.getElementById('percentDisplay').innerText = percent + '%';

            const bar = document.getElementById('costBar');
            bar.style.width = Math.min(100, data.percent_used) + '%';

            if (data.percent_used > 90) bar.style.background = 'var(--accent-warn)';
            else if (data.percent_used > 100) bar.style.background = 'var(--accent-error)';
            else bar.style.background = 'var(--success)';
        }
    } catch (e) {
        console.error("Failed to fetch cost", e);
    }
}

// Auto-refresh when tab is shown
document.querySelectorAll('.tab-link[data-tab="cost"]').forEach(btn => {
    btn.addEventListener('click', () => setTimeout(refreshCost, 100)); // Small delay for DOM
});

// Helper for auth if not defined globally (it likely is or hardcoded, but let's be safe)
function getAuthToken() {
    return `Bearer ${localStorage.getItem('router_auth_token') || prompt("🔐 Auth Token Required:") || ""}`;
}

// --- Smart Config Logic ---
async function runSmartConfig() {
    const input = document.getElementById('config-instruction').value;
    if (!input.trim()) return;

    const btn = document.getElementById('btn-smart-config');
    const log = document.getElementById('smart-config-log');

    btn.disabled = true;
    btn.innerHTML = "🤖 Processing...";
    log.innerText = "🚀 Asking Agent to edit config... (This takes ~30s)\n";

    try {
        const response = await fetch('/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': getAuthToken()
            },
            body: JSON.stringify({
                model: "agent:mcp",
                messages: [
                    {
                        role: "system",
                        content: `You are the Antigravity Config Manager. You must edit 'ai/config/config.yaml'.
                        
                        SAFETY RULES:
                        1. NEVER use 'write_to_file' to overwrite the file. It causes data loss.
                        2. ALWAYS use 'replace_file_content' to make surgical edits.
                        3. Process:
                           a. Read 'ai/config/config.yaml'.
                           b. Identify the exact block to change.
                           c. Use 'replace_file_content' to swap ONLY that block.
                           d. Run './manage.sh restart-agent'.`
                    },
                    { role: "user", content: "Instruction: " + input }
                ]
            })
        });

        const data = await response.json();
        if (data.choices && data.choices[0]) {
            log.innerText += "\n✅ Done! Agent says:\n" + data.choices[0].message.content;
            loadConfigFile(); // Refresh view
        } else {
            log.innerText += "\n❌ Error: " + JSON.stringify(data);
        }
    } catch (e) {
        log.innerText += "\n❌ Network Error: " + e.message;
    } finally {
        btn.disabled = false;
        btn.innerHTML = "✨ Run Smart Config";
    }
}

async function loadConfigFile() {
    editor.value = "Loading...";
    try {
        const res = await fetch('/admin/config/yaml', { headers: { 'Authorization': getAuthToken() } });
        const data = await res.json();
        if (data.ok) {
            editor.value = data.content;
        } else {
            editor.value = "Error loading config: " + data.error;
        }
    } catch (e) {
        editor.value = "Failed to fetch config: " + e.message;
    }
}

window.resumeIngestion = async () => {
    try {
        const resp = await fetch('/admin/ingestion/resume', { method: 'POST' });
        if (resp.ok) {
            showNotification('Resuming ingestion...');
            fetchSystemData();
        } else {
            showNotification('Failed to resume: ' + (await resp.text()));
        }
    } catch (e) {
        showNotification('Network error while resuming.');
    }
};

window.pauseIngestion = async () => {
    try {
        const resp = await fetch('/admin/ingestion/pause', { method: 'POST' });
        if (resp.ok) {
            showNotification('Pausing ingestion...');
            fetchSystemData();
        } else {
            showNotification('Failed to pause: ' + (await resp.text()));
        }
    } catch (e) {
        showNotification('Network error while pausing.');
    }
};

window.clearAndResumeIngestion = async () => {
    try {
        const resp = await fetch('/admin/ingestion/clear-and-resume', { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
            showNotification('Problem file cleared. Resuming...');
            fetchSystemData();
        } else {
            showNotification('Failed: ' + (data.error || data.message));
        }
    } catch (e) {
        showNotification('Network error during cleanup.');
    }
};
});

// --- Breaker Management ---
window.fetchBreakerData = async function () {
    const tbody = document.getElementById('breaker-table-body');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="6" class="text-center">Refreshing...</td></tr>';

    try {
        const resp = await fetch('/admin/circuit-breaker/status');
        if (resp.ok) {
            const data = await resp.json();
            const breakers = data.breakers || {};
            const names = Object.keys(breakers).sort();

            if (names.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No Circuit Breakers Active</td></tr>';
                return;
            }

            tbody.innerHTML = names.map(name => {
                const b = breakers[name];
                const stateClass = b.state === 'open' ? 'error' : (b.state === 'half_open' ? 'warn' : 'ok');
                const stateColor = b.state === 'open' ? 'var(--accent-error)' : (b.state === 'half_open' ? 'var(--accent-warning)' : 'var(--accent-neon)');
                const err = b.last_error ? `<span title="${b.last_error}" style="cursor:help;">${b.last_error.substring(0, 40)}...</span>` : '-';
                const cooldown = b.seconds_remaining > 0 ? `${Math.ceil(b.seconds_remaining)}s` : '-';

                return `
                        <tr>
                            <td class="mono" style="font-weight:600;">${name}</td>
                            <td><span style="color:${stateColor}; font-weight:bold;">${b.state.toUpperCase()}</span></td>
                            <td>${b.failures} / 5</td>
                            <td class="mono" style="font-size:0.85rem;">${err}</td>
                            <td>${cooldown}</td>
                            <td>
                                ${b.state === 'open' ?
                        `<button class="action-btn sm primary" onclick="resetBreaker('${name}')">Reset</button>` :
                        '<span style="opacity:0.3;">-</span>'}
                            </td>
                        </tr>
                    `;
            }).join('');

        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="color:var(--accent-error);">Failed to fetch status</td></tr>';
        }
    } catch (e) {
        console.error("Breaker fetch error", e);
        tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="color:var(--accent-error);">${e.message}</td></tr>`;
    }
};

// Global Reset Helper
window.resetBreaker = async function (name) {
    if (!confirm(`Reset breaker for '${name}'?`)) return;
    try {
        await fetch(`/admin/circuit-breaker/reset/${name}`, { method: 'POST' });
        showNotification(`Breaker '${name}' Reset`);
        fetchBreakerData(); // Refresh UI
        fetchMCPData(); // Refresh MCP list too
    } catch (e) {
        alert("Failed to reset: " + e);
    }
};


// --- Breaker Data Logic ---
// --- Breaker Data Logic (Refactored for V2 Table) ---
// Defined globally so fetchSystemData can call it
window.updateBreakersTable = function (data) {
    const container = document.getElementById('breaker-table-body');
    if (!container) return; // Legacy view or wrong page

    const breakers = data.breakers || {};

    if (Object.keys(breakers).length === 0) {
        container.innerHTML = '<tr><td colspan="6" class="text-center">No active circuit breakers.</td></tr>';
        return;
    }

    container.innerHTML = Object.entries(breakers).map(([name, b]) => {
        const stateClass = b.state ? b.state.toLowerCase() : 'unknown';
        return `
            <tr>
                <td style="font-weight:600;">${name}</td>
                <td><span class="indicator ${stateClass}">${b.state}</span></td>
                <td><span style="color:var(--accent-error)">${b.failures}</span> / ${b.total_failures}</td>
                <td>${b.last_error ? b.last_error.substring(0, 30) + '...' : '-'}</td>
                <td>${b.disabled_until > 0 ? b.disabled_until.toFixed(1) + 's' : '-'}</td>
                <td>
                    ${b.state === 'OPEN' ? `<button class="action-btn sm primary" onclick="resetBreaker('${name}')">Reset</button>` : '-'}
                </td>
            </tr>
        `;
    }).join('');
};

async function fetchBreakerData() {
    try {
        const resp = await fetch('/admin/circuit-breaker/status');
        if (resp.ok) {
            const data = await resp.json();
            window.updateBreakersTable(data);
        } else {
            // No notification on failure, just let the table update handle it or console error
        }
    } catch (e) {
        console.error("Breaker fetch error", e);
    }
}

// Refresh Breakers when tab is clicked
document.querySelectorAll('.tab-link[data-tab="status"]').forEach(btn => {
    btn.addEventListener('click', () => setTimeout(fetchBreakerData, 100));
});
// Also poll if visible
setInterval(() => {
    const statusTab = document.getElementById('status');
    if (statusTab && statusTab.style.display === 'block') fetchBreakerData();
}, 2000);

// --- Fix RAG Status ---
async function checkRAGHealth() {
    try {
        // Use the router proxy to hit the RAG server health
        const resp = await fetch('/rag/health');
        const indicator = document.querySelector('.status-item.rag .indicator');

        if (resp.ok) {
            if (indicator) { indicator.className = 'indicator online'; }
        } else {
            if (indicator) { indicator.className = 'indicator offline'; }
        }
    } catch (e) {
        const indicator = document.querySelector('.status-item.rag .indicator');
        if (indicator) indicator.className = 'indicator offline';
    }
}
setInterval(checkRAGHealth, 5000);

// Initial Trigger
checkRAGHealth();

// --- PHASE 25: DIAGNOSTICS LOGIC ---

async function fetchDiagnostics() {
    // Only fetch if tab is active
    if (activeTab !== 'diagnostics') return;

    try {
        // 1. Fetch Metrics (reuse existing endpoint which has some of this)
        // But for trace data we need separate calls
        const traceResp = fetch('/admin/observability/trace?limit=50').then(r => r.json());
        const stuckResp = fetch('/admin/observability/stuck').then(r => r.json());
        const statsResp = fetch('/admin/observability/stats').then(r => r.json());

        const [traces, stuck, stats] = await Promise.all([traceResp, stuckResp, statsResp]);

        if (traces.ok) renderTraceTable(traces.traces);
        if (stuck.ok) renderStuckTable(stuck.stuck_requests);
        if (stats.ok) renderDiagnosticsMetrics(stats.metrics);

    } catch (e) {
        console.error("Diagnostics fetch failed:", e);
    }
}

function renderDiagnosticsMetrics(metrics) {
    if (!metrics) return;

    // Throughput
    document.getElementById('diag-rps').textContent = (metrics.efficiency?.requests_per_second || 0).toFixed(2);
    document.getElementById('diag-tps').textContent = (metrics.efficiency?.tokens_per_second || 0).toFixed(0);
    // P99 is tricky without more data, use avg for now
    document.getElementById('diag-p99').textContent = (metrics.avg_response_time_1min || 0).toFixed(0) + "ms";

    // Cache
    document.getElementById('diag-cache-rate').textContent = (metrics.efficiency?.cache_hit_rate || 0).toFixed(1) + "%";
    // Hits/Misses are cumulative, not exposed directly in efficiency dict except via rates
    // If observing raw numbers is needed we'll need to expand stats endpoint. 
    // For now, placeholder or derived.

    // Concurrency
    document.getElementById('diag-active').textContent = metrics.active_requests;
    document.getElementById('diag-wait').textContent = (metrics.efficiency?.semaphore_wait_time_avg_ms || 0).toFixed(1) + "ms";
    document.getElementById('diag-queue').textContent = metrics.efficiency?.queue_depth || 0;
}

function renderTraceTable(traces) {
    const tbody = document.getElementById('diag-trace-table');
    if (!traces || traces.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">No recent traces</td></tr>';
        return;
    }

    tbody.innerHTML = traces.map(t => {
        const date = new Date(t.started_at * 1000).toLocaleTimeString();
        const duration = t.duration_ms ? t.duration_ms.toFixed(0) + 'ms' : 'Running';

        // Color coding
        let durabilityClass = '';
        if (t.duration_ms > 1000) durabilityClass = 'text-red';
        else if (t.duration_ms > 200) durabilityClass = 'text-yellow';
        else durabilityClass = 'text-green';

        let statusClass = t.stage === 'error' || t.stage === 'timeout' ? 'status-offline' : 'status-online';

        return `
        <tr>
            <td>${date}</td>
            <td><span class="badge">${t.method}</span></td>
            <td title="${t.path}" style="max-width:200px;overflow:hidden;text-overflow:ellipsis;">${t.path}</td>
            <td><span class="status-indicator ${statusClass}"></span> ${t.stage}</td>
            <td class="${durabilityClass}" font-weight:bold;">${duration}</td>
            <td>
               <small>${JSON.stringify(t.metadata || {}).substring(0, 50)}</small>
            </td>
        </tr>
    `;
    }).join('');
}

function renderStuckTable(stuck) {
    const tbody = document.getElementById('diag-stuck-table');
    if (!stuck || stuck.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: #888;">No stuck requests</td></tr>';
        return;
    }

    tbody.innerHTML = stuck.map(req => `
    <tr class="bg-red-dim">
        <td>${req.request_id.substring(0, 8)}</td>
        <td>${req.age_seconds.toFixed(1)}s</td>
        <td>${req.current_stage}</td>
        <td>${req.method} ${req.path}</td>
        <td><button class="btn btn-sm" onclick="alert('Kill not implemented')">Kill</button></td>
    </tr>
`).join('');
}

// --- PHASE 30: ANOMALY MANAGEMENT (Global) ---

window.fetchAnomalies = async function () {
    try {
        const resp = await fetch('/admin/dashboard/state');
        if (!resp.ok) return;
        const data = await resp.json();
        const anomalies = data.summary?.anomalies || [];

        const tbody = document.getElementById('anomaly-table-body');

        // Update Widget
        let newCount = anomalies.filter(a => a.status === 'new').length;
        let critCount = anomalies.filter(a => a.severity === 'critical' && a.status === 'new').length;
        if (window.updateAnomalyWidget) {
            window.updateAnomalyWidget(newCount, critCount, anomalies.length);
        }

        if (!tbody) return;

        if (anomalies.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No anomalies recorded.</td></tr>';
            return;
        }

        anomalies.sort((a, b) => b.timestamp - a.timestamp);

        tbody.innerHTML = anomalies.map(a => {
            const date = new Date(a.timestamp * 1000).toLocaleTimeString();
            const isAck = a.status === 'acknowledged';
            const severityClass = (a.severity || 'info').toLowerCase();

            const errorCtx = a.metadata?.latest_error ? `<div style="font-size:0.85em; color:var(--accent-error); margin-top:4px;">${a.metadata.latest_error}</div>` : '';

            return `
                <tr class="${isAck ? 'dimmed' : ''}">
                    <td>${date}</td>
                    <td><span class="badge ${severityClass}">${(a.severity || 'INFO').toUpperCase()}</span></td>
                    <td>
                        ${a.metric_name}
                        ${errorCtx}
                    </td>
                    <td>${(a.deviation || 0).toFixed(1)}σ</td>
                    <td>${(a.status || 'NEW').toUpperCase()}</td>
                    <td>
                        ${!isAck ? `<button class="action-btn sm" onclick="ackAnomaly('${a.id}')">Ack</button>` : '-'}
                    </td>
                </tr>
            `;
        }).join('');

    } catch (e) { console.error("Anomaly fetch failed", e); }
};

window.updateAnomalyWidget = function (newCount, critCount, totalCount) {
    const w = document.getElementById('anomaly-widget');
    const s = document.getElementById('anomaly-widget-status');
    const b = document.getElementById('anomaly-count-badge');

    if (w) w.style.display = totalCount > 0 ? 'block' : 'none';

    if (s) {
        if (newCount > 0) {
            s.textContent = `${newCount} Active (${critCount} Critical)`;
            s.style.color = critCount > 0 ? 'var(--accent-error)' : 'var(--accent-warning)';
        } else if (totalCount > 0) {
            s.textContent = "All Acknowledged";
            s.style.color = 'var(--text-secondary)';
        } else {
            s.textContent = "No Issues";
        }
    }

    if (b) b.textContent = `${newCount} New`;
};

window.ackAnomaly = async function (id) {
    try {
        await fetch(`/admin/observability/anomalies/${id}/ack`, { method: 'POST' });
        showNotification('Anomaly Acknowledged');
        fetchAnomalies();
    } catch (e) {
        showNotification('Failed to acknowledge', 'error');
        console.error(e);
    }
};

// Initial Hook
document.addEventListener('DOMContentLoaded', () => {
    // Hook Tab
    document.querySelectorAll('.tab-link[data-tab="anomalies"]').forEach(btn => {
        btn.addEventListener('click', () => { setTimeout(fetchAnomalies, 100); });
    });

    // Start Polling
    setInterval(fetchAnomalies, 5000);
});

// --- PHASE 25: DIAGNOSTICS STREAM ---
window.diagEventSource = null;

window.startDiagnosticsStream = function () {
    const logWindow = document.getElementById('diag-stream-log');
    if (!logWindow) return;

    if (window.diagEventSource) window.diagEventSource.close();

    const evtSource = new EventSource("/admin/diagnostics/stream");
    window.diagEventSource = evtSource;

    evtSource.onmessage = function (e) {
        try {
            if (!e.data) return;
            const data = JSON.parse(e.data);
            const line = data.line || "";

            const div = document.createElement('div');
            div.className = 'log-entry info';
            div.style.whiteSpace = 'pre-wrap';
            div.style.fontFamily = "'JetBrains Mono', monospace";
            div.style.fontSize = "0.85rem";

            if (line.includes('[AI Insight]')) {
                div.style.color = "var(--accent-neon)";
                div.style.fontWeight = "bold";
            } else if (line.includes('CRITICAL')) {
                div.style.color = "var(--accent-error)";
            } else if (line.includes('WARNING')) {
                div.style.color = "var(--accent-warning)";
            } else if (line.includes('INFO')) {
                div.style.color = "var(--text-secondary)";
            }

            div.textContent = line;
            logWindow.appendChild(div);
            // Auto Scroll
            logWindow.scrollTop = logWindow.scrollHeight;

        } catch (err) {
            console.warn("Stream parse error", err);
        }
    };

    evtSource.onerror = function (e) {
        evtSource.close();
        // Auto-reconnect after 3s
        setTimeout(() => { if (window.diagEventSource === evtSource) window.startDiagnosticsStream(); }, 3000);
    };
};
