from flask import Blueprint, render_template

main: Blueprint = Blueprint("main", __name__)


@main.route("/")
def home() -> str:
    amount: float = 20.99
    currency_symbol: str = "USD"

    return render_template(
        "index.html",
        amount=f"{amount:.2f}{currency_symbol}"
    )

