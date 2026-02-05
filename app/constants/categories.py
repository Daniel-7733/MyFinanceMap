CATEGORY_BUCKETS = {
    # Needs
    "rent": "needs",
    "mortgage": "needs",
    "electric_bill": "needs",
    "water_bill": "needs",
    "gas_bill": "needs",
    "internet": "needs",
    "phone": "needs",
    "groceries": "needs",
    "fuel": "needs",
    "public_transport": "needs",
    "health_insurance": "needs",
    "medical": "needs",

    # Savings
    "savings": "savings",
    "emergency_fund": "savings",
    "investment": "savings",
    "retirement": "savings",

    # Wants (default)
    "coffee": "wants",
    "entertainment": "wants",
    "subscriptions": "wants",
    "travel": "wants",
    "shopping": "wants",
    "other": "wants",
}




# --------------List----------------

"""
✅ Recommended “Needs” category list

🏠 Housing & Utilities
    rent
    mortgage
    electric_bill
    water_bill
    gas_bill
    internet
    phone
    
🍞 Food
    groceries

🚗 Transportation
    public_transport
    fuel
    car_insurance
    car_maintenance

🏥 Health
    health_insurance
    medical
    pharmacy
    
🏛️ Obligations
    tax
    loan_payment
    credit_card_minimum

✅ Categories that are usually “Wants”

These should not be labeled as wants in the UI — just mapped internally:
    eating_out
    coffee
    entertainment
    subscriptions
    travel
    shopping
    hobbies
    games
    gifts
    other ✅ (default to wants)

💰 Savings categories (optional but powerful)

If you want real reports later, these are gold:
    savings
    emergency_fund
    investment
    retirement
    education

(These should still be txn_type="expense" or maybe "transfer" later.)
"""
