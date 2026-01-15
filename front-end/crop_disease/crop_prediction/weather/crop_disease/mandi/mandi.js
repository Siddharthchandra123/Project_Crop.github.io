/* =====================================================
   GLOBAL STATE
===================================================== */
let mandiData = null;
let trendChart = null;
let barChart = null;

/* =====================================================
   DOM ELEMENTS
===================================================== */
const stateFilter = document.getElementById("stateFilter");
const commodityFilter = document.getElementById("commodityFilter");
const tableBody = document.getElementById("tableBody");
const topMoversDiv = document.getElementById("topMovers");
const lastUpdatedEl = document.getElementById("lastUpdated");

/* =====================================================
   FETCH DATA FROM FLASK API
===================================================== */
async function fetchFromAPI() {
  try {
    const state =
      stateFilter.value && stateFilter.value !== "All"
        ? stateFilter.value
        : "";

    const commodity =
      commodityFilter.value && commodityFilter.value !== "All"
        ? commodityFilter.value
        : "";

    const response = await fetch(
      `http://127.0.0.1:5000/api/mandi-prices?state=${state}&commodity=${commodity}`
    );

    if (!response.ok) {
      throw new Error("API response not OK");
    }

    mandiData = await response.json();

    if (!mandiData || !Array.isArray(mandiData.markets)) {
      throw new Error("Invalid API data");
    }

    initFilters();
    updateDashboard();
    renderTopMovers();

    lastUpdatedEl.innerText =
      "Last updated: " +
      (mandiData.lastUpdated
        ? new Date(mandiData.lastUpdated).toLocaleString()
        : new Date().toLocaleString());

  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

/* =====================================================
   FILTER DROPDOWNS
===================================================== */
function initFilters() {
  const states = ["All", ...new Set(mandiData.markets.map(m => m.state))];
  const commodities = ["All", ...new Set(mandiData.markets.map(m => m.commodity))];

  stateFilter.innerHTML = states.map(s => `<option>${s}</option>`).join("");
  commodityFilter.innerHTML = commodities.map(c => `<option>${c}</option>`).join("");
}

/* =====================================================
   FILTER DATA
===================================================== */
function getFilteredData() {
  const state = stateFilter.value;
  const commodity = commodityFilter.value;
  const search = document.getElementById("searchInput").value.toLowerCase();

  return mandiData.markets.filter(m =>
    (state === "All" || m.state === state) &&
    (commodity === "All" || m.commodity === commodity) &&
    m.mandi.toLowerCase().includes(search)
  );
}

/* =====================================================
   TABLE
===================================================== */
function renderTable(data) {
  tableBody.innerHTML = data
    .map(
      m => `
      <tr>
        <td>${m.state}</td>
        <td>${m.mandi}</td>
        <td>${m.commodity}</td>
        <td>₹${m.price}</td>
        <td>${m.avg7d}</td>
      </tr>`
    )
    .join("");
}

/* =====================================================
   TOP MOVERS
===================================================== */
function renderTopMovers() {
  const movers = [...mandiData.markets]
    .map(m => ({ ...m, diff: m.price - m.avg7d }))
    .sort((a, b) => Math.abs(b.diff) - Math.abs(a.diff))
    .slice(0, 5);

  topMoversDiv.innerHTML = movers
    .map(
      m => `
      <div class="top-mover">
        <span>${m.mandi} (${m.commodity})</span>
        <span class="${m.diff >= 0 ? "up" : "down"}">
          ${m.diff >= 0 ? "+" : ""}${m.diff}
        </span>
      </div>`
    )
    .join("");
}

/* =====================================================
   CHARTS
===================================================== */
function renderCharts(filteredData) {
  if (!mandiData || !mandiData.markets.length) return;

  if (trendChart) trendChart.destroy();
  if (barChart) barChart.destroy();

  /* =========================================
     PIE CHART → ALL CROPS IN STATE
  ========================================== */

  const stateData = getStateMandiData();

  const pieAgg = {};
  stateData.forEach(m => {
    pieAgg[m.commodity] = pieAgg[m.commodity] || [];
    pieAgg[m.commodity].push(m.price);
  });

  const pieLabels = Object.keys(pieAgg);
  const pieValues = pieLabels.map(
    k => Math.round(pieAgg[k].reduce((a,b)=>a+b) / pieAgg[k].length)
  );

  trendChart = new Chart(
    document.getElementById("trendChart"),
    {
      type: "pie",
      data: {
        labels: pieLabels,
        datasets: [{
          data: pieValues
        }]
      },
      options: {
        plugins: {
          legend: { position: "right" },
          title: {
            display: true,
            text: `All Crop Prices in ${stateFilter.value} Mandis`
          }
        }
      }
    }
  );

  /* =========================================
     BAR CHART → STATE + CROP FILTER
  ========================================== */

  if (!filteredData.length) return;

  const barAgg = {};
  filteredData.forEach(m => {
    barAgg[m.commodity] = barAgg[m.commodity] || [];
    barAgg[m.commodity].push(m.price);
  });

  const barLabels = Object.keys(barAgg);
  const barValues = barLabels.map(
    k => Math.round(barAgg[k].reduce((a,b)=>a+b) / barAgg[k].length)
  );

  barChart = new Chart(
    document.getElementById("barChart"),
    {
      type: "bar",
      data: {
        labels: barLabels,
        datasets: [{
          label: "Average Price ₹",
          data: barValues
        }]
      }
    }
  );
}


/* =====================================================
   DASHBOARD UPDATE
===================================================== */
function updateDashboard() {
  const filtered = getFilteredData();
  renderTable(filtered);
  renderCharts(filtered);
}

/* =====================================================
   CSV EXPORT
===================================================== */
function exportCSV() {
  const rows = getFilteredData();
  let csv = "State,Mandi,Commodity,Price,7d Avg\n";

  rows.forEach(r => {
    csv += `${r.state},${r.mandi},${r.commodity},${r.price},${r.avg7d}\n`;
  });

  const blob = new Blob([csv], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "mandi_prices.csv";
  link.click();
}

/* =====================================================
   EVENT LISTENERS
===================================================== */
stateFilter.onchange = fetchFromAPI;
commodityFilter.onchange = fetchFromAPI;
document.getElementById("searchInput").oninput = updateDashboard;

/* =====================================================
   INITIAL LOAD
===================================================== */
window.onload = () => {
  fetchFromAPI();
  setInterval(fetchFromAPI, 30000);
};
function getStateMandiData() {
  const state = stateFilter.value;

  if (!state || state === "All") {
    return mandiData.markets; // all states
  }

  return mandiData.markets.filter(m => m.state === state);
}