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


  // Find Current date
  var today = new Date();
  var day = String(today.getDate()).padStart(2, '0');
  var month = String(today.getMonth() + 1).padStart(2, '0');
  var year = today.getFullYear();

  function fullFormateCurrentDate() {
    var fullCurrentDate = year + '-' + month + '-' + day;
    document.getElementById("date_paid").value = fullCurrentDate;
  }

  function yearMonthFormateCurrentDate() {
    document.getElementById("period_month").value = year + "-" + month;

    document.getElementById("period_month_text").innerHTML =
      new Date(year, month - 1).toLocaleString("en-US", {
        month: "long",
        year: "numeric"
      });

  }

  fullFormateCurrentDate();
  yearMonthFormateCurrentDate();

