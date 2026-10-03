<div align="center">

# 💸 Lusi Expense Tracker

A personal expense tracking dashboard built with Python and Streamlit.
Log spending, set a monthly budget, and see where your money goes.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)

![Dashboard](dashboard.png)

</div>

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data and Security](#data-and-security)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)

## Features

| Area | What you can do |
|------|-----------------|
| **Authentication** | Sign up, log in, and reset a forgotten password with a security question |
| **Dashboard** | Total expenses, remaining budget, 7-day spending chart, category donut, recent transactions |
| **Add Expense** | Enter amount, category, date, and description |
| **Categories** | Food, Travel, Shopping, Education, Entertainment, Bills, Other |
| **History** | Search, filter by date and category, edit or delete entries |
| **Reports** | Daily, weekly, and monthly charts plus category-wise spending |
| **Budget** | Set a monthly budget and compare it with actual spending |
| **Alerts** | Warning at 80% of budget, error when exceeded, month-end reminder |
| **Export and Backup** | Excel, PDF, and database downloads, plus a local backup copy |

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** SQLite
- **Data handling:** Pandas
- **Charts and PDF:** Matplotlib
- **Excel export:** OpenPyXL

## Getting Started

### Prerequisites

- Python 3.9 or newer
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/expense-tracker.git
cd expense-tracker

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows (PowerShell)
source .venv/bin/activate         # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

> Start the app with `streamlit run app.py`. Running `python app.py` will not open the dashboard.

## Usage

1. Open the **Sign up** tab, create an account, and choose a security question.
2. Log in and set your monthly budget under **Budget**.
3. Log spending under **Add Expense**.
4. Check totals and charts on the **Dashboard**.
5. Use **History** to edit entries and **Reports** to analyze spending.
6. Use **Export** to download your data.

## Project Structure

```
expense-tracker/
├── app.py              # The full application
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
├── .gitignore          # Keeps local data out of Git
├── expenses.db         # Created on first run (not tracked)
└── backups/            # Created by local backups (not tracked)
```

## Data and Security

- All data stays on your machine in a local SQLite file.
- Passwords and security answers are stored as salted PBKDF2-SHA256 hashes.
- Each user only sees their own expenses and budgets.
- `expenses.db` is listed in `.gitignore` so your data is never pushed to GitHub.

## Known Limitations

- Alerts appear inside the app. There are no email or push notifications.
- Cloud backup is manual: sync the `backups/` folder with Google Drive or OneDrive.
- The PDF export lists the latest 40 expenses in a simple table.
- Password reset uses a security question because there is no email service.
- Amounts are shown in rupees (₹).

## Roadmap

- [ ] Email notifications for budget alerts and weekly summaries
- [ ] Automatic cloud backup
- [ ] Recurring expenses
- [ ] Per-category budgets
- [ ] Richer PDF reports with charts

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Could not open requirements file` | Check the spelling (`requirements.txt`) and that you are in the project folder |
| `File does not exist: app.py` | `cd` into the project folder first |
| `streamlit` is not recognized | Activate the virtual environment, then `pip install streamlit` |
| Port already in use | Run `streamlit run app.py --server.port 8502` |
