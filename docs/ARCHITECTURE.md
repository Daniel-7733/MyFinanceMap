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


### New Model for income, expense, saving:
```
                    MONEY SYSTEM

Outside World
     │
     │ Income
     ▼
  Checking ─────── Transfer ──────► Savings
     │                               │
     │ Expense                       │ Transfer back
     ▼                               ▼
Outside World                     Checking


                    ANALYTICS

Income ─────┐
Expense ────┼──► Monthly Cash Flow
Saving ─────┘          │
                       ▼
                    Leftover
                       │
                       ▼
              Financial Intelligence
```

### What actually exists in our financial world?
```
                         MyFinanceMap Universe

             ┌──────────── OUTSIDE WORLD ────────────┐
             │                                       │
             │        Income              Expense    │
             │          │                    ▲       │
             │          ▼                    │       │
             │      ┌──────────┐             │       │
             └─────►│ Checking │─────────────┘       │
                    └────┬─────┘
                         │
                      Transfer
                         │
                         ▼
                    ┌─────────┐
                    │ Savings │
                    └────┬────┘
                         │
                      Transfer
                         │
                         ▼
                    ┌──────────┐
                    │ Checking │
                    └──────────┘
```
### Example:
```
Income      30,000
Expense    -15,000
Saving      -5,000
──────────────────
Leftover    10,000

```
### The ownership map
```
User
 │
 ├── owns → Accounts
 │
 └── owns → Financial history


Account
 │
 └── represents → where money exists


Transaction
 │
 └── represents → money crossing the system boundary


Transfer
 │
 └── represents → money moving between accounts


Saving
 │
 └── derived from → qualifying transfers


Leftover
 │
 └── derived from → monthly cash flow
```

### For analytics engine:
```
                 FINANCIAL DOMAIN

        Transactions        Transfers
             │                  │
             ▼                  ▼
       Income/Expense       Saving Activity
             │                  │
             └────────┬─────────┘
                      ▼
               Monthly Cash Flow
                      │
              ┌───────┴────────┐
              ▼                ▼
           Leftover       Account State
              │
              └───────┬────────┘
                      ▼
            Financial Intelligence
```

We can think of architecture like this:

```
          HISTORY
     source of financial truth
             │
             │ produces
             ▼
        CURRENT STATE
      fast stored balances
      
In other words:
"History is authoritative; stored balance is a fast current-state representation."
```

### The money flow:
``` 
                         OUTSIDE WORLD
                              │
                         +30,000 Income
                              │
                              ▼
                    ┌──────────────────┐
                    │     CHECKING     │
                    │     30,000       │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        15,000 Expense                5,000 Transfer
              │                             │
              ▼                             ▼
       OUTSIDE WORLD                 ┌──────────────┐
                                    │   SAVINGS    │
                                    │    5,000     │
                                    └──────────────┘


Monthly interpretation:

Income                 30,000
Expense               -15,000
Savings allocation     -5,000
─────────────────────────────
Leftover               10,000


Account state:

Checking               10,000
Savings                 5,000
─────────────────────────────
Total wealth           15,000
```

### The whole architecture will store two balances on `User`

```
                    USER
                     │
                  Accounts
                ┌────┴────┐
                ▼         ▼
            Checking    Savings
                ▲         ▲
                │         │
             financial movements
                │         │
        ┌───────┴─────────┴───────┐
        │                         │
   Transactions               Transfers
        │                         │
        ▼                         ▼
Income / Expense          Internal movement
        │                         │
        └────────────┬────────────┘
                     ▼
                  History
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    Current Balances         Analytics
                                  │
                                  ▼
                       Financial Intelligence
```

### The responsibilities
```
             TransferService
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     Account    Account    Transfer
     source     target      history
```

and pipline will be like this:
```
User requests:
"Save 2,000 TRY"

        ↓

TransferService

        ↓

Validate request
├── amount > 0?
├── accounts different?
├── same owner?
├── enough money?
└── same currency?

        ↓

Update balances

Checking
10,000 → 8,000

Savings
20,000 → 22,000

        ↓

Create Transfer history

        ↓

Commit everything together
```

### So responsibility become clear:
```
Account
"What money container exists?"

Transfer
"What internal movement happened?"

TransferService
"How do we safely perform that movement?"

Analytics
"What does the history mean?"

UI
"What should the user see?"
```