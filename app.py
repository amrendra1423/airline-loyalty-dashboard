"""
Airline Loyalty Retention Dashboard — Streamlit App
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Loyalty Retention Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px 18px;
    }
    div[data-testid="metric-container"] label {
        color: #94A3B8 !important;
        font-size: 12px !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #F1F5F9 !important;
    }
</style>
""", unsafe_allow_html=True)

SEG_COLORS = {
    "Champions":        "#6C63FF",
    "Loyalists":        "#0EA5E9",
    "Steady Flyers":    "#10B981",
    "Casual / Emerging":"#F59E0B",
    "At-Risk Lapsed":   "#EF4444",
}
RISK_COLORS = {
    "Low":      "#10B981",
    "Medium":   "#F59E0B",
    "High":     "#EF4444",
    "Critical": "#991B1B",
}

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    here = Path(__file__).parent
    df = pd.read_csv(here / "master_scored.csv")
    df["risk_band"] = pd.cut(
        df["churn_prob"],
        bins=[-0.001, 0.10, 0.25, 0.50, 1.01],
        labels=["Low", "Medium", "High", "Critical"],
    )
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/ios/50/6C63FF/airport.png", width=48)
st.sidebar.title("✈️ Loyalty Retention")
st.sidebar.markdown("**14,670 members scored**  \n2018 · GBM + Logit blend · AUC 0.82")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "👥 Segments", "🚨 Risk Watch List", "🔍 Member Lookup", "📋 Retention Playbook"],
)

st.sidebar.divider()
st.sidebar.markdown("**Quick filters**")
selected_segs = st.sidebar.multiselect(
    "Segments", df["segment_name"].unique().tolist(), default=df["segment_name"].unique().tolist()
)
selected_cards = st.sidebar.multiselect(
    "Card tier", df["Loyalty Card"].unique().tolist(), default=df["Loyalty Card"].unique().tolist()
)

