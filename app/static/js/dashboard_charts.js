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

(() => {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    if (typeof differentChartData === "undefined") return;

    const canvas = document.getElementById("incomeExpenseDateChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
      type: "line", // try "line" too 1) "bar" 2) "line"
      data: {
        labels: differentChartData.labels,
        datasets: [
          {
            label: "Income",
            data: differentChartData.income,
          },
          {
            label: "Expense",
            data: differentChartData.expense,
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



// bar chart; total expanses in a specific month

(() => {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    if (typeof expenseCategory === "undefined") return;

    const canvas = document.getElementById("categoryExpenseDateChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: expenseCategory.labels,
        datasets: [
          {
            label: "Expenses by Category",
            data: expenseCategory.totals,
          },
        ],
      },
      options: {
        responsive: true,
        onResize: handleResize,
        scales: {
          y: { beginAtZero: true },
        },
      },
    });
  });
})();


