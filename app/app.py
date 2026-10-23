"""What does it take to get a data job in Germany?

Streamlit app on 1,062 data-role job ads from the Bundesagentur für Arbeit (collected 7 October 2026).
It reads only aggregated tables from `app/data/` (created by notebooks/04_analysis.ipynb), no ad texts.
Shares are shown as natural frequencies ("1 in 3 ads"); exact percentages are in the tooltips.

Run locally from the project root:
    uv run streamlit run app/app.py
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
# Colours: the scientific colour map "oslo" (Crameri 2018, https://www.fabiocrameri.ch/colourmaps/):
# perceptually uniform, readable for colour-vision deficiencies and in greyscale. Ordered things
# (fit levels, skill tiers) get ordered lightness: darker = more.
OSLO = {
    "20": "#122d48",
    "30": "#1a446d",
    "35": "#215081",
    "40": "#2c5d96",
    "45": "#3b6bab",
    "55": "#6388c6",
}  # oslo sampled at 0.20-0.55: every level has at least 3:1 contrast to the background
MAIN, GREY, DARK = OSLO["30"], OSLO["55"], "#0f2236"
FIT_COLOURS = {
    "Strong fit": OSLO["20"],
    "Good start": OSLO["35"],
    "Some overlap": OSLO["45"],
    "Little overlap": OSLO["55"],
}
ROLES = [
    "Data Analyst",
    "BI / Analytics",
    "Data Scientist",
    "Data Engineer",
    "ML / AI Engineer",
]
KEY_THRESHOLD = 0.10  # a key skill of a role is required in at least 1 in 10 of its ads
TOP_THRESHOLD = 0.25  # "asked for most": required in at least 1 in 4 ads
GITHUB = "https://github.com/zeqizhao12/data-job-ad-nlp-de"

# The 46 skills of the dictionary in 03_extraction, grouped as there
SKILL_GROUPS = {
    "Programming": [
        "Python",
        "SQL",
        "R",
        "Java",
        "JavaScript / TypeScript",
        "Scala",
        "C++",
        "C#",
        "SAS",
        "MATLAB",
        "VBA",
    ],
    "Data engineering": [
        "Spark",
        "Kafka",
        "Airflow",
        "dbt",
        "ETL / ELT",
        "Data warehouse",
        "Data modelling",
        "Snowflake",
        "Databricks",
        "NoSQL",
    ],
    "Cloud and DevOps": [
        "AWS",
        "Azure",
        "Google Cloud",
        "Docker",
        "Kubernetes",
        "Terraform",
        "Git",
        "Linux",
    ],
    "BI and reporting": [
        "Power BI",
        "Tableau",
        "Qlik",
        "Excel",
        "DAX / Power Query",
        "SAP",
    ],
    "Machine learning and AI": [
        "Machine learning",
        "Deep learning",
        "NLP",
        "Computer vision",
        "LLM / GenAI",
        "scikit-learn",
        "TensorFlow",
        "PyTorch",
        "pandas",
        "Statistics",
    ],
    "Ways of working": ["Agile / Scrum"],
}


# --- Translating shares into job-seeker language -------------------------------------------------------
def freq(p):
    """A share as a natural frequency: 0.31 -> '1 in 3', 0.85 -> '8 in 10'."""
    if p >= 0.95:
        return "almost all"
    if p >= 0.45:
        return f"{round(p * 10)} in 10"
    if p >= 0.02:
        # round to a denominator people can picture: 1 in 3, 1 in 4, ... 1 in 10, 1 in 15, 1 in 20 ...
        nice = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]
        return f"1 in {min(nice, key=lambda d: abs(d - 1 / p))}"
    return "hardly any"


def fit_label(match):
    """Weighted share of a role's key-skill demand you cover, in words."""
    if match >= 0.6:
        return "Strong fit"
    if match >= 0.4:
        return "Good start"
    if match >= 0.2:
        return "Some overlap"
    return "Little overlap"


@st.cache_data
def load():
    skills = pd.read_csv(DATA_DIR / "role_skills.csv")
    barriers = pd.read_csv(DATA_DIR / "role_barriers.csv").set_index("role")
    # average over all ads (incl. "Other data role"), weighted by the number of ads per role
    average = (
        barriers.drop(columns="n_ads").mul(barriers["n_ads"], axis=0).sum()
        / barriers["n_ads"].sum()
    )
    n_total = int(barriers["n_ads"].sum())
    return skills[skills["role"].isin(ROLES)], barriers.loc[ROLES], average, n_total


