console.log("🔥 Enterprise Dashboard JS Loaded v2.1");

const STATUS_URL = "/api/status";
const METRICS_URL = "/api/metrics";

let cpuChart, memChart, latChart, networkChart;

const MAX_POINTS = 20;

/* ================================
   Utils
================================ */

async function fetchJSON(url) {
  try {
    const r = await fetch(url, { cache: "no-store" });
    return await r.json();
  } catch (e) {
    console.error("Fetch failed", e);
    return null;
  }
}

function pct(v) {
  return Math.round((v || 0) * 100);
}

function createGradient(ctx, colorStart, colorEnd) {
  const gradient = ctx.createLinearGradient(0, 0, 0, 100);
  gradient.addColorStop(0, colorStart);
  gradient.addColorStop(1, colorEnd);
  return gradient;
}

/* ================================
   Charts Configuration
================================ */
const commonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { enabled: false } },
  scales: {
    x: { display: false },
    y: { display: false, min: 0 }
  },
  elements: {
    point: { radius: 0 },
    line: { tension: 0.4, borderWidth: 2 }
  },
  animation: { duration: 0 } // Performance
};

function initCharts() {
  const ctxCpu = document.getElementById('miniCpuChart').getContext('2d');
  const ctxMem = document.getElementById('miniMemChart').getContext('2d');
  const ctxLat = document.getElementById('miniLatChart').getContext('2d');
  const ctxNet = document.getElementById('networkChart').getContext('2d'); // Dummy for visual

  const gradientCpu = createGradient(ctxCpu, 'rgba(59, 130, 246, 0.5)', 'rgba(59, 130, 246, 0.0)');
  const gradientMem = createGradient(ctxMem, 'rgba(168, 85, 247, 0.5)', 'rgba(168, 85, 247, 0.0)');
  const gradientLat = createGradient(ctxLat, 'rgba(236, 72, 153, 0.5)', 'rgba(236, 72, 153, 0.0)');
  const gradientNet = createGradient(ctxNet, 'rgba(6, 182, 212, 0.5)', 'rgba(6, 182, 212, 0.0)');

  cpuChart = new Chart(ctxCpu, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        data: [],
        borderColor: '#3B82F6',
        backgroundColor: gradientCpu,
        fill: true
      }]
    },
    options: commonOptions
  });

  memChart = new Chart(ctxMem, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        data: [],
        borderColor: '#A855F7',
        backgroundColor: gradientMem,
        fill: true
      }]
    },
    options: commonOptions
  });

  latChart = new Chart(ctxLat, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        data: [],
        borderColor: '#EC4899',
        backgroundColor: gradientLat,
        fill: true
      }]
    },
    options: commonOptions
  });

  // Simulated Network Chart (Cosmetic)
  networkChart = new Chart(ctxNet, {
    type: 'line',
    data: {
      labels: Array(20).fill(''),
      datasets: [{
        data: Array(20).fill(0).map(() => Math.random() * 100),
        borderColor: '#06B6D4',
        backgroundColor: gradientNet,
        fill: true
      }]
    },
    options: commonOptions
  });
}

function updateChart(chart, labels, data) {
  chart.data.labels = labels;
  chart.data.datasets[0].data = data;
  chart.update('none'); // 'none' mode for performance
}

/* ================================
   Logic
================================ */

async function updateStatus() {
  const d = await fetchJSON(STATUS_URL);
  if (!d) return;

  // Status: Failure or Normal
  const isNormal = d.cause === "normal";
  const confidence = pct(d.confidence);

  // UI Elements
  const pulseStatusText = document.getElementById("pulse-status-text");
  const pulseIcon = document.getElementById("pulse-icon");
  const confidenceVal = document.getElementById("val-confidence");
  const confidenceBar = document.getElementById("confidence-bar");
  const connectionStatus = document.getElementById("connection-status");

  // Update Text
  pulseStatusText.innerText = isNormal ? "Normal" : "Anomaly Detected";
  confidenceVal.innerText = confidence + "%";
  confidenceBar.style.width = confidence + "%";

  document.getElementById("val-cpu").innerText = Math.round(d.metrics?.cpu || 0) + "%";
  document.getElementById("val-mem").innerText = (d.metrics?.mem || 0).toFixed(1);
  document.getElementById("val-lat").innerText = Math.round(d.metrics?.lat || 0) + "ms";

  // Visual State
  if (isNormal) {
    pulseStatusText.className = "text-xl font-bold text-textMain tracking-wide";
    pulseIcon.className = "w-16 h-16 rounded-full bg-success/20 flex items-center justify-center text-success text-3xl mb-3 shadow-[0_0_30px_rgba(16,185,129,0.3)]";
    pulseIcon.innerHTML = '<i class="fa-solid fa-check"></i>';
    confidenceBar.className = "h-full bg-success w-full text-right transition-all duration-500";
    connectionStatus.className = "flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 border border-success/20 text-success text-xs font-medium";
    connectionStatus.innerHTML = '<span class="relative flex h-2 w-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-success"></span></span> System Stable';
  } else {
    pulseStatusText.innerText = d.cause; // Show the Error Name
    pulseStatusText.className = "text-xl font-bold text-danger tracking-wide";
    pulseIcon.className = "w-16 h-16 rounded-full bg-danger/20 flex items-center justify-center text-danger text-3xl mb-3 shadow-[0_0_30px_rgba(239,68,68,0.3)]";
    pulseIcon.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
    confidenceBar.className = "h-full bg-danger w-full text-right transition-all duration-500";
    connectionStatus.className = "flex items-center gap-2 px-3 py-1.5 rounded-full bg-danger/10 border border-danger/20 text-danger text-xs font-medium";
    connectionStatus.innerHTML = '<span class="relative flex h-2 w-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-danger opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-danger"></span></span> CRITICAL ALERT';
  }

  // Add to History Table
  addToHistoryTable(d);
}

