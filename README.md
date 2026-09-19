# Groww Review Pulse — LIP 5

A Streamlit prototype that turns public app-store reviews into a weekly product pulse.

## Flow
1. Import a public CSV with `source,date,rating,title,text,record_type,source_url`.
2. Remove obvious PII from review text.
3. Assign each review to one of five fixed themes.
4. Filter a 7-day weekly window.
5. Generate top themes, representative quotes, action ideas and an email draft.
6. Download the weekly note and email draft.

## Five-theme legend
- Funds, KYC & Account Access
- Orders & Trading
- App Experience & Reliability
- Support & Communications
- Product Requests

## Demo data
The bundled demo corpus contains **5 public review excerpts** and **26 clearly labeled synthetic/redacted rows** spanning 8–12 weeks. Synthetic rows are included only to demonstrate the end-to-end weekly workflow. They must not be presented as real user reviews.

The public rows are from publicly visible Groww Google Play/App Store review pages. Usernames, emails and IDs are excluded.

## Rerun
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Submission note
For a production-like run, replace `data/reviews_demo.csv` with a public review export/feed covering the latest 8–12 weeks. Do not scrape behind logins and do not include usernames, emails or IDs.
