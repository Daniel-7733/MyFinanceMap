(() => {
  "use strict";

  const MAIN_CURRENCY = window.MAIN_CURRENCY;

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

      if (currencySelect && window.MAIN_CURRENCY) {
          currencySelect.value = window.MAIN_CURRENCY;
      }

      const rateBlock = document.getElementById("rate_block");
      const rateInput = document.getElementById("exchange_rate");
      const rateHelp = document.getElementById("rate_help");

      // If this page doesn't have these inputs, do nothing.
      if (!currencySelect || !rateBlock || !rateInput) return;

      function updateRateVisibility() {
        const selected = (currencySelect.value || "").toUpperCase();

        if (selected && selected !== MAIN_CURRENCY) {
          rateBlock.style.display = "block";
          rateInput.required = true;

          if (rateHelp) {
            rateHelp.textContent =
              `Example: 1 ${selected} = 1.0847 ${MAIN_CURRENCY} → rate = 1.0847`;
          }

        } else {
          rateBlock.style.display = "none";
          rateInput.required = false;
          rateInput.value = "";

          if (rateHelp) {
            rateHelp.textContent =
              "Only required when using a different currency.";
          }
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



setTimeout(() => {
  document.querySelectorAll('.flash').forEach(flash => {
      flash.style.opacity = "0";
      flash.style.transform = "translateX(30px)";
      setTimeout(() => flash.remove(), 400);
  });
}, 4000);
