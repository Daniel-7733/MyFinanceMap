(() => {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    if (typeof chartData === "undefined") return;

    const canvas = document.getElementById("incomeExpenseChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
      type: "line", // try "line" too 1) "bar" 2) "line"
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
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  });
})();
