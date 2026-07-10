# MyFinanceMap Architecture

## What ARCHITECTURE.md contain?
1. Purpose
2. Project Structure
3. Data Flow
4. Module Responsibilities
5. Future Architecture

---

### 1. Purpose

MyFinanceMap is a personal finance application whose mission is to make **_financial life easier_**.

The application focuses on four major areas:
1. Recording financial data
2. Organizing financial information
3. Analyzing financial behavior
4. Predicting future financial trends

The application is built around modular components where every module has exactly one responsibility.

---

### 2. High Level Architecture

```
                 User
                  │
                  ▼
             Flask Routes
                  │
                  ▼
          Business Services
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
    Database          Analytics Engine
        │                   │
        └─────────┬─────────┘
                  ▼
             HTML Templates
                  │
                  ▼
             Charts / Reports
```


---

### 3. Request Pipeline

```
            Browser
               │
               ▼
        /analysis Route
               │
               ▼
        Analytics Service
               │
               ▼
               
        Statistics Module
        
        Trend Module
        
        Forecast Module
        
               │
               ▼
        Database Queries
               │
               ▼
        Processed Results
               │
               ▼
        analysis.html
               │
               ▼
        User sees charts
```

---

### 4. Module Responsibilities


### app/

Purpose: **Contains the web application.**

Responsible for
- Flask application
- Routing
- Templates
- User interaction


### services/

Purpose: **Contains the business logic.**

Responsible for
- Calculations
- Financial analysis
- Data processing

**_"Routes should never perform heavy calculations."_**


### analytics/

Purpose: **Produces financial intelligence.**

Responsible for
- Statistics
- Trend Analysis
- Forecasting

**_"This module never renders HTML."_**



### statistics.py

Purpose: **Describes the current financial situation.**

Examples:
- Mean
- Median
- Standard deviation
- Income totals
- Expense totals
- Spending by category

Answers: **_"What does the user's financial data look like?"_**


### trends.py

Purpose: **Detects the direction of financial behavior.**

Examples:
- Spending increasing
- Spending decreasing
- Stable income
- Category growth
- Category decline

Answers: **_"Where is the user's financial behavior heading?"_**


### forecast.py

Purpose: **Predicts future financial behavior.**

Examples:
- Next month's income
- Expected expenses
- Savings prediction
- Cash flow prediction

Answers: **_"What will probably happen next?"_**


---

### Future Architecture
```
                Analytics
        ┌──────────┼───────────┐
        ▼          ▼           ▼
  Statistics     Trends     Forecast
        │          │           │
        └──────────┼───────────┘
                   ▼
      generate_financial_report()
                   │
                   ▼
            HTML / Charts
```

### Note: This document should answer these questions:
1. What is this project?
2. How does data move through it?
3. What does each module do?
4. Where should I add new code?
5. Where should I not add code?
