  const MAIN_CURRENCY = "USD";

  const currencySelect = document.getElementById("currency_code");
  const rateBlock = document.getElementById("rate_block");
  const rateInput = document.getElementById("exchange_rate");

  function updateRateVisibility() {
    const selected = (currencySelect.value || "").toUpperCase();

    if (selected && selected !== MAIN_CURRENCY) {
      rateBlock.style.display = "block";
      rateInput.required = true;
    } else {
      rateBlock.style.display = "none";
      rateInput.required = false;
      rateInput.value = "";
    }
  }

  currencySelect.addEventListener("change", updateRateVisibility);
  updateRateVisibility();