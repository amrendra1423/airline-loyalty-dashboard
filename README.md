# ✈️ Airline Loyalty Retention Dashboard

A data-driven solution to identify at-risk loyalty members, segment the customer base, and deliver specific retention actions — built for the Business Analytics team of a mid-sized Canadian airline.

---

## 📁 Project Files

| File | Description |
|---|---|
| `app.py` | Streamlit dashboard app |
| `requirements.txt` | Python dependencies |
| `master_scored.csv` | 14,670 members scored with churn probability, segment, and future value score |
| `Loyalty_Retention_Report.docx` | 7-section technical report (6–8 pages) |
| `Loyalty_Retention_Dashboard.html` | Standalone HTML dashboard (no install needed) |

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 🌐 Deploy on Streamlit Cloud

1. Push this repo to GitHub (must be public)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. New app → select this repo → set main file to `app.py` → Deploy

---

## 📊 Dashboard Pages

| Page | What it shows |
|---|---|
| **Overview** | KPI tiles, risk distribution, segment composition, card-tier chart, province table, churn vs. value scatter |
| **Segments** | Profile cards for all 5 segments with embedded retention actions |
| **Risk Watch List** | All 446 members with churn prob > 10%, filterable, downloadable as CSV |
| **Member Lookup** | Search any loyalty number — full profile, risk meter, recommended action |
| **Retention Playbook** | 5 segment-specific interventions with trigger, action, channel, and KPI |

---

## 🧠 Methodology

### Data
- **Source:** 4 files — Customer Loyalty History, Customer Flight Activity, Calendar, Data Dictionary
- **Members:** 16,737 Canadian loyalty members, 2012–2018
- **Activity window:** Monthly flight data for 2017–2018

### Churn Definition
Churn = **formal cancellation** OR **zero flights** in the label window.
Purely cancellation-based labels miss ~60% of actual disengagement.

### Model
- **Type:** Gradient Boosted Machine (300 trees, depth 3) + Logistic Regression blend (70/30)
- **Test AUC:** 0.82
- **Leakage prevention:** Features built from Jan–Dec 2017; labels from Jan–Jun 2018 (strict temporal split)
- **Top drivers:** Tenure (49%), Recency (17%), Salary (9%), Recent flights (11%)

### Segmentation
K-means clustering (k=5) on 11 behavioural + demographic features:

| Segment | Members | Avg Flights/yr | Avg Churn Prob |
|---|---|---|---|
| Champions | 612 | 56.0 | 3.7% |
| Loyalists | 5,335 | 22.9 | 3.5% |
| Steady Flyers | 5,465 | 16.8 | 3.7% |
| Casual / Emerging | 2,589 | 10.6 | 5.9% |
| At-Risk Lapsed | 669 | 0.0 | 26.5% |

### Future Value Score
Forward-looking composite score (0–1) combining flight trajectory, expected points accumulation discounted by churn probability, historical CLV, and salary. Replaces CLV as the primary member value metric.

---

## 🎯 Key Findings

- **348 members** are high/critical risk (churn prob > 25%)
- **At-Risk Lapsed** members have the highest historical CLV ($8,118 avg) but zero current activity — CLV alone would classify them as safe
- **Tenure and recency** drive 66% of churn signal; card tier matters far less than behavioural signals
- **1,570 members** have quietly disengaged (zero flights) without formally cancelling — invisible to standard reporting

---

## 💡 Top 3 Recommendations

1. **Win-back campaign for At-Risk Lapsed** (669 members) — 3-step email sequence triggered at 90 days of inactivity. Target 15% re-activation = ~100 members recovered at avg CLV $8,118.

2. **First-Year Habit Formation programme** for Casual/Emerging members (2,589 members) — structured challenge in months 1–12 to form the flying habit before churn risk peaks.

3. **Replace CLV with Future Value Score** as the programme's core performance metric — it correctly identifies who is likely to remain valuable, not just who has been valuable historically.

---

## 🛠️ Tech Stack

- **Modelling:** Pure NumPy/Pandas (custom GBM + Logistic Regression — no sklearn dependency)
- **Dashboard:** Streamlit + Plotly
- **Report:** docx (Node.js)
- **Data processing:** Python, Pandas

---

## 📬 Contact

Business Analytics Team — Summer Projects 2026
