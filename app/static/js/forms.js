// static/js/forms.js
(() => {
  "use strict";

  // Keep this in one place. Later you can inject it from the backend if needed.
  const MAIN_CURRENCY = "USD";

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function getTodayParts() {
    const t = new Date();
    return {
      year: t.getFullYear(),
      month: pad2(t.getMonth() + 1),
      day: pad2(t.getDate()),
    };
  }

  // -------- Currency -> exchange rate visibility --------
  function initExchangeRateToggle() {
    const currencySelect = document.getElementById("currency_code");
    const rateBlock = document.getElementById("rate_block");
    const rateInput = document.getElementById("exchange_rate");

    // If this page doesn't have these inputs, do nothing.
    if (!currencySelect || !rateBlock || !rateInput) return;

    function updateRateVisibility() {
      const selected = (currencySelect.value || "").toUpperCase();

      if (selected && selected !== MAIN_CURRENCY) {
        rateBlock.style.display = "block";
        rateInput.required = true;
      } else {
        rateBlock.style.display = "none";
        rateInput.required = false;
        // Only clear if user is not using foreign currency
        rateInput.value = "";
      }
    }

    currencySelect.addEventListener("change", updateRateVisibility);
    updateRateVisibility(); // run once on load
  }

  // -------- Date defaults (only if empty) --------
  function initDateDefaults() {
    const datePaidInput = document.getElementById("date_paid");
    const periodMonthInput = document.getElementById("period_month");
    const periodMonthText = document.getElementById("period_month_text");

    // If page has none of them, do nothing
    if (!datePaidInput && !periodMonthInput && !periodMonthText) return;

    const { year, month, day } = getTodayParts();

    // date_paid: YYYY-MM-DD
    if (datePaidInput && !datePaidInput.value) {
      datePaidInput.value = `${year}-${month}-${day}`;
    }

    // period_month: YYYY-MM
    if (periodMonthInput && !periodMonthInput.value) {
      periodMonthInput.value = `${year}-${month}`;
    }

    // Human readable label like "January 2026"
    if (periodMonthText) {
      periodMonthText.textContent = new Date(year, Number(month) - 1, 1).toLocaleString("en-US", {
        month: "long",
        year: "numeric",
      });
    }
  }

  // -------- Boot --------
  document.addEventListener("DOMContentLoaded", () => {
    initExchangeRateToggle();
    initDateDefaults();
  });
})();
