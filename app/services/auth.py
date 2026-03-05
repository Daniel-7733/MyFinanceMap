from dataclasses import dataclass
from flask import flash
from ..core.security import hash_password

@dataclass(frozen=True)
class RegisterData:
    email: str
    password_hash: str
    full_name: str
    home_currency: str
    location: str

def parse_register_form(form) -> RegisterData | None:
    email = (form.get("email") or "").strip().lower()
    password = (form.get("password") or "").strip()
    full_name = (form.get("full_name") or "").strip()
    home_currency = (form.get("user_currency") or "").strip().upper()


    country = (form.get("country") or "").strip().title()
    state = (form.get("state") or "").strip().title()
    city = (form.get("city") or "").strip().title()
    location = f"{country}, {state}, {city}"

    if not email:
        flash("Email is required.", "error"); return None
    if len(password) < 8:
        flash("Password must be at least 8 characters.", "error"); return None
    if not full_name:
        flash("Full name is required.", "error"); return None
    if not home_currency:
        flash("Home currency is required.", "error"); return None

    return RegisterData(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        home_currency=home_currency,
        location=location,
    )

