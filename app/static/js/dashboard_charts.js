// This function give width & height size for a chart
const handleResize = (chart) => {
chart.resize(500, 500);
}

// Bar chart; income vs expanse
(() => {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    if (typeof chartData === "undefined") return;

    const canvas = document.getElementById("incomeExpenseChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
      type: "bar", // try "line" too 1) "bar" 2) "line"
      data: {
        labels: chartData.labels,
        datasets: [
          {
            label: "Income",
            data: chartData.income,
          },
          {
            label: "Expense",
            data: chartData.expense,
          },
        ],
      },
      options: {
        responsive: true,
        onResize: handleResize,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  });
})();


// line chart; total expanses in a specific month

