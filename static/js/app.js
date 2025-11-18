// static/js/app.js

// --- Helpers -------------------------------------------------------------

function getCSSVar(name) {
  // Reads a CSS variable like --emerald-400 from :root
  if (!window.getComputedStyle) return undefined;
  const value = getComputedStyle(document.documentElement).getPropertyValue(name);
  return value ? value.trim() : undefined;
}

function safePlot(el, plotFn) {
  if (!el) return;
  if (typeof Plotly === "undefined") {
    el.textContent = "Plotly not loaded.";
    return;
  }
  plotFn();
}

// --- Home Page: Overview Chart ------------------------------------------

function initHomePage() {
  const el = document.getElementById("overview-chart");
  safePlot(el, () => {
    const emerald = getCSSVar("--emerald-400") || "#10b981";
    const purple = getCSSVar("--panel-purple-dark") || "#2F1D41";

    const traceWinRate = {
      x: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"],
      y: [52, 54, 51, 55, 53, 56, 57],
      type: "scatter",
      mode: "lines+markers",
      name: "Avg Win Rate",
      line: { width: 2, color: emerald },
      marker: { size: 6 }
    };

    const layout = {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 40, r: 10, t: 30, b: 40 },
      xaxis: {
        title: "",
        tickfont: { color: "#cbd5f5", size: 10 },
        gridcolor: "rgba(148,163,184,0.1)"
      },
      yaxis: {
        title: "Win Rate (%)",
        tickfont: { color: "#cbd5f5", size: 10 },
        gridcolor: "rgba(148,163,184,0.1)"
      },
      font: { color: "#e5e7eb" },
      showlegend: false
    };

    Plotly.newPlot(el, [traceWinRate], layout, { displayModeBar: false });
    window.addEventListener("resize", () => Plotly.Plots.resize(el));
  });
}

// --- Cards Page: Scatter Chart ------------------------------------------

function initCardsPage() {
  const scatterEl = document.getElementById("cards-scatter");
  safePlot(scatterEl, () => {
    const emerald = getCSSVar("--emerald-400") || "#10b981";

    // Dummy card data: usage vs win rate
    const cardNames = [
      "Hog Rider", "Mega Knight", "Miner", "X-Bow", "Lava Hound",
      "Golem", "Mortar", "Royal Giant", "P.E.K.K.A", "Graveyard"
    ];

    const usage = [18, 12, 9, 4, 5, 6, 7, 10, 8, 11]; // %
    const winRate = [55, 53, 57, 50, 54, 52, 51, 56, 53, 58]; // %

    const trace = {
      x: usage,
      y: winRate,
      mode: "markers",
      type: "scatter",
      text: cardNames,
      hovertemplate: "%{text}<br>Usage: %{x}%<br>Win Rate: %{y}%<extra></extra>",
      marker: {
        size: 10,
        color: emerald,
        opacity: 0.9
      }
    };

    const layout = {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 40, r: 10, t: 30, b: 40 },
      xaxis: {
        title: "Usage (%)",
        tickfont: { color: "#cbd5f5", size: 10 },
        gridcolor: "rgba(148,163,184,0.1)"
      },
      yaxis: {
        title: "Win Rate (%)",
        tickfont: { color: "#cbd5f5", size: 10 },
        gridcolor: "rgba(148,163,184,0.1)"
      },
      font: { color: "#e5e7eb" },
      showlegend: false
    };

    Plotly.newPlot(scatterEl, [trace], layout, { displayModeBar: false });
    window.addEventListener("resize", () => Plotly.Plots.resize(scatterEl));
  });

  // v1: filters are static only (no behavior yet)
  // const trophySelect = document.getElementById("trophy-range");
  // const minGamesSelect = document.getElementById("min-games");
  // Later: add event listeners here to refetch/redraw chart based on API.
}

// --- Archetypes Page: Heatmap -------------------------------------------

function initArchetypesPage() {
  const heatmapEl = document.getElementById("archetype-heatmap");
  safePlot(heatmapEl, () => {
    const emerald = getCSSVar("--emerald-400") || "#10b981";
    const bgPurple = getCSSVar("--bg-purple") || "#1B1126";

    // Dummy archetype names
    const archetypes = [
      "Hog Cycle",
      "LavaLoon",
      "Bridge Spam",
      "Golem Beatdown",
      "Control"
    ];

    // Dummy 5x5 matrix of win rates vs other archetypes
    const z = [
      [50, 55, 48, 52, 53],
      [45, 50, 47, 49, 51],
      [52, 53, 50, 48, 54],
      [48, 51, 52, 50, 49],
      [49, 52, 46, 51, 50]
    ];

    const trace = {
      z: z,
      x: archetypes,
      y: archetypes,
      type: "heatmap",
      colorscale: [
        [0, bgPurple],
        [1, emerald]
      ],
      reversescale: false,
      colorbar: {
        title: "Win Rate (%)",
        tickfont: { color: "#e5e7eb" }
      },
      hovertemplate:
        "Your archetype: %{y}<br>Opponent: %{x}<br>Win Rate: %{z}%<extra></extra>"
    };

    const layout = {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 80, r: 20, t: 30, b: 80 },
      xaxis: {
        tickfont: { color: "#cbd5f5", size: 10 },
        showgrid: false
      },
      yaxis: {
        tickfont: { color: "#cbd5f5", size: 10 },
        showgrid: false,
        autorange: "reversed"
      },
      font: { color: "#e5e7eb" },
      showlegend: false
    };

    Plotly.newPlot(heatmapEl, [trace], layout, { displayModeBar: false });
    window.addEventListener("resize", () => Plotly.Plots.resize(heatmapEl));
  });

  // v1: detail pane is static, but we already have hook IDs:
  // - archetype-name
  // - archetype-best
  // - archetype-worst
  // - archetype-summary
  //
  // Later, we can add:
  // heatmapEl.on('plotly_click', (data) => { ... });
}

// --- Simple Router (based on data-page on <body>) -----------------------

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page || "home";

  if (page === "home") {
    initHomePage();
  } else if (page === "cards") {
    initCardsPage();
  } else if (page === "archetypes") {
    initArchetypesPage();
  }
});