dff = df[df["segment_name"].isin(selected_segs) & df["Loyalty Card"].isin(selected_cards)]

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.title("📊 Overview")

    # KPIs
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Members Scored", f"{len(dff):,}")
    k2.metric("High/Critical Risk", f"{(dff.churn_prob > 0.25).sum():,}", delta="need action", delta_color="inverse")
    k3.metric("Medium Risk (10–25%)", f"{((dff.churn_prob > 0.10) & (dff.churn_prob <= 0.25)).sum():,}")
    k4.metric("Mean Churn Prob", f"{dff.churn_prob.mean()*100:.1f}%")
    k5.metric("Avg CLV", f"${dff.CLV.mean():,.0f}")
    k6.metric("Model AUC", "0.82", delta="test set")

    st.divider()

    col1, col2 = st.columns(2)

    # Risk donut
    with col1:
        st.subheader("Churn Risk Distribution")
        risk_counts = dff["risk_band"].value_counts().reindex(["Low", "Medium", "High", "Critical"]).fillna(0)
        fig = go.Figure(go.Pie(
            labels=risk_counts.index,
            values=risk_counts.values,
            hole=0.55,
            marker_colors=[RISK_COLORS[r] for r in risk_counts.index],
            textinfo="label+percent",
            hovertemplate="%{label}: %{value:,} members<extra></extra>",
        ))
        fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#94A3B8", legend=dict(font_color="#94A3B8"))
        st.plotly_chart(fig, use_container_width=True)

    # Segment donut
    with col2:
        st.subheader("Segment Composition")
        seg_counts = dff["segment_name"].value_counts().reindex(list(SEG_COLORS.keys())).fillna(0)
        fig2 = go.Figure(go.Pie(
            labels=seg_counts.index,
            values=seg_counts.values,
            hole=0.55,
            marker_colors=[SEG_COLORS[s] for s in seg_counts.index],
            textinfo="label+percent",
            hovertemplate="%{label}: %{value:,}<extra></extra>",
        ))
        fig2.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#94A3B8", legend=dict(font_color="#94A3B8"))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    # Card tier bar
    with col3:
        st.subheader("Avg Flights / Year by Card Tier")
        card_stats = dff.groupby("Loyalty Card")["flights_12m"].mean().reset_index()
        fig3 = px.bar(card_stats, x="Loyalty Card", y="flights_12m",
                      color="Loyalty Card",
                      color_discrete_map={"Aurora":"#6C63FF","Nova":"#0EA5E9","Star":"#10B981"},
                      labels={"flights_12m":"Avg Flights/yr"},
                      text_auto=".1f")
        fig3.update_layout(height=280, showlegend=False,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#94A3B8", xaxis=dict(color="#94A3B8"),
                           yaxis=dict(color="#94A3B8", gridcolor="#334155"))
        st.plotly_chart(fig3, use_container_width=True)

    # Province table
    with col4:
        st.subheader("Top Provinces — Members & Avg Churn Risk")
        prov = (dff.groupby("Province")
                .agg(Members=("Loyalty Number","count"), Avg_Churn=("churn_prob","mean"))
                .sort_values("Members", ascending=False).head(10)
                .reset_index())
        prov["Avg Churn %"] = (prov["Avg_Churn"] * 100).round(1).astype(str) + "%"
        st.dataframe(
            prov[["Province","Members","Avg Churn %"]],
            use_container_width=True, hide_index=True, height=280,
        )

    st.divider()
    st.subheader("Churn Probability vs. Future Value Score")
    fig_scatter = px.scatter(
        dff.sample(min(3000, len(dff)), random_state=42),
        x="future_value_score", y="churn_prob",
        color="segment_name",
        color_discrete_map=SEG_COLORS,
        hover_data=["Loyalty Number","Loyalty Card","flights_12m","CLV"],
        labels={"future_value_score":"Future Value Score","churn_prob":"Churn Probability","segment_name":"Segment"},
        opacity=0.65, size_max=6,
    )
    fig_scatter.update_layout(
        height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94A3B8",
        xaxis=dict(color="#94A3B8", gridcolor="#334155"),
        yaxis=dict(color="#94A3B8", gridcolor="#334155"),
        legend=dict(font_color="#94A3B8"),
    )
    fig_scatter.add_hline(y=0.25, line_dash="dash", line_color="#EF4444",
                          annotation_text="High-risk threshold (25%)", annotation_font_color="#EF4444")
    st.plotly_chart(fig_scatter, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SEGMENTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Segments":
    st.title("👥 Segment Profiles")

    ICONS = {"Champions":"🏆","Loyalists":"💙","Steady Flyers":"✈️",
             "Casual / Emerging":"🌱","At-Risk Lapsed":"🚨"}
    ACTIONS = {
        "Champions": ("Early tier upgrade + milestone challenge",
            "Fast-track to Aurora. Offer a challenge: fly 10× in 90 days → Aurora + 50,000 bonus points. Assign a dedicated loyalty concierge.",
            "Within 30 days of segment entry", "Push + personalized email"),
        "Loyalists": ("Redemption amplifier + anniversary reward",
            "Offer 2× points redemption value weekends quarterly. Anniversary message with 500 bonus pts. Lounge access trial for top members.",
            "Quarterly + on membership anniversary", "Email + app notification"),
        "Steady Flyers": ("Route-specific frequency nudge",
            "Identify top 2–3 routes and offer 3× points on those routes for 60 days. Progress tracker showing flights to next tier.",
            "Start of Q1 and Q3", "Personalized email with route data"),
        "Casual / Emerging": ("First-Year Habit Formation Challenge",
            "Fly 3× in next 6 months → unlock Silver benefits early. Monthly points summaries. Double value on first redemption.",
            "Within first 6 months of enrollment", "Email sequence (months 3, 5, 8, 12)"),
        "At-Risk Lapsed": ("3-step win-back sequence",
            "Week 1: 'We miss you' + 3× bonus pts. Week 3: Route-specific offer (e.g. YYC–YUL $189 + 5,000 pts). Week 6: Points expiry warning + 20% off. No response: flag dormant.",
            "Trigger: 90 days since last flight", "Email (wks 1, 3, 6) + SMS"),
    }

    for sn in ["Champions","Loyalists","Steady Flyers","Casual / Emerging","At-Risk Lapsed"]:
        if sn not in selected_segs:
            continue
        sub = dff[dff.segment_name == sn]
        color = SEG_COLORS[sn]
        act = ACTIONS[sn]

        with st.container(border=True):
            hcol, _ = st.columns([5, 1])
            with hcol:
                st.markdown(f"### {ICONS[sn]} <span style='color:{color}'>{sn}</span> &nbsp; <span style='font-size:14px;color:#94A3B8'>{len(sub):,} members · {len(sub)/len(df)*100:.1f}% of base</span>",
                            unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Avg Flights / yr", f"{sub.flights_12m.mean():.1f}")
            m2.metric("Avg CLV", f"${sub.CLV.mean():,.0f}")
            m3.metric("Avg Churn Prob", f"{sub.churn_prob.mean()*100:.1f}%")
            m4.metric("Avg Future Value", f"{sub.future_value_score.mean():.3f}")

            st.markdown(f"""
            <div style='background:#1a1f2e;border-left:3px solid {color};border-radius:6px;padding:12px 16px;margin-top:10px'>
                <div style='font-size:11px;color:#94A3B8;text-transform:uppercase;font-weight:600;margin-bottom:5px'>Recommended Action</div>
                <div style='font-size:15px;font-weight:700;color:#F1F5F9;margin-bottom:8px'>{act[0]}</div>
                <div style='font-size:13px;color:#CBD5E1;line-height:1.6'>{act[1]}</div>
                <div style='margin-top:10px;font-size:12px;color:#64748B'>
                    ⏱ {act[2]} &nbsp;&nbsp; 📧 {act[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — RISK WATCH LIST
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🚨 Risk Watch List":
    st.title("🚨 Risk Watch List")
    st.caption("Members with churn probability > 10%, sorted by risk. Prioritise High-Value members (CLV > $5,000).")

    risk_df = dff[dff.churn_prob > 0.10].sort_values("churn_prob", ascending=False).copy()

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    min_prob = fc1.slider("Min churn prob %", 10, 50, 10, step=5) / 100
    min_fv   = fc2.slider("Min future value score", 0.0, 1.0, 0.0, step=0.05)
    sort_by  = fc3.selectbox("Sort by", ["Churn Prob ↓", "Future Value ↓", "CLV ↓"])

    risk_df = risk_df[risk_df.churn_prob >= min_prob]
    risk_df = risk_df[risk_df.future_value_score >= min_fv]

    if sort_by == "Future Value ↓":
        risk_df = risk_df.sort_values("future_value_score", ascending=False)
    elif sort_by == "CLV ↓":
        risk_df = risk_df.sort_values("CLV", ascending=False)

    st.markdown(f"**{len(risk_df):,} members match filters**")

    PLAY = {"At-Risk Lapsed":"Win-back sequence","Casual / Emerging":"Habit formation",
            "Steady Flyers":"Frequency nudge","Champions":"Tier upgrade","Loyalists":"Redemption amplifier"}

    display = risk_df[["Loyalty Number","segment_name","Loyalty Card","Province",
                        "churn_prob","future_value_score","flights_12m","CLV","tenure_months"]].copy()
    display["churn_prob"] = (display["churn_prob"] * 100).round(1).astype(str) + "%"
    display["future_value_score"] = display["future_value_score"].round(3)
    display["CLV"] = display["CLV"].round(0).astype(int)
    display["tenure_months"] = display["tenure_months"].round(0).astype(int)
    display["Action"] = display["segment_name"].map(PLAY)
    display.columns = ["Loyalty #","Segment","Card","Province",
                       "Churn Prob","Future Value","Flights/yr","CLV ($)","Tenure (mo)","Action"]

    def highlight_risk(val):
        if isinstance(val, str) and "%" in val:
            p = float(val.replace("%",""))
            if p > 50: return "color: #EF4444; font-weight: bold"
            if p > 25: return "color: #F97316; font-weight: bold"
            if p > 10: return "color: #F59E0B"
        return ""

    st.dataframe(
        display.style.map(highlight_risk, subset=["Churn Prob"]),
        use_container_width=True, hide_index=True, height=560,
    )

    st.download_button(
        "⬇️ Download risk list as CSV",
        data=risk_df.to_csv(index=False),
        file_name="risk_watch_list.csv",
        mime="text/csv",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — MEMBER LOOKUP
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Member Lookup":
    st.title("🔍 Member Lookup")

    col_in, _ = st.columns([2, 3])
    with col_in:
        query = st.text_input("Enter Loyalty Number", placeholder="e.g. 100018, 100590, 101902")

    if query.strip():
        try:
            ln = int(query.strip())
            row = df[df["Loyalty Number"] == ln]
        except ValueError:
            row = pd.DataFrame()

        if row.empty:
            st.error("Member not found.")
        else:
            m = row.iloc[0]
            color = SEG_COLORS.get(m["segment_name"], "#6C63FF")
            prob  = m["churn_prob"] * 100
            prob_color = "#EF4444" if prob > 25 else "#F59E0B" if prob > 10 else "#10B981"

            st.markdown(f"""
            <div style='font-size:22px;font-weight:700;margin-bottom:8px'>
                Member #{int(m['Loyalty Number'])} &nbsp;
                <span style='color:{prob_color}'>Churn Risk: {prob:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)

            # Risk meter
            st.progress(min(prob / 100, 1.0))
            st.caption("← Low risk &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; High risk →")

            st.divider()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Segment", m["segment_name"])
            c2.metric("Loyalty Card", m["Loyalty Card"])
            c3.metric("Future Value Score", f"{m['future_value_score']:.3f}")
            c4.metric("Risk Band", str(m["risk_band"]))

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Flights (12 mo)", int(m["flights_12m"]))
            c6.metric("Active Months / 12", int(m["active_months"]))
            c7.metric("Points Accumulated", f"{int(m.get('pts_acc_12m', 0)):,}")
            c8.metric("Points Redeemed", f"{int(m.get('pts_red_12m', 0)):,}")

            c9, c10, c11, c12 = st.columns(4)
            c9.metric("Lifetime CLV", f"${m['CLV']:,.0f}")
            c10.metric("Tenure (months)", int(m["tenure_months"]))
            c11.metric("Province", m.get("Province","—"))
            c12.metric("Annual Salary", f"${int(m.get('Salary', 0)):,}")

            st.divider()

            ACTIONS = {
                "Champions": ("Early tier upgrade + milestone challenge",
                    "Fast-track to Aurora. Offer: fly 10× in 90 days → Aurora + 50,000 bonus points.",
                    "Within 30 days","Push + email"),
                "Loyalists": ("Redemption amplifier + anniversary reward",
                    "2× redemption weekends quarterly. Anniversary message + 500 pts. Lounge trial.",
                    "Quarterly + anniversary","Email + app"),
                "Steady Flyers": ("Route-specific frequency nudge",
                    "3× points on top 2–3 routes for 60 days. Progress tracker to next tier.",
                    "Q1 and Q3","Personalized email"),
                "Casual / Emerging": ("First-Year Habit Formation Challenge",
                    "Fly 3× in 6 months → Silver benefits early. Double value on first redemption.",
                    "First 6 months","Email sequence"),
                "At-Risk Lapsed": ("3-step win-back sequence",
                    "Wk 1: 'We miss you' + 3× pts. Wk 3: Route offer. Wk 6: Last-chance + 20% off.",
                    "90 days since last flight","Email + SMS"),
            }
            act = ACTIONS.get(m["segment_name"], ("Review", "Manual review recommended.", "—", "—"))

            st.markdown(f"""
            <div style='background:#1a1f2e;border-left:3px solid {color};border-radius:8px;padding:14px 18px'>
                <div style='font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase;margin-bottom:6px'>Recommended Action</div>
                <div style='font-size:16px;font-weight:700;color:#F1F5F9;margin-bottom:8px'>{act[0]}</div>
                <div style='font-size:13px;color:#CBD5E1;line-height:1.6'>{act[1]}</div>
                <div style='margin-top:10px;font-size:12px;color:#64748B'>⏱ {act[2]} &nbsp;&nbsp; 📧 {act[3]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Enter a loyalty number above to look up a member's full profile and recommended action.")
        st.caption("Try: 100018 · 100590 · 101902")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — PLAYBOOK
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Retention Playbook":
    st.title("📋 Retention Playbook")
    st.caption("Specific interventions for each segment — who, when, what, channel, and KPI.")

    PLAYBOOK = {
        "Champions 🏆": {
            "color":"#6C63FF",
            "target":"612 high-frequency members, avg 9 months tenure",
            "trigger":"Segment entry (top 5% of flights)",
            "action":"Fast-track to Aurora card. Milestone challenge: fly 10× in 90 days → Aurora + 50,000 bonus points. Top 50 members by Future Value Score get a dedicated loyalty concierge.",
            "timing":"Within 30 days of segment entry",
            "channel":"Push notification + personalised email",
            "kpi":"Aurora conversion rate · 90-day retention rate",
        },
        "Loyalists 💙": {
            "color":"#0EA5E9",
            "target":"5,335 long-tenure members (avg 41 mo), highest redemption rate",
            "trigger":"Quarterly calendar event + membership anniversary",
            "action":"Offer 2× points redemption value weekends once per quarter. Loyalty anniversary message with personalised year-in-review + 500-point bonus. Invite top 20% (by FVS) to lounge access trial.",
            "timing":"Quarterly + on membership anniversary date",
            "channel":"Email + in-app notification",
            "kpi":"Redemption rate · quarterly flight frequency",
        },
        "Steady Flyers ✈️": {
            "color":"#10B981",
            "target":"5,465 long-tenure members (avg 51 mo), moderate activity",
            "trigger":"Start of Q1 and Q3 each year",
            "action":"Identify member's top 2–3 historical routes. Offer 3× bonus points on those routes for 60 days. Include visual progress tracker: flights needed to reach the next loyalty tier.",
            "timing":"Q1 (January) and Q3 (July) launch",
            "channel":"Personalised email with route-level data",
            "kpi":"Flights in next 90 days vs prior 90 days · tier upgrade rate",
        },
        "Casual / Emerging 🌱": {
            "color":"#F59E0B",
            "target":"2,589 newer members (avg 13 mo tenure), habit not yet formed",
            "trigger":"Enrollment + months 3, 5, 8, 12 milestones",
            "action":"First-Year Habit Formation Challenge: fly 3× in next 6 months → Silver benefits unlocked early. Monthly points summaries. Double redemption value on first redemption (capped 5,000 pts).",
            "timing":"Triggered by enrollment + ongoing milestone emails",
            "channel":"Email sequence (months 3, 5, 8, 12)",
            "kpi":"6-month flight completion rate · first redemption rate",
        },
        "At-Risk Lapsed 🚨": {
            "color":"#EF4444",
            "target":"669 members · zero flights 12+ months · 26% avg churn probability · avg CLV $8,118",
            "trigger":"90 days since member's last recorded flight",
            "action":"**Week 1:** 'We miss you' email + 3× bonus points on next booking (30-day window). **Week 3:** Personalised route offer on top historical city pair (e.g. YYC–YUL from $189 + 5,000 pts). **Week 6:** Last-chance — points expiry warning + 20% off next flight + SMS (if opted in). **No response:** Flag as dormant. Reduce email frequency to quarterly. Do not escalate spend.",
            "timing":"Trigger: 90 days of inactivity",
            "channel":"Email (weeks 1, 3, 6) + SMS if opted in",
            "kpi":"Re-activation rate within 90 days · cost per re-activated member (target < $45)",
        },
    }

    for seg, pb in PLAYBOOK.items():
        with st.container(border=True):
            st.markdown(f"### <span style='color:{pb['color']}'>{seg}</span>", unsafe_allow_html=True)
            st.caption(f"**Target:** {pb['target']}")

            ia, ib = st.columns(2)
            with ia:
                st.markdown("**Trigger**")
                st.info(pb["trigger"])
                st.markdown("**Timing**")
                st.write(pb["timing"])
                st.markdown("**Channel**")
                st.write(pb["channel"])

            with ib:
                st.markdown("**Action**")
                st.markdown(pb["action"])
                st.markdown("**KPI**")
                st.success(pb["kpi"])

        st.markdown("")
