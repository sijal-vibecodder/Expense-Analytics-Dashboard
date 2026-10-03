"""Lusi-style Expense Tracker  |  run: streamlit run app.py"""
import hashlib, io, os, secrets, shutil, sqlite3
from datetime import date, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import streamlit as st

DB = "expenses.db"
CATS = ["Food", "Travel", "Shopping", "Education", "Entertainment", "Bills", "Other"]
BG, CARD, MINT, YELLOW, MUTED = "#1c1d21", "#2a2b30", "#6ee7a0", "#f5d84a", "#8b8d94"
COLORS = [MINT, YELLOW, "#5aa9e6", "#e67e7e", "#b48cf2", "#f2a65a", "#8b8d94"]

st.set_page_config("Lusi Expenses", "💸", layout="wide")
st.markdown(f"""<style>
.stApp{{background:{BG};color:#eee}} [data-testid=stSidebar]{{background:#232428}}
.card{{background:{CARD};border-radius:20px;padding:18px 22px;border:1px solid #38393f}}
.card small{{color:{MUTED}}} .big{{font-size:2rem;font-weight:700;margin:4px 0}}
.pro{{background:linear-gradient(135deg,{YELLOW},#d9b92e);color:#111;border-radius:20px;padding:18px 22px}}
.tx{{background:{CARD};border-radius:14px;padding:10px 14px;margin-bottom:8px;display:flex;justify-content:space-between}}
.tx span{{color:{MUTED};font-size:.8rem}} .amt{{color:{MINT};font-weight:600}}
.stButton>button{{background:{MINT};color:#111;border:0;border-radius:12px;font-weight:600}}
</style>""", unsafe_allow_html=True)