def key_skills(skills, role):
    """Skills required in at least KEY_THRESHOLD of the role's ads, most required first."""
    key = skills[(skills["role"] == role) & (skills["share_required"] >= KEY_THRESHOLD)]
    return key.sort_values("share_required", ascending=False)[
        ["skill", "share_required"]
    ]


def match_roles(skills, selected):
    """Rank roles by the share of their key-skill demand the selected skills cover.
    Each key skill counts with how often it is required, so frequent requirements weigh more."""
    rows = []
    for role in ROLES:
        key = key_skills(skills, role)
        have = key["skill"].isin(selected)
        rows.append(
            {
                "role": role,
                "match": key.loc[have, "share_required"].sum()
                / key["share_required"].sum(),
                "have": key[have],
                "missing": key[~have],
                "n_key": len(key),
            }
        )
    return sorted(rows, key=lambda r: r["match"], reverse=True)


def names(df):
    return ", ".join(df["skill"]) or "none yet"


def with_freq(df, role):
    return (
        ", ".join(
            f"{s} *({freq(p)} ads)*" for s, p in zip(df["skill"], df["share_required"])
        )
        or "–"
    )


def fit_chart(results):
    df = pd.DataFrame(
        {
            "role": [r["role"] for r in results],
            "match": [r["match"] for r in results],
            "label": [
                f"{len(r['have'])} of {r['n_key']} key skills · {fit_label(r['match'])}"
                for r in results
            ],
        }
    )
    df["fit"] = [fit_label(m) for m in df["match"]]
    bars = (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("match:Q", scale=alt.Scale(domain=[0, 1.6]), axis=None),
            y=alt.Y(
                "role:N",
                sort=df["role"].tolist(),
                title=None,
                axis=alt.Axis(
                    labelFontSize=14, labelLimit=220, domain=False, ticks=False
                ),
            ),
            color=alt.Color(
                "fit:N",
                scale=alt.Scale(
                    domain=list(FIT_COLOURS), range=list(FIT_COLOURS.values())
                ),
                legend=None,
            ),
            tooltip=[
                "role",
                alt.Tooltip("match:Q", format=".0%", title="weighted fit"),
            ],
        )
    )
    labels = bars.mark_text(align="left", dx=8, fontSize=14).encode(
        text="label:N", color=alt.value(DARK)
    )
    return (bars + labels).properties(height=50 * len(df))


def tier_list(df, selected, role, suffix=""):
    """Skills as a list: name, check mark if the user has it, and how often the role's ads ask for it."""
    if df.empty:
        st.write("–")
    for s, p in zip(df["skill"], df["value"]):
        mark = " ✓" if s in selected else ""
        st.markdown(f"**{s}**{mark} · {freq(p)} ads{suffix}")


def detail_chart(skills, role, selected, n=15):
    """Stacked bars of the exact shares, for readers who want the numbers."""
    top = skills[skills["role"] == role].nlargest(n, "share_mentioned").copy()
    top["label"] = [("✓ " if s in selected else "") + s for s in top["skill"]]
    long = top.melt(
        id_vars="label",
        value_vars=["share_required", "share_nice"],
        var_name="type",
        value_name="share",
    )
    long["type"] = long["type"].map(
        {"share_required": "must-have", "share_nice": "bonus (nice-to-have)"}
    )
    long["order"] = long["type"].map({"must-have": 0, "bonus (nice-to-have)": 1})
    return (
        alt.Chart(long)
        .mark_bar()
        .encode(
            x=alt.X(
                "share:Q",
                stack="zero",
                axis=alt.Axis(format="%", title="share of the role's ads"),
            ),
            y=alt.Y(
                "label:N",
                sort=top["label"].tolist(),
                title=None,
                axis=alt.Axis(labelOverlap=False, labelLimit=240, labelFontSize=14),
            ),
            color=alt.Color(
                "type:N",
                scale=alt.Scale(
                    domain=["must-have", "bonus (nice-to-have)"], range=[MAIN, GREY]
                ),
                legend=alt.Legend(title=None, orient="bottom", labelFontSize=13),
            ),
            order=alt.Order("order:Q"),
            tooltip=[
                alt.Tooltip("label:N", title="skill"),
                "type",
                alt.Tooltip("share:Q", format=".0%"),
            ],
        )
        .properties(height=34 * n)
    )


