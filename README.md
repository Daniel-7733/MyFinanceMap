# MyFinanceMap 💰🗺️

MyFinanceMap is a personal finance web application that helps users understand, track, and plan their financial situation using clear rules and real-world context.

The goal of the project is not only expense tracking, but **financial awareness**:
- Where does my money go?
- Am I following the 50 / 30 / 20 rule?
- Can I afford to live in a specific city?
- How healthy is my financial behavior over time?

---

## ✨ Features (Current & Planned)

### ✅ Implemented / MVP
- Add income and expense transactions
- Categorize transactions (Needs / Wants / Savings)
- Monthly financial dashboard
- 50 / 30 / 20 budget comparison
- SQLite database (local-first)
- Clean modular Flask architecture

### 🚧 Planned
- City-based cost of living estimation
- Yearly expense projections
- Financial insights & trends
- Daily money tips / proverbs
- Health score (financial stability indicator)
- Progressive Web App (PWA) support

---

## 🧠 Budgeting Rule
The app uses the **50 / 30 / 20 rule** as a baseline:
- **50% Needs** – rent, groceries, bills
- **30% Wants** – entertainment, eating out
- **20% Savings** – savings, investments, emergency fund

These values are configurable.

---

## 🏗️ Project Structure
```
MyFinanceMap/
│
├── app/
│ ├── data/ # Static data (cities, cost of living)
│ ├── services/ # Business logic (budgeting, analytics)
│ ├── static/ # CSS, JS, images
│ ├── templates/ # HTML templates
│ ├── models.py # Database models
│ ├── routes.py # Flask routes
│ └── init.py
│
├── instance/ # SQLite database (local)
├── tests/ # Unit tests
├── config.py # App configuration
├── run.py # App entry point
├── requirements.txt # Dependencies
└── README.md
```


---

## ⚙️ Tech Stack
- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript (Chart.js planned)
- **Architecture:** MVC-inspired, service-based design

---

## 🚀 How to Run Locally

### 1. Clone the repository

```
git clone https://github.com/YOUR_USERNAME/MyFinanceMap.git
cd MyFinanceMap
```

### 2.Create and activate virtual environment

```
python -m venv .venv
```

- Windows
```
.venv\Scripts\activate
```

- macOS / Linux
```
source .venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Run the app
```
python run.py
```

### 5. Then open:
```
http://127.0.0.1:5000
```

---
## 📌 Why This Project Exists

This project is part of a long-term learning journey focused on:
- Python backend development
- Clean software architecture
- Financial literacy & behavioral insight
- Preparing for larger, real-world applications
---

## 📄 License
This project is open for learning and personal use.
Created by Daniel