# ---------- database ----------
def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def init():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, salt TEXT, pw TEXT, question TEXT, answer TEXT);
        CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY, user_id INT, amount REAL, category TEXT, date TEXT, description TEXT);
        CREATE TABLE IF NOT EXISTS budgets(user_id INT, month TEXT, amount REAL, PRIMARY KEY(user_id, month));""")

def h(text, salt): return hashlib.pbkdf2_hmac("sha256", text.strip().lower().encode(), salt.encode(), 100_000).hex()

def q(sql, args=(), one=False, commit=False):
    with db() as c:
        cur = c.execute(sql, args)
        if commit: return cur.lastrowid
        r = cur.fetchall(); return (r[0] if r else None) if one else r

def expenses(uid):
    df = pd.DataFrame([dict(r) for r in q("SELECT * FROM expenses WHERE user_id=? ORDER BY date DESC, id DESC", (uid,))],
                      columns=["id", "user_id", "amount", "category", "date", "description"])
    df["date"] = pd.to_datetime(df["date"]); return df

# ---------- auth ----------
def auth_page():
    st.title("💸 Lusi Expenses")
    tab1, tab2, tab3 = st.tabs(["Log in", "Sign up", "Forgot password"])
    with tab1:
        u, p = st.text_input("Username", key="lu"), st.text_input("Password", type="password", key="lp")
        if st.button("Log in"):
            r = q("SELECT * FROM users WHERE username=?", (u.strip(),), one=True)
            if r and h(p, r["salt"]) == r["pw"]:
                st.session_state.uid, st.session_state.user = r["id"], r["username"]; st.rerun()
            else: st.error("Wrong username or password.")
    with tab2:
        u, p = st.text_input("Choose a username", key="su"), st.text_input("Choose a password (6+ characters)", type="password", key="sp")
        qn, an = st.text_input("Security question", "Name of your first school", key="sq"), st.text_input("Answer", key="sa")
        if st.button("Create account"):
            if len(u) < 3 or len(p) < 6 or not an: st.error("Fill every field: username 3+, password 6+ characters.")
            elif q("SELECT 1 FROM users WHERE username=?", (u.strip(),), one=True): st.error("That username is taken.")
            else:
                s = secrets.token_hex(8)
                q("INSERT INTO users(username,salt,pw,question,answer) VALUES(?,?,?,?,?)", (u.strip(), s, h(p, s), qn, h(an, s)), commit=True)
                st.success("Account created. Log in to continue.")
    with tab3:
        u = st.text_input("Username", key="fu")
        r = q("SELECT * FROM users WHERE username=?", (u.strip(),), one=True) if u else None
        if r:
            st.caption(f"Security question: {r['question']}")
            an, np_ = st.text_input("Answer", key="fa"), st.text_input("New password", type="password", key="fn")
            if st.button("Reset password"):
                if h(an, r["salt"]) == r["answer"] and len(np_) >= 6:
                    q("UPDATE users SET pw=? WHERE id=?", (h(np_, r["salt"]), r["id"]), commit=True); st.success("Password updated.")
                else: st.error("Wrong answer, or the new password is under 6 characters.")

# ---------- charts ----------
def style(ax, fig):
    fig.patch.set_alpha(0); ax.set_facecolor("none")
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(colors=MUTED); ax.yaxis.label.set_color(MUTED)

def week_chart(df):
    days = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
    vals = [df[df.date.dt.date == d].amount.sum() for d in days]
    fig, ax = plt.subplots(figsize=(6, 3)); style(ax, fig)
    ax.bar([d.strftime("%a") for d in days], [max(vals + [1])] * 7, color="#34353a", width=.55)
    ax.bar([d.strftime("%a") for d in days], vals, color=["#3f7a5a" if v != max(vals) else MINT for v in vals], width=.55)
    ax.set_yticks([]); return fig

def donut(df):
    s = df.groupby("category").amount.sum()
    fig, ax = plt.subplots(figsize=(3.4, 3.4)); fig.patch.set_alpha(0)
    if s.empty: ax.text(.5, .5, "No data", ha="center", color=MUTED); ax.axis("off"); return fig
    ax.pie(s, colors=COLORS, startangle=90, wedgeprops=dict(width=.35, edgecolor=CARD))
    ax.text(0, 0, f"Total\n₹{s.sum():,.0f}", ha="center", va="center", color="white", fontsize=12); return fig

def pro_cards(c, title, value, sub=""):
    c.markdown(f'<div class="card"><small>{title}</small><div class="big">{value}</div><small>{sub}</small></div>', unsafe_allow_html=True)

# ---------- pages ----------
def month_info(uid, df):
    m = date.today().strftime("%Y-%m")
    b = q("SELECT amount FROM budgets WHERE user_id=? AND month=?", (uid, m), one=True)
    spent = df[df.date.dt.strftime("%Y-%m") == m].amount.sum()
    return m, (b["amount"] if b else 0.0), spent

def alerts(budget, spent):
    if budget and spent > budget: st.error(f"Budget exceeded by ₹{spent - budget:,.0f}.")
    elif budget and spent > .8 * budget: st.warning(f"You've used {spent / budget:.0%} of this month's budget.")
    if date.today().day >= 28: st.info("Month end is near. Open Reports to review this month.")

def dashboard(uid, df):
    m, budget, spent = month_info(uid, df)
    alerts(budget, spent)
    st.subheader(f"Welcome back, {st.session_state.user}")
    a, b, c = st.columns(3)
    pro_cards(a, "Total expenses (this month)", f"₹{spent:,.0f}")
    pro_cards(b, "Remaining budget", f"₹{budget - spent:,.0f}" if budget else "Not set", f"Budget ₹{budget:,.0f}" if budget else "Set one in Budget")
    c.markdown('<div class="pro"><b>Weekly summary</b><div class="big">₹%s</div>spent in the last 7 days</div>'
               % f"{df[df.date >= pd.Timestamp(date.today() - timedelta(days=6))].amount.sum():,.0f}", unsafe_allow_html=True)
    l, r = st.columns([2, 1])
    with l:
        st.markdown("##### Spending in the last 7 days"); st.pyplot(week_chart(df))
    with r:
        st.markdown("##### Spending by category"); st.pyplot(donut(df[df.date.dt.strftime("%Y-%m") == m]))
    st.markdown("##### Recent transactions")
    if df.empty: st.info("No expenses yet. Open Add Expense to log your first one.")
    for _, x in df.head(6).iterrows():
        st.markdown(f'<div class="tx"><div>{x.description or x.category}<br><span>{x.category} · {x.date:%d %b %Y}</span></div>'
                    f'<div class="amt">-₹{x.amount:,.2f}</div></div>', unsafe_allow_html=True)

def add_page(uid):
    st.subheader("Add expense")
    with st.form("add", clear_on_submit=True):
        amt = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
        cat, d = st.selectbox("Category", CATS), st.date_input("Date", date.today())
        desc = st.text_input("Description")
        if st.form_submit_button("Save expense"):
            if amt <= 0: st.error("Enter an amount above 0.")
            else:
                q("INSERT INTO expenses(user_id,amount,category,date,description) VALUES(?,?,?,?,?)", (uid, amt, cat, str(d), desc), commit=True)
                st.success("Expense saved.")

def history_page(uid, df):
    st.subheader("Expense history")
    a, b, c = st.columns(3)
    s = a.text_input("Search description"); cats = b.multiselect("Category", CATS)
    rng = c.date_input("Date range", (date.today() - timedelta(days=90), date.today()))
    f = df.copy()
    if s: f = f[f.description.str.contains(s, case=False, na=False)]
    if cats: f = f[f.category.isin(cats)]
    if len(rng) == 2: f = f[(f.date.dt.date >= rng[0]) & (f.date.dt.date <= rng[1])]
    ed = st.data_editor(f[["id", "date", "category", "amount", "description"]], num_rows="dynamic", hide_index=True, disabled=["id"],
                        column_config={"category": st.column_config.SelectboxColumn(options=CATS)}, use_container_width=True)
    if st.button("Save changes"):
        keep = set(ed.id.dropna().astype(int))
        for i in set(f.id) - keep: q("DELETE FROM expenses WHERE id=? AND user_id=?", (int(i), uid), commit=True)
        for _, x in ed.dropna(subset=["id"]).iterrows():
            q("UPDATE expenses SET amount=?,category=?,date=?,description=? WHERE id=? AND user_id=?",
              (x.amount, x.category, str(pd.to_datetime(x.date).date()), x.description, int(x.id), uid), commit=True)
        st.success("Changes saved."); st.rerun()

def reports_page(df):
    st.subheader("Reports")
    if df.empty: st.info("Add expenses to see reports."); return
    per = st.radio("Period", ["Daily", "Weekly", "Monthly"], horizontal=True)
    rule = {"Daily": "D", "Weekly": "W", "Monthly": "M"}[per]
    t = df.set_index("date").amount.resample(rule).sum().tail(12)
    fig, ax = plt.subplots(figsize=(8, 3)); style(ax, fig)
    ax.bar(t.index.strftime("%d %b" if rule != "M" else "%b %Y"), t.values, color=MINT); plt.xticks(rotation=45)
    st.pyplot(fig)
    cat = df.groupby("category").amount.sum().sort_values()
    fig, ax = plt.subplots(figsize=(8, 3)); style(ax, fig)
    ax.barh(cat.index, cat.values, color=YELLOW); ax.tick_params(colors="white"); st.pyplot(fig)
    st.caption(f"Top category: {cat.index[-1]} (₹{cat.iloc[-1]:,.0f}). Average per day: ₹{df.groupby(df.date.dt.date).amount.sum().mean():,.0f}.")

def budget_page(uid, df):
    m, budget, spent = month_info(uid, df)
    st.subheader(f"Budget for {m}")
    nb = st.number_input("Monthly budget (₹)", min_value=0.0, value=float(budget), step=500.0)
    if st.button("Save budget"):
        q("INSERT OR REPLACE INTO budgets VALUES(?,?,?)", (uid, m, nb), commit=True); st.rerun()
    if budget:
        st.progress(min(spent / budget, 1.0), f"₹{spent:,.0f} of ₹{budget:,.0f} used")
        st.dataframe(pd.DataFrame({"Budget": [budget], "Actual": [spent], "Difference": [budget - spent]}), hide_index=True)
    alerts(budget, spent)

def export_page(uid, df):
    st.subheader("Export and backup")
    out = df.drop(columns="user_id")
    x = io.BytesIO(); out.to_excel(x, index=False, engine="openpyxl")
    st.download_button("Download Excel", x.getvalue(), "expenses.xlsx")
    p = io.BytesIO()
    with PdfPages(p) as pdf:
        fig, ax = plt.subplots(figsize=(8.3, 11.7)); ax.axis("off")
        ax.set_title(f"Expense report: {date.today():%d %b %Y}  |  Total ₹{out.amount.sum():,.2f}")
        top = out.head(40).assign(date=out.head(40).date.dt.strftime("%Y-%m-%d"))
        if not top.empty: ax.table(cellText=top.values, colLabels=top.columns, loc="upper center").auto_set_font_size(True)
        pdf.savefig(fig)
    st.download_button("Download PDF", p.getvalue(), "expenses.pdf")
    st.download_button("Download database backup", open(DB, "rb").read(), f"backup_{date.today()}.db")
    if st.button("Save local backup copy"):
        os.makedirs("backups", exist_ok=True); shutil.copy(DB, f"backups/backup_{date.today()}.db"); st.success("Saved to the backups folder.")
    st.caption("For cloud backup, point the backups folder at Google Drive or OneDrive sync.")

# ---------- main ----------
init()
if "uid" not in st.session_state: auth_page(); st.stop()
uid = st.session_state.uid; df = expenses(uid)
with st.sidebar:
    st.markdown("### 🟨 Lusi")
    page = st.radio("Menu", ["Dashboard", "Add Expense", "History", "Reports", "Budget", "Export"], label_visibility="collapsed")
    if st.button("Log out"): st.session_state.clear(); st.rerun()
{"Dashboard": lambda: dashboard(uid, df), "Add Expense": lambda: add_page(uid), "History": lambda: history_page(uid, df),
 "Reports": lambda: reports_page(df), "Budget": lambda: budget_page(uid, df), "Export": lambda: export_page(uid, df)}[page]()