# ------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Data jobs in Germany", page_icon="📊", layout="wide")
skills, barriers, AVG, N_TOTAL = load()

st.title("What does it take to get a data job in Germany?")
st.markdown(
    f"Based on **{N_TOTAL:,} real job ads** for data roles from the Bundesagentur für Arbeit (October 2026). "
    "Click the skills you have to see which roles fit you, or pick a role to see what employers ask for."
)

tab_find, tab_role = st.tabs(
    ["**1 · Which roles fit my skills?**", "**2 · What does a role ask for?**"]
)

# --- Tab 1: skills -> roles ------------------------------------------------------------------------
with tab_find:
    st.markdown("#### Click the skills you have")
    selected = []
    cols = st.columns(2, gap="large")
    for k, (group, options) in enumerate(SKILL_GROUPS.items()):
        with cols[k % 2]:
            picked = st.pills(
                group, options, selection_mode="multi", key=f"pills_{k}", wrap=True
            )
            selected += picked or []
    st.session_state["selected_skills"] = selected

    st.divider()
    if not selected:
        st.info("Select at least one skill above to see which data roles fit you.")
    else:
        results = match_roles(skills, selected)
        best = results[0]
        role = best["role"]
        b = barriers.loc[role]

        left, right = st.columns([1, 1], gap="large")
        with left, st.container(border=True):
            st.markdown("#### Your best fit")
            st.markdown(f"## {role}")
            st.markdown(
                f"**{fit_label(best['match'])}:** you already have **{len(best['have'])} of the {best['n_key']} "
                f"key skills** that {role} employers ask for."
            )
            nxt = best["missing"].head(3)
            if len(nxt):
                st.markdown("**Learn next**")
                st.markdown(
                    "\n".join(
                        f"{i}. **{s}**: required in {freq(p)} {role} ads"
                        for i, (s, p) in enumerate(
                            zip(nxt["skill"], nxt["share_required"]), start=1
                        )
                    )
                )
            more = (
                "more than"
                if b["newcomer_friendly"] > AVG["newcomer_friendly"] + 0.03
                else (
                    "fewer than"
                    if b["newcomer_friendly"] < AVG["newcomer_friendly"] - 0.03
                    else "about as many as"
                )
            )
            st.markdown(
                f"**{freq(b['newcomer_friendly']).capitalize()} {role} ads are open to beginners**, "
                f"{more} the average across data roles ({freq(AVG['newcomer_friendly'])})."
            )
        with right, st.container(border=True):
            st.markdown("#### How well do you fit each role?")
            st.altair_chart(fit_chart(results), width="stretch")
            st.caption(
                "Darker = better fit. Ranked by how much of each role's key-skill demand you cover."
            )

        st.markdown("#### Details per role")
        for r in results:
            with st.expander(
                f"{r['role']} · {fit_label(r['match'])} · {len(r['have'])} of {r['n_key']} key skills"
            ):
                c1, c2 = st.columns(2, gap="large")
                c1.markdown("**Key skills you have**")
                c1.markdown(names(r["have"]))
                c2.markdown("**Key skills still missing** (most asked for first)")
                c2.markdown(with_freq(r["missing"], r["role"]))

        with st.expander("How is the fit calculated?"):
            st.markdown("""
- **Key skills** of a role are the skills that at least 1 in 10 of its ads list as a must-have.
- Roles are ranked by how much of this demand you cover. A skill that 6 in 10 ads require counts more
  than one that 1 in 10 ads require.
- **Strong fit**: you cover at least 60% of the demand · **Good start**: 40–60% · **Some overlap**: 20–40% · **Little overlap**: below 20%.
""")