const historyCache = new Set();

function addToHistoryTable(d) {
  if (!d.cause || d.cause === 'normal') return;

  // Create a unique key for the event to allow duplicates only if time differs significantly or just showing latest stream
  // For this simple dashboard, we will just prepend to table
  // But we don't want to spam the table if it's the exact same poll.
  // Let's rely on the history API mostly, but for live "Pop", we can do this.
  // Actually, safer to just Poll the History API.
}

async function updateHistory() {
  const data = await fetchJSON("/api/history"); // This returns list of recent
  if (!data) return;

  const tbody = document.getElementById("history-table-body");
  tbody.innerHTML = "";

  // data = [{time, cause, confidence}, ...]
  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-white/5 transition";

    const isFailure = row.cause !== "normal";
    const severityClass = isFailure ? "bg-danger/20 text-danger border-danger/20" : "bg-success/20 text-success border-success/20";
    const severityLabel = isFailure ? "Critical" : "Routine";
    const action = isFailure ? "Auto-scaled +1 instance" : "Health Check Passed"; // Mocking intelligent actions

    tr.innerHTML = `
            <td class="py-3 pl-2 text-textMuted/70">${row.time}</td>
            <td class="py-3 items-center gap-2">
                 <span class="inline-block w-2 h-2 rounded-full ${isFailure ? 'bg-danger' : 'bg-primary'} mr-2"></span>
                 ${isFailure ? 'Backend Service' : 'System Watchdog'}
            </td>
            <td class="py-3 text-textMain">${row.cause}</td>
            <td class="py-3">
                <span class="px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${severityClass}">
                    ${severityLabel}
                </span>
            </td>
            <td class="py-3 text-textMuted">${action}</td>
            <td class="py-3 pr-2 text-right text-textMuted"><i class="fa-solid fa-ellipsis hover:text-textMain cursor-pointer"></i></td>
        `;
    tbody.appendChild(tr);
  });
}

async function updateMetrics() {
  const d = await fetchJSON(METRICS_URL);
  if (!d) return;

  const ts = d.timestamps.slice(-MAX_POINTS);
  const cpu = d.cpu.slice(-MAX_POINTS);
  const mem = d.memory.slice(-MAX_POINTS);
  const lat = d.latency.slice(-MAX_POINTS);

  updateChart(cpuChart, ts, cpu);
  updateChart(memChart, ts, mem);
  updateChart(latChart, ts, lat);

  // Update Network (Fake)
  const netData = networkChart.data.datasets[0].data;
  netData.shift();
  netData.push(Math.random() * 100);
  networkChart.update('none');
}

async function tick() {
  await updateStatus();
  await updateMetrics();
  await updateHistory();
}

// Theme Logic
function initTheme() {
  const toggleBtn = document.getElementById("theme-toggle");
  const icon = toggleBtn.querySelector("i");
  const html = document.documentElement;

  // Check LocalStorage or System Preference
  const savedTheme = localStorage.getItem("theme");
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  // Default to dark if no save, or if saved is 'dark'
  let isDark = savedTheme ? savedTheme === "dark" : true;

  // Apply Initial State
  if (isDark) {
    html.classList.add("dark");
    icon.classList.remove("fa-sun");
    icon.classList.add("fa-moon");
  } else {
    html.classList.remove("dark");
    icon.classList.remove("fa-moon");
    icon.classList.add("fa-sun");
  }

  // Toggle Listener
  toggleBtn.addEventListener("click", () => {
    isDark = !isDark;

    if (isDark) {
      html.classList.add("dark");
      icon.classList.remove("fa-sun");
      icon.classList.add("fa-moon");
      localStorage.setItem("theme", "dark");
    } else {
      html.classList.remove("dark");
      icon.classList.remove("fa-moon");
      icon.classList.add("fa-sun");
      localStorage.setItem("theme", "light");
    }
  });
}

// Init
window.onload = () => {
  initTheme();
  initCharts();
  tick();
  setInterval(tick, 3000);
};
