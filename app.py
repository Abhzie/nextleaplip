import re
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Groww — Weekly Review Pulse", page_icon="📊", layout="wide")

THEMES = [
    "Funds, KYC & Account Access",
    "Orders & Trading",
    "App Experience & Reliability",
    "Support & Communications",
    "Product Requests",
]

THEME_RULES = {
    "Funds, KYC & Account Access": ["kyc","rek yc","account","withdraw","withdrawal","redeem","credit","bank","login","frozen","verification"],
    "Orders & Trading": ["order","trade","trading","execution","profit/loss","stop loss","sl","target","f&o","fno","position"],
    "App Experience & Reliability": ["slow","lag","stuck","crash","loading","update","performance","speed","login issue"],
    "Support & Communications": ["support","ticket","notification","email","response","follow-up","chat"],
    "Product Requests": ["goal","tracker","tracking","filter","dashboard","feature","reminder","controls","suggest","wish","would be great","more filters"],
}

DATA_PATH = Path(__file__).parent / "data" / "reviews_demo.csv"

def clean_text(x):
    x = str(x)
    x = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[redacted email]', x)
    x = re.sub(r'@\w+', '[redacted handle]', x)
    x = re.sub(r'\+?\d[\d\s\-]{7,}\d', '[redacted phone]', x)
    return x.strip()

def classify(text):
    t = text.lower()
    scores = {theme: sum(1 for kw in kws if kw in t) for theme, kws in THEME_RULES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "App Experience & Reliability"

def load_demo():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df["text"] = df["text"].map(clean_text)
    df["theme"] = df["text"].map(classify)
    return df

st.title("Groww — Weekly Review Pulse")
st.caption("LIP 5 prototype · public review CSV → PII-safe cleaning → themes → quotes → actions → email draft")

with st.sidebar:
    st.header("Weekly run")
    uploaded = st.file_uploader("Upload public review export CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.success("Using uploaded CSV")
        df["date"] = pd.to_datetime(df["date"])
        for c in ["title","text","source","record_type","source_url"]:
            if c not in df.columns: df[c] = ""
        df["text"] = df["text"].map(clean_text)
        df["theme"] = df["text"].map(classify)
    else:
        df = load_demo()
        st.info("Demo corpus: 5 public reviews + 26 clearly labeled synthetic/redacted rows. Replace with a public export for a real run.")

    latest = df["date"].max()
    default_end = latest.date()
    week_end = st.date_input("Week ending", value=default_end)
    week_end = pd.Timestamp(week_end)
    week_start = week_end - pd.Timedelta(days=6)
    week_df = df[(df["date"] >= week_start) & (df["date"] <= week_end)].copy()

st.metric("Reviews in selected week", len(week_df))
st.caption(f"Window: {week_start.date()} → {week_end.date()} · Corpus: {len(df)} reviews · Sources: {df['source'].replace({'google_play':'Google Play','app_store':'App Store'}).nunique()}")

# If the chosen week has fewer than 3 reviews, offer the latest populated week automatically.
if len(week_df) < 3:
    st.warning("Selected week has fewer than 3 reviews. The demo can still run, but a weekly pulse is more useful with 3+ reviews.")

st.subheader("Top 3 themes")
theme_counts = week_df["theme"].value_counts().head(3)
if theme_counts.empty:
    st.write("No reviews in this week.")
else:
    for i, (theme, count) in enumerate(theme_counts.items(), 1):
        st.markdown(f"**{i}. {theme}** — {count} review(s)")

st.subheader("3 user quotes")
public_week = week_df[week_df["record_type"].fillna("").eq("public")].copy()
quote_pool = public_week.sort_values(["rating","date"], ascending=[True, False]).head(3)
if len(quote_pool) < 3:
    extra = week_df[~week_df.index.isin(quote_pool.index)].sort_values("date", ascending=False)
    quote_pool = pd.concat([quote_pool, extra]).head(3)

if quote_pool.empty:
    st.write("No reviews available.")
else:
    for _, r in quote_pool.iterrows():
        label = "PUBLIC" if str(r.get("record_type","")) == "public" else "DEMO/REDACTED"
        st.markdown(f'> “{r["text"]}”  \n> — {int(r["rating"])}★ · {r["source"].replace("_"," ").title()} · {r["date"].date()} · **{label}**')

st.subheader("3 action ideas")
actions = [
    ("Reliability", "Instrument withdrawal/order flows with clear status states and expected completion timing."),
    ("Support", "Add visible ticket progress and reduce repeat-information loops in support journeys."),
    ("Product request", "Test goal-wise portfolio tracking with configurable buckets for retirement, education and wealth creation."),
]
for title, body in actions:
    st.markdown(f"**• {title}:** {body}")

st.subheader("One-page weekly pulse")
note = f"""# Groww — Weekly Review Pulse
**Week:** {week_start.date()} to {week_end.date()}  
**Reviews:** {len(week_df)} · **Public + demo/redacted corpus**

## Top themes
{chr(10).join([f"- {t}: {c} review(s)" for t,c in theme_counts.items()])}

## User quotes
{chr(10).join([f'- “{r["text"]}” — {int(r["rating"])}★, {r["source"]}, {r["date"].date()}' for _,r in quote_pool.iterrows()])}

## Action ideas
- Instrument withdrawal/order flows with clear status and expected completion timing.
- Add visible support-ticket progress and reduce repeat-information loops.
- Test goal-wise portfolio tracking with configurable buckets.

**Data note:** Demo rows are explicitly labeled synthetic/redacted. Public quotes are taken from publicly visible store reviews; no usernames, emails or IDs are included.
"""
st.download_button("Download weekly pulse (Markdown)", note, file_name="groww_weekly_pulse.md")

email = f"""Subject: Groww weekly review pulse — {week_end.date()}

Hi team,

Here is this week's review pulse for {week_start.date()} to {week_end.date()}.

Top themes:
{chr(10).join([f"- {t}: {c}" for t,c in theme_counts.items()])}

Action ideas:
- Instrument withdrawal/order flows with clear status and expected completion timing.
- Add visible support-ticket progress and reduce repeat-information loops.
- Test goal-wise portfolio tracking with configurable buckets.

See the attached/exported weekly pulse for representative review excerpts.

Best,
Product Insights
"""
st.download_button("Download email draft", email, file_name="groww_email_draft.txt")

st.caption("Theme legend: Funds/KYC & Account Access · Orders & Trading · App Experience & Reliability · Support & Communications · Product Requests")