# --- Tab 2: role -> skills ---------------------------------------------------------------------------
with tab_role:
    role = st.selectbox("Choose a role", ROLES)
    b = barriers.loc[role]
    selected = st.session_state.get("selected_skills", [])

    st.markdown("#### What do employers ask for?")
    rs = skills[skills["role"] == role]
    top = rs[rs["share_required"] >= TOP_THRESHOLD].sort_values(
        "share_required", ascending=False
    )
    common = rs[
        (rs["share_required"] >= KEY_THRESHOLD) & (rs["share_required"] < TOP_THRESHOLD)
    ].sort_values("share_required", ascending=False)
    bonus = rs[
        (rs["share_required"] < KEY_THRESHOLD) & (rs["share_nice"] >= 0.03)
    ].nlargest(5, "share_nice")

    def tier_header(title, note, colour):
        st.markdown(
            f'<div style="border-top:6px solid {colour};padding-top:8px"><b>{title}</b><br>'
            f'<span style="color:#4a5568;font-size:0.9rem">{note}</span></div>',
            unsafe_allow_html=True,
        )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1, st.container(border=True):
        tier_header("Asked for most", "must-have in at least 1 in 4 ads", OSLO["20"])
        tier_list(top.rename(columns={"share_required": "value"}), selected, role)
    with c2, st.container(border=True):
        tier_header("Also common", "must-have in 1 in 4 to 1 in 10 ads", OSLO["40"])
        tier_list(common.rename(columns={"share_required": "value"}), selected, role)
    with c3, st.container(border=True):
        tier_header("Bonus skills", "often listed as “nice to have”", OSLO["55"])
        tier_list(
            bonus.rename(columns={"share_nice": "value"}),
            selected,
            role,
            suffix=" as a bonus",
        )
    if selected:
        st.caption("✓ = a skill you selected in tab 1.")

    st.markdown("#### How easy is it to get in?")
    box = st.container(border=True)
    m = box.columns(4)
    m[0].metric(
        "Open to beginners",
        freq(b["newcomer_friendly"]) + " ads",
        help=f"{b['newcomer_friendly']:.0%} of {role} ads: junior title, beginner wording "
        "('Berufseinsteiger', 'erste Erfahrung'), or at most 1–2 years of experience",
    )
    m[0].caption(f"Average across data roles: {freq(AVG['newcomer_friendly'])}")
    m[1].metric(
        "Ask for 3+ years of experience",
        freq(b["years_3_plus"]) + " ads",
        help=f"{b['years_3_plus']:.0%} of {role} ads: three or more years, or 'several years'",
    )
    m[1].caption(f"Average across data roles: {freq(AVG['years_3_plus'])}")
    m[2].metric(
        "Mention a university degree",
        freq(b["degree"]) + " ads",
        help=f"{b['degree']:.0%} of {role} ads mention a degree; {b['alt_path']:.0%} also accept an "
        "alternative such as 'oder vergleichbare Qualifikation'",
    )
    m[2].caption(
        f"{freq(b['alt_path']).capitalize()} also accept equivalent qualifications"
    )
    m[3].metric(
        "Require fluent German",
        freq(b["german_fluent"]) + " ads",
        help=f"{b['german_fluent']:.0%} of {role} ads: fließend, verhandlungssicher, muttersprachlich or C1/C2",
    )
    m[3].caption(f"{freq(b['english_ad']).capitalize()} ads are written in English")
    box.caption(
        f"Based on {int(b['n_ads'])} {role} ads. Hover over ⓘ for the exact percentages."
    )

    with st.expander("See the detailed numbers"):
        st.altair_chart(detail_chart(skills, role, selected), width="stretch")
        st.caption(
            "A skill counts as *bonus* when every mention in the ad is hedged ('idealerweise', "
            "'von Vorteil', 'a plus') or listed under a heading such as 'Nice-to-have'."
        )

# --- About ---------------------------------------------------------------------------------------------
with st.expander("About the data and methods"):
    st.markdown(f"""
- **Data:** job ads from the job search of the Bundesagentur für Arbeit (7 October 2026). After cleaning and a
  title-based data-role filter (precision 0.88, recall 0.85 against 100 hand-labelled ads), {N_TOTAL:,} ads remain.
  {N_TOTAL - int(barriers["n_ads"].sum())} ads with no clear role ("Other data role") count in the averages but are not shown as a role.
- **Extraction:** role and seniority from the job title; 46 skills with a regex dictionary (108 of 110 checked hits
  correct); must-have vs. nice-to-have from hedging words (28 of 30 correct); experience, degree and German level
  (53 of 58 correct); ad language from function words, cross-checked with a language detector (1,061 of 1,062 agree).
- **Limitations:** a snapshot of one day from one platform; rule-based extraction can miss what a hedge word refers to;
  "mention a degree" includes "idealerweise ein Studium".
- **Colours:** scientific colour map *oslo* by Fabio Crameri ([fabiocrameri.ch/colourmaps](https://www.fabiocrameri.ch/colourmaps/)),
  perceptually uniform and readable with colour-vision deficiencies.
- **Code and full analysis:** [{GITHUB}]({GITHUB})
""")
