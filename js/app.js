document.addEventListener("DOMContentLoaded", () => {
  const div = document.getElementById("dummy-chart");
  if (!div) return;

  Plotly.newPlot(div, [{
    x: ["Golem", "Hog Rider", "Lava Hound"],
    y: [52, 56, 54],
    type: "bar",
  }], {
    margin: { t: 20, l: 40 }
  });
});
