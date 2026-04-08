document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------
    // INITIALIZATION & STATE
    // ----------------------------------------------------
    let ec2ChartInstance = null;
    let s3ChartInstance = null;
    let allRecommendations = [];

    // CSE Project Chart Config (Intense Tech)
    Chart.defaults.color = '#52525b';
    Chart.defaults.font.family = "'JetBrains Mono', monospace";
    Chart.defaults.font.size = 10;
    const gridColor = '#27272a';

    const syncBtn = document.getElementById('syncBtn');
    const syncStatus = document.getElementById('syncStatus');
    const severityFilter = document.getElementById('severityFilter');

    syncBtn.addEventListener('click', handleSync);
    severityFilter.addEventListener('change', (e) => renderRecommendations(e.target.value));

    // Boot Up Sequence
    startTypewriter();
    startUptimeCounter();
    simulateHealthMetrics();
    initTerminalFeed();
    fetchDashboardData();

    // ----------------------------------------------------
    // TYPEWRITER & EFFECTS
    // ----------------------------------------------------
    function startTypewriter() {
        const el = document.querySelector('.text-typewriter');
        const text = el.getAttribute('data-text');
        el.textContent = '';
        let i = 0;
        const interval = setInterval(() => {
            el.textContent += text.charAt(i);
            i++;
            if (i >= text.length) clearInterval(interval);
        }, 50);
    }

    function startUptimeCounter() {
        const uptimeEl = document.getElementById('sysUptime');
        let sec = 1420; // Fake start time
        setInterval(() => {
            sec++;
            const h = Math.floor(sec / 3600).toString().padStart(2, '0');
            const m = Math.floor((sec % 3600) / 60).toString().padStart(2, '0');
            const s = (sec % 60).toString().padStart(2, '0');
            uptimeEl.textContent = `${h}:${m}:${s}`;
        }, 1000);
    }

    // Number Anim
    function animateCounter(id, targetValue, isCurrency = false) {
        const obj = document.getElementById(id);
        if (!obj) return;
        const duration = 1000;
        let startTime = null;
        function update(currentTime) {
            if (!startTime) startTime = currentTime;
            const progress = Math.min((currentTime - startTime) / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentVal = targetValue * easeOut;
            obj.textContent = isCurrency ? currentVal.toFixed(2) : Math.floor(currentVal);
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    // ----------------------------------------------------
    // REAL DATA INTEGRATION
    // ----------------------------------------------------
    async function fetchDashboardData() {
        try {
            await Promise.all([
                loadSummary(),
                loadEC2Data(),
                loadS3Data(),
                loadRecommendations()
            ]);
            logTerminalEvent('SYS', 'DATA_PIPELINE_OK');
        } catch (error) {
            logTerminalEvent('ERR', 'API_CONNECTION_REFUSED');
            console.error("Diagnostic error:", error);
        }
    }

    async function handleSync() {
        syncBtn.disabled = true;
        syncStatus.textContent = 'EXECUTING TASK...';
        logTerminalEvent('SYS', 'INITIATING MANUAL SYNC');
        
        try {
            const res = await fetch('/api/sync', { method: 'POST' });
            if (res.ok) {
                logTerminalEvent('OK', 'SYNC TASK DISPATCHED');
                setTimeout(() => {
                    fetchDashboardData();
                    syncBtn.disabled = false;
                    syncStatus.textContent = 'Awaiting input...';
                    logTerminalEvent('OK', 'SYNC COMPLETE');
                }, 1500);
            } else throw new Error('Failed');
        } catch (error) {
            syncStatus.textContent = 'SYNC_FAILED';
            syncBtn.disabled = false;
            logTerminalEvent('ERR', 'SYNC TASK ABORTED');
        }
    }

    async function loadSummary() {
        const res = await fetch('/api/summary');
        const data = await res.json();
        
        animateCounter('totalResources', data.total_ec2 + data.total_s3);
        document.getElementById('totalEc2').textContent = data.total_ec2;
        document.getElementById('totalS3').textContent = data.total_s3;
        
        animateCounter('wasteCount', data.waste_count);
        animateCounter('estimatedSavings', parseFloat(data.estimated_savings_monthly), true);
    }

    async function loadEC2Data() {
        const res = await fetch('/api/ec2');
        const data = await res.json();
        
        const labels = data.map(i => i.instance_id.substring(0, 8));
        const usage = data.map(i => i.cpu_utilization);

        const ctx = document.getElementById('ec2Chart').getContext('2d');
        if (ec2ChartInstance) ec2ChartInstance.destroy();
        
        // Solid technical color
        ec2ChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'CPU LOAD %',
                    data: usage,
                    borderColor: '#0ea5e9',
                    backgroundColor: 'rgba(14, 165, 233, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.2,
                    pointBackgroundColor: '#0ea5e9',
                    pointRadius: 2
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, max: 100, grid: { color: gridColor }, border: { dash: [2,2] } },
                    x: { grid: { color: gridColor }, border: { dash: [2,2] } }
                }
            }
        });
    }

    async function loadS3Data() {
        const res = await fetch('/api/s3');
        const data = await res.json();
        const labels = data.map(b => b.bucket_name);
        const sizes = data.map(b => parseFloat(b.size_mb));

        const ctx = document.getElementById('s3Chart').getContext('2d');
        if (s3ChartInstance) s3ChartInstance.destroy();

        s3ChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: sizes,
                    backgroundColor: ['#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6'],
                    borderWidth: 1, borderColor: '#121214'
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: gridColor } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    async function loadRecommendations() {
        const res = await fetch('/api/recommendations');
        allRecommendations = await res.json();
        renderRecommendations('All');
    }

    function renderRecommendations(filterObj) {
        const tbody = document.querySelector('#recommendationsTable tbody');
        tbody.innerHTML = '';
        let filtered = filterObj !== 'All' ? allRecommendations.filter(r => r.severity === filterObj) : allRecommendations;

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 2rem;">[SYS_OK] No directives required.</td></tr>';
            return;
        }

        filtered.forEach(rec => {
            const tr = document.createElement('tr');
            let displayId = rec.resource_id;
            if (rec.resource_type === 'EC2' && displayId.length > 12) {
                displayId = displayId.substring(0, 10) + '...';
            }
            tr.innerHTML = `
                <td>${displayId}</td>
                <td>${rec.resource_type}</td>
                <td>${rec.issue}</td>
                <td style="color: var(--text-main);">${rec.recommendation}</td>
                <td><span class="badge ${rec.severity.toLowerCase()}">${rec.severity}</span></td>
                <td class="text-right" style="color:var(--accent-emerald);">+$${parseFloat(rec.estimated_savings_monthly).toFixed(2)}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // ----------------------------------------------------
    // SIMULATED DATA & ACTIVITY FEED
    // ----------------------------------------------------
    function simulateHealthMetrics() {
        setInterval(() => {
            const ping = 15 + Math.floor(Math.random() * 20);
            const mem = 35 + Math.floor(Math.random() * 10);
            const io = 65 + Math.floor(Math.random() * 25);
            
            document.getElementById('valPing').textContent = ping + 'ms';
            document.getElementById('barPing').style.width = ping + '%';
            
            document.getElementById('valMem').textContent = mem + '%';
            document.getElementById('barMem').style.width = mem + '%';
            
            document.getElementById('valIo').textContent = io + '%';
            document.getElementById('barIo').style.width = io + '%';
            if(io > 80) document.getElementById('barIo').classList.add('warn');
            else document.getElementById('barIo').classList.remove('warn');
            
        }, 3000);
    }

    function initTerminalFeed() {
        const initialLogs = [
            { t: 'SYS', m: 'Boot sequence initiated' },
            { t: 'OK', m: 'AWS API credentials verified' },
            { t: 'SYS', m: 'Scanning topography...' }
        ];
        initialLogs.forEach(l => logTerminalEvent(l.t, l.m));
        
        // Random fake streams
        const events = ['TCP Ping: OK', 'Fetching object meta...', 'Mem cache clear', 'Handshake EC2_Node', 'Latency check 24ms'];
        setInterval(() => {
            if(Math.random() > 0.6) {
                logTerminalEvent('SYS', events[Math.floor(Math.random()*events.length)]);
            }
        }, 2000);
    }

    function logTerminalEvent(type, msg) {
        const term = document.getElementById('eventStream');
        if (!term) return;
        const d = new Date();
        const timeStr = d.toISOString().split('T')[1].substring(0,12); // HH:MM:SS.mmm
        
        const line = document.createElement('div');
        line.className = 'term-line';
        
        let typeClass = 'term-sys';
        if(type === 'OK') typeClass = 'term-ok';
        if(type === 'ERR') typeClass = 'term-err';

        line.innerHTML = `<span class="term-time">[${timeStr}]</span> <span class="${typeClass}">[${type}]</span> ${msg}`;
        term.appendChild(line);
        term.scrollTop = term.scrollHeight;
    }
});
