"""What does it take to get a data job in Germany?

Streamlit app on 1,062 data-role job ads from the Bundesagentur für Arbeit (collected 7 October 2026).
It reads only aggregated tables from `app/data/` (created by notebooks/04_analysis.ipynb), no ad texts.

Run locally from the project root:
    uv run streamlit run app/app.py
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
MAIN, GREY, DARK = "#5b7a99", "#c9ced6", "#2f3e4e"
ROLES = ["Data Analyst", "BI / Analytics", "Data Scientist", "Data Engineer", "ML / AI Engineer"]
CORE_THRESHOLD = 0.10      # a skill is "core" for a role if at least 10% of the role's ads require it
GITHUB = "https://github.com/zeqizhao12/data-job-ad-nlp-de"


@st.cache_data
def load():
    skills = pd.read_csv(DATA_DIR / "role_skills.csv")
    barriers = pd.read_csv(DATA_DIR / "role_barriers.csv").set_index("role")
    n_total = int(barriers["n_ads"].sum())            # all ads, incl. "Other data role"
    return skills[skills["role"].isin(ROLES)], barriers.loc[ROLES], n_total


def match_table(skills, barriers, selected):
    """Rank roles by how much of their core-skill demand the selected skills cover.

    Core skills of a role: required in at least CORE_THRESHOLD of its ads.
    Match = sum of share_required over the selected core skills / sum over all core skills,
    so frequently required skills count more than rarely required ones.
    """
    rows = []
    for role in ROLES:
        core = (skills[(skills["role"] == role) & (skills["share_required"] >= CORE_THRESHOLD)]
                .sort_values("share_required", ascending=False))
        have = core["skill"].isin(selected)
        missing = core.loc[~have]
        rows.append({
            "Role": role,
            "Match": 100 * core.loc[have, "share_required"].sum() / core["share_required"].sum(),
            "Core skills covered": f"{have.sum()} of {len(core)}",
            "Most required skills you are missing": ", ".join(
                f"{s} ({p:.0%})" for s, p in zip(missing["skill"][:4], missing["share_required"][:4])) or "–",
            "Newcomer-friendly ads": 100 * barriers.at[role, "newcomer_friendly"],
            "Ads in English": 100 * barriers.at[role, "english_ad"],
        })
    return pd.DataFrame(rows).sort_values("Match", ascending=False)


def skill_chart(skills, role, n=15):
    """Stacked bars: share of the role's ads that require a skill, and that list it only as nice-to-have."""
    top = skills[skills["role"] == role].nlargest(n, "share_mentioned")
    long = top.melt(id_vars="skill", value_vars=["share_required", "share_nice"], var_name="type", value_name="share")
    long["type"] = long["type"].map({"share_required": "required", "share_nice": "only nice-to-have"})
    long["order"] = long["type"].map({"required": 0, "only nice-to-have": 1})
    return (alt.Chart(long).mark_bar()
            .encode(x=alt.X("share:Q", stack="zero", axis=alt.Axis(format="%", title="share of the role's ads")),
                    y=alt.Y("skill:N", sort=top["skill"].tolist(), title=None,
                            axis=alt.Axis(labelOverlap=False, labelLimit=220, labelFontSize=13)),
                    color=alt.Color("type:N", scale=alt.Scale(domain=["required", "only nice-to-have"], range=[MAIN, GREY]),
                                    legend=alt.Legend(title=None, orient="bottom")),
                    order=alt.Order("order:Q"),
                    tooltip=["skill", "type", alt.Tooltip("share:Q", format=".0%")])
            .properties(height=34 * n))


# ------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Data jobs in Germany", page_icon="📊", layout="wide")
skills, barriers, N_TOTAL = load()

st.title("What does it take to get a data job in Germany?")
st.caption(f"Based on {N_TOTAL:,} data-role job ads from the Bundesagentur für Arbeit, "
           "collected on 7 October 2026. Skills and requirements were extracted from the ad texts and checked by hand.")

tab_roles, tab_skills = st.tabs(["Skills → roles", "Role → skills"])

with tab_roles:
    st.subheader("Which data roles match your skills?")
    selected = st.multiselect("Select the skills you have", sorted(skills["skill"].unique(), key=str.lower),
                              default=["Python", "SQL", "Statistics"])
    if not selected:
        st.info("Select at least one skill to see matching roles.")
    else:
        table = match_table(skills, barriers, selected)
        st.dataframe(
            table, hide_index=True, width="stretch",
            column_config={
                "Match": st.column_config.ProgressColumn(
                    "Match", format="%.0f%%", min_value=0, max_value=100,
                    help="Share of the role's core-skill demand that your skills cover (weighted by how often each skill is required)"),
                "Newcomer-friendly ads": st.column_config.NumberColumn(
                    format="%.0f%%", help="Junior title, entry signal in the text, or at most 1–2 years of experience"),
                "Ads in English": st.column_config.NumberColumn(format="%.0f%%"),
            })
        st.caption(f"Core skills of a role are skills that at least {CORE_THRESHOLD:.0%} of its ads require. "
                   "The match weights them by how often they are required, so missing Python counts more than missing Git. "
                   "Numbers in brackets: share of the role's ads that require the skill.")

with tab_skills:
    st.subheader("What does a role require?")
    role = st.selectbox("Choose a role", ROLES)
    b = barriers.loc[role]

    cols = st.columns(6)
    cols[0].metric("Ads", f"{int(b['n_ads'])}")
    cols[1].metric("Newcomer-friendly", f"{b['newcomer_friendly']:.0%}",
                   help="Junior title, entry signal in the text, or at most 1–2 years of experience")
    cols[2].metric("3+ years required", f"{b['years_3_plus']:.0%}", help="Three or more years, or 'several years'")
    cols[3].metric("Degree mentioned", f"{b['degree']:.0%}",
                   help=f"{b['alt_path']:.0%} of the ads also accept an alternative, e.g. 'oder vergleichbare Qualifikation'")
    cols[4].metric("Fluent German", f"{b['german_fluent']:.0%}", help="Fließend, verhandlungssicher, muttersprachlich or C1/C2")
    cols[5].metric("Ads in English", f"{b['english_ad']:.0%}")

    st.altair_chart(skill_chart(skills, role), width="stretch")
    st.caption("The 15 skills most often mentioned in this role. A skill is *nice-to-have* when every mention "
               "in the ad is hedged ('idealerweise', 'von Vorteil', 'a plus') or listed under a heading such as 'Nice-to-have'.")

with st.expander("About the data and methods"):
    st.markdown(f"""
- **Data:** job ads from the job search of the Bundesagentur für Arbeit (7 October 2026). After cleaning and a
  title-based data-role filter (precision 0.88, recall 0.85 against 100 hand-labelled ads), {N_TOTAL:,} ads remain.
  {N_TOTAL - int(barriers["n_ads"].sum())} ads with no clear role ("Other data role") are not shown here.
- **Extraction:** role and seniority from the job title; 46 skills with a regex dictionary (108 of 110 checked hits
  correct); required vs. nice-to-have from hedging words (28 of 30 correct); experience, degree and German level
  (53 of 58 correct); ad language from function words, cross-checked with a language detector (1,061 of 1,062 agree).
- **Limitations:** a snapshot of one day from one platform; rule-based extraction can miss what a hedge word refers to;
  "degree mentioned" includes "idealerweise ein Studium".
- **Code and full analysis:** [{GITHUB}]({GITHUB})
""")
