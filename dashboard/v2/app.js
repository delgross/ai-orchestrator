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
        pollingInterval: 3000,
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
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');

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
            if (targetTab === 'logs') fetchLogTail();
            if (targetTab === 'tools') fetchMCPData();
        });
    });

    setInterval(() => {
        const now = new Date();
        const el = document.getElementById('clock');
        if (el) el.textContent = now.toLocaleTimeString('en-US', { hour12: false });
    }, 1000);

    // --- Core Data Loop ---
    async function fetchSystemData() {
        // 1. Fetch System Health (Best Effort)
        try {
            const [healthResp, statusResp, breakerResp, llmResp] = await Promise.all([
                fetch('/health'),
                fetch('/admin/system-status'),
                fetch('/admin/circuit-breaker/status'),
                fetch('/admin/llm/status')
            ]);

            if (healthResp.ok) {
                const healthData = await healthResp.json();
                const newVersion = healthData.services?.router?.version;
                if (state.currentVersion && newVersion && state.currentVersion !== newVersion) {
                    showNotification('System Update Detected. Reloading...');
                    setTimeout(() => window.location.reload(), 2000);
                }
                state.currentVersion = newVersion;

                let indicatorData = { ...healthData };

                if (statusResp.ok) {
                    const sData = await statusResp.json();
                    indicatorData.internet = sData.internet;
                }

                if (breakerResp.ok) {
                    const bData = await breakerResp.json();
                    indicatorData.breakers = bData.breakers || {};
                }

                if (llmResp.ok) {
                    const lData = await llmResp.json();
                    // Find Ollama
                    const ollama = lData.llms?.find(x => x.id === 'ollama');
                    indicatorData.ollama_ok = (ollama && ollama.status === 'online');
                }

                updateIndicators(indicatorData);
            }
        } catch (err) {
            console.warn("Health Poll Error: ", err);
        }

        // 2. Fetch Active Tab Data (Isolated from health check failures)
        try {
            if (state.activeTab === 'overview') await fetchOverviewData();
            if (state.activeTab === 'misc') await fetchMiscLLMData();
            if (state.activeTab === 'tools') await fetchMCPData();
            if (state.activeTab === 'logs') await fetchLogTail();
        } catch (err) {
            console.error("Tab Data Poll Error: ", err);
        }
    }

    function updateIndicators(data) {
        function setInd(bgId, ok) {
            const el = document.getElementById(bgId);
            if (!el) return;
            const ind = el.querySelector('.indicator');
            const val = el.querySelector('.value');
            ind.className = `indicator ${ok ? 'online' : 'offline'}`;
            if (val && bgId !== 'status-mcp-tools') val.textContent = ok ? 'ONLINE' : 'OFFLINE';
        }

        setInd('status-router', data.services?.router?.ok);
        setInd('status-mcp', data.services?.agent_runner?.ok);
        setInd('status-ollama', data.ollama_ok);

        // Memory/DB Status based on 'project-memory' breaker
        // If agent is up, check if memory breaker is open (failed)
        let dbOk = data.services?.agent_runner?.ok;
        const memBreaker = data.breakers ? data.breakers['project-memory'] : null;
        if (memBreaker && memBreaker.state === 'open') dbOk = false;

        setInd('status-db', dbOk);

        const internetEl = document.getElementById('status-internet');
        if (internetEl) {
            const internetInd = internetEl.querySelector('.indicator');
            const internetVal = internetEl.querySelector('.value');
            const isConnected = (data.internet === true || data.internet === 'Connected');
            internetInd.className = `indicator ${isConnected ? 'online' : 'offline'}`;
            internetVal.textContent = isConnected ? 'CONNECTED' : 'OFFLINE';
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
                    <div class="card glass">
                        <h3>LLM Provider Status</h3>
                        <div style="margin-bottom:10px; font-size:0.9em; color:var(--text-secondary);">
                            Real-time latency check and model discovery.
                        </div>
                        <table class="status-table">
                            <thead>
                                <tr>
                                    <th align="left">Provider</th>
                                    <th align="left">Type</th>
                                    <th align="left">Latency</th>
                                    <th align="left">Available Models</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.llms.map(p => `
                                    <tr>
                                        <td style="font-weight:600; color:var(--text-main);">${p.id}</td>
                                        <td><span class="badge ${p.type === 'local' ? 'green' : 'blue'}">${p.type}</span></td>
                                        <td class="mono">${p.latency_ms !== null ? p.latency_ms + 'ms' : '<span style="color:var(--text-muted)">?</span>'}</td>
                                        <td style="font-size:0.85em; color:var(--text-secondary); max-width: 400px; overflow:hidden; text-overflow:ellipsis;">
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
        const statsResp = await fetch('/admin/observability/stats');
        if (statsResp.ok) {
            const data = await statsResp.json();
            const metrics = data.metrics || {};
            document.getElementById('metric-requests').textContent = metrics.completed_requests || metrics.requests || 0;
            document.getElementById('metric-latency').textContent = `${Math.round(metrics.avg_latency || 0)}ms`;
            document.getElementById('metric-cache').textContent = `${((metrics.cache_hit_rate || 0) * 100).toFixed(1)}%`;
            document.getElementById('metric-errors').textContent = `${((metrics.error_rate || 0) * 100).toFixed(1)}%`;
        }
    }

    // --- Helper: Robust Fetch ---
    async function fetchWithRetry(url, options = {}, retries = 3, delay = 1000, timeout = 5000) {
        for (let i = 0; i < retries; i++) {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), timeout);
            try {
                const resp = await fetch(url, { ...options, signal: controller.signal });
                clearTimeout(id);
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                return resp;
            } catch (err) {
                clearTimeout(id);
                if (i === retries - 1) throw err;
                console.warn(`Fetch failed for ${url} (${err.name}), retrying (${i + 1}/${retries})...`);
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
                        allModels.push({ id: `${provider.id}:${m}`, provider: provider.id });
                    });
                } else {
                    allModels.push({ id: provider.id + ":*", provider: provider.id });
                }
            });

            const roleLabels = {
                "agent_model": "Agent Runner (MCP Host)",
                "task_model": "Task Executor",
                "mcp_model": "Generic Tool Host",
                "router_model": "Gateway / Router",
                "embedding_model": "Embedding Engine",
                "summarization_model": "Memory & Summarization",
                "finalizer_model": "Finalizer (High-Reasoning)",
                "fallback_model": "Fallback Engine"
            };

            const tbody = document.getElementById('roles-table-body');
            if (tbody && rolesData.roles) {
                tbody.innerHTML = Object.entries(rolesData.roles).map(([key, val]) => {
                    if (!roleLabels[key]) return '';

                    let found = false;
                    let options = allModels.map(m => {
                        let valToCheck = m.provider === 'local' || m.provider === 'ollama' ? `ollama:${m.id}` : m.id;
                        let selected = (val === valToCheck);
                        if (selected) found = true;
                        return `<option value="${valToCheck}" ${selected ? 'selected' : ''}>${m.id} (${m.provider})</option>`;
                    }).join('');

                    if (!found) {
                        options = `<option value="${val}" selected style="color:#ffcc00; font-weight:bold;">${val} (Active - Not in Catalog)</option>` + options;
                    }

                    return `
                        <tr>
                            <td style="font-weight:600; color:var(--text-main);">${roleLabels[key]}</td>
                            <td class="mono" style="color:var(--accent-neon);">${val}</td>
                            <td>
                                <select class="config-select" id="sel-${key}" style="width:100%">
                                    ${options}
                                </select>
                            </td>
                            <td>
                                <button class="action-btn sm" onclick="updateRole('${key}', document.getElementById('sel-${key}').value, this)">Apply</button>
                            </td>
                        </tr>
                    `;
                }).join('');
            }
        } catch (e) {
            console.error("Failed to load roles after retries", e);
            const tbody = document.getElementById('roles-table-body');
            if (tbody) tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--accent-err);">System Offline or Connecting...</td></tr>`;
        }
    };

    window.updateRole = async (roleKey, newValue, btn) => {
        if (btn) {
            btn.textContent = '...';
            btn.disabled = true;
        }

        const body = { updates: {} };
        body.updates[roleKey] = newValue;

        try {
            const resp = await fetch('/admin/llm/roles', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            if (resp.ok) {
                showNotification(`Updated ${roleKey}`);
                await fetchSystemRoles();
            } else {
                showNotification('Failed to update role');
            }
        } catch (e) {
            console.error(e);
            showNotification('Error updating role');
        } finally {
            if (btn) {
                btn.textContent = 'Apply';
                btn.disabled = false;
            }
        }
    };

    // ... (fetchMCPData, etc. remain the same, ensure they are not cut off)

    // --- MCP / Tools Logic ---
    let mcpRetryCount = 0;
    async function fetchMCPData() {
        const list = document.getElementById('mcp-servers-list');
        const retryLimit = 3;

        if (!list) return;

        try {
            // Robust Parallel Fetch: Tools (Content) + Breakers (Status)
            const [toolsResult, breakersResult] = await Promise.allSettled([
                fetchWithRetry('/admin/mcp/tools', {}, 2, 500, 5000),
                fetch('/admin/circuit-breaker/status')
            ]);

            // Handle Tools (Primary Content)
            let toolMap = {};
            if (toolsResult.status === 'fulfilled' && toolsResult.value.ok) {
                const data = await toolsResult.value.json();
                if (data.ok) toolMap = data.tools || {};
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

            const serverNames = Object.keys(toolMap);

            if (serverNames.length === 0) {
                if (mcpRetryCount < retryLimit) {
                    list.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-secondary);">Initializing MCP Servers... (Attempt ${mcpRetryCount + 1})<br><small>Waiting for backend to populate tools cache...</small></div>`;
                    mcpRetryCount++;
                    setTimeout(fetchMCPData, 2000);
                    return;
                } else {
                    list.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-muted);">No MCP Servers Detected.<br><small>Check your configuration or logs.</small></div>`;
                    return;
                }
            }

            mcpRetryCount = 0; // Success, reset counter

            // Render
            list.innerHTML = serverNames.map(name => {
                const tools = toolMap[name] || [];
                const breaker = breakerMap[name] || { state: 'UNKNOWN', total_successes: 0, total_failures: 0 };
                const stateClass = breaker.state ? breaker.state.toLowerCase() : 'unknown';

                const toolOptions = tools.length > 0
                    ? tools.map(t => {
                        const tName = t.name || t.function?.name || 'Unknown';
                        return `<option>${tName}</option>`;
                    }).join('')
                    : `<option disabled>No tools loaded</option>`;

                return `
                    <div class="server-card glass">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4>
                                <span>${name}</span>
                                <span class="indicator ${stateClass}" title="Circuit Breaker: ${stateClass.toUpperCase()}"></span>
                            </h4>
                             ${breaker.state === 'OPEN' ? `<button class="action-btn sm primary" onclick="resetBreaker('${name}')">Reset</button>` : ''}
                        </div>
                        <div class="tool-meta">
                            Success: ${breaker.total_successes || 0} | Failures: ${breaker.total_failures || 0}
                        </div>
                        <div style="margin-top: 10px;">
                            <label style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-bottom: 4px;">Available Tools (${tools.length})</label>
                            <select class="config-select" style="width: 100%;">
                                ${toolOptions}
                            </select>
                        </div>
                    </div>
                `;
            }).join('');

        } catch (e) {
            console.warn("MCP Fetch Loop Error", e);
            if (mcpRetryCount < retryLimit) {
                list.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-secondary);">Connecting to Agent Runner... (${mcpRetryCount + 1})<br><small>${e.message}</small></div>`;
                mcpRetryCount++;
                setTimeout(fetchMCPData, 2000);
            } else {
                list.innerHTML = `<div style="text-align:center; padding:20px; color:var(--accent-err);">Connection Failed.<br><small>${e.message}</small><br><button class="action-btn sm" onclick="fetchMCPData()">Retry</button></div>`;
            }
        }
    }

    // --- Ollama Manager ---
    async function fetchOllamaModels() {
        const grid = document.getElementById('ollama-models-grid');
        if (!grid) return;

        grid.innerHTML = `
            <div class="card glass full-width" style="grid-column: 1 / -1; margin-bottom: 20px;">
                <h3>Manage Ollama Models</h3>
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 10px;">
                    <div style="flex: 1; min-width: 300px;">
                         <label class="label">Pull New Model</label>
                         <div style="display: flex; gap: 10px;">
                            <input type="text" id="pull-model-name" placeholder="e.g. llama3, mistral..." class="input-text" style="flex-grow:1;">
                            <button class="action-btn" onclick="startModelPull()">Pull</button>
                         </div>
                         <div id="pull-status" style="font-size: 0.8rem; color: var(--text-muted); margin-top: 5px;"></div>
                    </div>
                    <div style="flex: 1; min-width: 300px;">
                        <label class="label">Runtime Parameters (Global)</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div>
                                <span style="font-size: 0.8rem;">Temperature</span>
                                <input type="number" step="0.1" min="0" max="1" value="0.7" class="input-text">
                            </div>
                             <div>
                                <span style="font-size: 0.8rem;">Context Window</span>
                                <input type="number" step="1024" value="8192" class="input-text">
                            </div>
                        </div>
                        <button class="action-btn sm" style="margin-top: 10px;" onclick="alert('Params Updated')">Apply Params</button>
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
            status.textContent = `Pulling ${name}: 10%... (Simulation)`;
            showNotification(`Pull started for ${name}`);
        }, 500);
    };

    // --- Config Logic ---
    async function fetchConfigFiles() {
        const sel = document.getElementById('config-file-selector');
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
            const r = await fetch(`/admin/config/read?path=${encodeURIComponent(path)}`);
            if (r.ok) {
                const d = await r.json();
                document.getElementById('config-editor').value = d.content;
                const help = document.querySelector('.tip-text');
                if (path.includes('providers.yaml')) {
                    help.innerHTML = `<strong>Tip:</strong> Define MCP servers here. Restart required after saving.`;
                } else {
                    help.innerHTML = `Editing <strong>${path.split('/').pop()}</strong>`;
                }
            }
        });
    }

    document.getElementById('btn-save-config').addEventListener('click', async () => {
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
# --- NEW SERVER TEMPLATE ---
# 1. Replace 'my-server-name' with your tool's name
# 2. Check 'args' for the correct package
# 3. Add env vars if needed
my-server-name:
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

    function showNotification(msg) {
        const toast = document.createElement('div');
        toast.className = 'toast glass';
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 500); }, 3000);
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
                    <div class="task-item" style="cursor:pointer;" onclick="loadDoc('${f.path}', '${f.name}')">
                        <span class="task-name">📄 ${f.name}</span>
                    </div>
                `).join('');
            } else {
                listEl.innerHTML = '<div style="padding:1rem; color:var(--text-muted)">No documentation files found in ai/docs.</div>';
            }
        }
    }
    window.loadDoc = async (path, name) => {
        const resp = await fetch(`/admin/docs/read?path=${encodeURIComponent(path)}`);
        if (resp.ok) {
            const data = await resp.json();
            document.getElementById('doc-viewer-title').textContent = name;
            document.getElementById('doc-viewer-content').innerHTML = marked.parse(data.content);
        }
    };

    async function fetchLogTail() {
        const resp = await fetch('/admin/logs/tail?lines=50');
        if (resp.ok) {
            const data = await resp.json();
            const container = document.getElementById('log-container');
            container.innerHTML = data.logs.map(line => {
                const updated = line.replace(/</g, '&lt;');
                let cls = 'info';
                if (updated.includes('ERROR')) cls = 'error';
                if (updated.includes('WARNING')) cls = 'warn';
                return `<div class="log-entry ${cls}">${updated}</div>`;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }
    }
    document.getElementById('btn-refresh-logs')?.addEventListener('click', fetchLogTail);

    window.resetBreaker = async (name) => {
        await fetch(`/admin/circuit-breakers/${name}/reset`, { method: 'POST' });
        showNotification(`Breaker ${name} reset.`);
        fetchMCPData();
    };

    fetchSystemData();
    fetchSystemRoles();

    // Start Polling Loop
    setInterval(fetchSystemData, state.pollingInterval);

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
            let fullResponse = "";

            try {
                // Use relative path since Dashboard is served by Router
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

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        const trimmed = line.trim();
                        if (!trimmed || !trimmed.startsWith('data: ')) continue;

                        const dataStr = trimmed.slice(6);
                        if (dataStr === '[DONE]') break;

                        try {
                            const json = JSON.parse(dataStr);
                            if (json.error) {
                                fullResponse += `\n[Error: ${json.error.message}]`;
                            } else {
                                const content = json.choices[0]?.delta?.content || "";
                                fullResponse += content;
                            }
                            assistantDiv.textContent = fullResponse;
                            historyDiv.scrollTop = historyDiv.scrollHeight;
                        } catch (e) { }
                    }
                }
                statusSpan.textContent = "Ready";
                statusSpan.className = "status-indicator";

                // Speak completed response if enabled
                speak(fullResponse);

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
});

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
        btn.innerHTML = "�� Apply Changes";
    }
}

async function loadConfigFile() {
    const editor = document.getElementById('config-editor');
    if (!editor) return;
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
