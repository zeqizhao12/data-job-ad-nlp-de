"""Which data job fits you?

Streamlit app on 1,062 data-role job ads from the Bundesagentur für Arbeit (collected 7 October 2026).
It reads only aggregated tables from `app/data/` (created by notebooks/04_analysis.ipynb), no ad texts.

Design:
- Three pages: a short start page (what the app is for, one start button, how it works, proof),
  then the two tools: skills -> roles and role -> skills.
- Attention order on each tool page: where to input -> the most useful result (next to the input) -> details.
- Shares are shown as natural frequencies ("1 in 3 ads"); exact percentages sit in tooltips and an expander.
- No hard-coded colours: everything uses the theme (.streamlit/config.toml), whose light and dark variants
  come from the scientific colour map "oslo" (Crameri), so text and bars stay readable in both modes.

Run locally from the project root:
    uv run streamlit run app/app.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
ROLES = [
    "Data Analyst",
    "BI / Analytics",
    "Data Scientist",
    "Data Engineer",
    "ML / AI Engineer",
]
KEY_THRESHOLD = (
    0.10  # a key skill of a role is a must-have in at least 1 in 10 of its ads
)
TOP_THRESHOLD = 0.25  # "must-have skills": a must-have in at least 1 in 4 ads
GITHUB = "https://github.com/zeqizhao12/data-job-ad-nlp-de"
HAVE = ":blue-badge[:material/check: You have it]"
TO_LEARN = ":gray-badge[To learn]"

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
        "Statistics",
        "Deep learning",
        "NLP",
        "Computer vision",
        "LLM / GenAI",
        "scikit-learn",
        "TensorFlow",
        "PyTorch",
        "pandas",
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
    "Ways of working": ["Agile / Scrum"],
}


# --- Data and helpers -----------------------------------------------------------------------------------
def freq(p):
    """A share as a natural frequency: 0.31 -> '1 in 3', 0.85 -> '8 in 10'."""
    if p >= 0.95:
        return "almost all"
    if p >= 0.45:
        return f"{round(p * 10)} in 10"
    if p >= 0.02:
        nice = [
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            12,
            15,
            20,
            25,
            30,
            40,
            50,
        ]  # denominators people can picture
        return f"1 in {min(nice, key=lambda d: abs(d - 1 / p))}"
    return "hardly any"


def fit_label(match):
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
    """Skills that are a must-have in at least KEY_THRESHOLD of the role's ads, most required first."""
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


def skill_rows(df, selected, value_col, suffix="", mark_missing=True):
    """One aligned row per skill: name | how often | status badge in its own column."""
    if df.empty:
        st.caption("None")
    for s, p in zip(df["skill"], df[value_col]):
        c1, c2, c3 = st.columns([4, 4, 3], vertical_alignment="center")
        c1.markdown(f"**{s}**")
        c2.markdown(f"{freq(p)} ads{suffix}", help=f"{p:.0%} of the ads")
        if s in selected:
            c3.markdown(HAVE)
        elif selected and mark_missing:
            c3.markdown(TO_LEARN)


def selected_skills():
    return st.session_state.get("skills_store", [])


skills, barriers, AVG, N_TOTAL = load()


# --- Page 1: start ---------------------------------------------------------------------------------------
def start_page():
    st.title("Which data job fits you?")
    st.markdown(
        "#### See which data roles match your skills, what employers really require, and what to learn next."
    )
    st.markdown(
        f"Based on **{N_TOTAL:,} real job ads** for data roles in Germany "
        "(Bundesagentur für Arbeit, October 2026)."
    )

    st.write("")
    if st.button(
        "Start: check my skills", type="primary", icon=":material/arrow_forward:"
    ):
        st.switch_page(find_page)
    if st.button("or explore a role directly", type="tertiary"):
        st.switch_page(explore_page)
    st.caption("Takes about a minute. No sign-up, nothing is stored.")

    st.write("")
    st.subheader("How it works")
    steps = st.columns(3, gap="medium")
    for col, (icon, title, text) in zip(
        steps,
        [
            (
                ":material/touch_app:",
                "1 · Click your skills",
                "Pick the tools and methods you know, from Python to Power BI.",
            ),
            (
                ":material/target:",
                "2 · See your best fit",
                "Find the data role that fits you best and the three skills to learn next.",
            ),
            (
                ":material/work:",
                "3 · Explore a role",
                "See what employers ask for and how open the role is to beginners.",
            ),
        ],
    ):
        with col, st.container(border=True):
            st.markdown(f"### {icon}")
            st.markdown(f"**{title}**")
            st.caption(text)

    st.write("")
    st.subheader("Built on real data, checked by hand")
    proof = st.columns(3)
    proof[0].metric("Job ads analysed", f"{N_TOTAL:,}")
    proof[1].metric("Skills tracked", "46")
    proof[2].metric(
        "Skill matches correct",
        "108 of 110",
        help="Random sample of extracted skills, checked by hand",
    )
    st.caption(
        f"A text-mining portfolio project. Code and full analysis: [GitHub]({GITHUB})"
    )


# --- Page 2: skills -> roles ------------------------------------------------------------------------------
def find_page():
    st.title("Find roles for my skills")
    col_in, col_out = st.columns([11, 9], gap="large")

    # Input
    with col_in:
        st.subheader("1 · Click the skills you have")
        store = selected_skills()
        selected = []
        for k, (group, options) in enumerate(SKILL_GROUPS.items()):
            key = f"pills_{k}"
            if (
                key not in st.session_state
            ):  # restore the selection after visiting another page
                st.session_state[key] = [s for s in store if s in options]
            selected += (
                st.pills(group, options, selection_mode="multi", key=key, wrap=True)
                or []
            )
        st.session_state["skills_store"] = selected
        if selected and st.button(
            "Clear my selection", type="tertiary", icon=":material/close:"
        ):
            for k in range(len(SKILL_GROUPS)):
                st.session_state.pop(f"pills_{k}", None)
            st.session_state["skills_store"] = []
            st.rerun()

    # The most useful result, right next to the input
    with col_out:
        st.subheader("2 · Your best fit")
        if not selected:
            with st.container(border=True):
                st.markdown("Your result appears here as soon as you click a skill.")
                st.caption(
                    "Tip: start with the tools you use most, e.g. Python, SQL or Excel."
                )
            return
        results = match_roles(skills, selected)
        best = results[0]
        role = best["role"]
        b = barriers.loc[role]
        with st.container(border=True):
            st.markdown(f"## :blue[{role}]")
            st.markdown(
                f"**{fit_label(best['match'])}:** you have **{len(best['have'])} of the "
                f"{best['n_key']} key skills** that {role} employers ask for."
            )
            st.progress(best["match"])
            nxt = best["missing"].head(3)
            if len(nxt):
                st.markdown("**Learn next**")
                st.markdown(
                    "\n".join(
                        f"{i}. **{s}**, a must-have in {freq(p)} {role} ads"
                        for i, (s, p) in enumerate(
                            zip(nxt["skill"], nxt["share_required"]), start=1
                        )
                    )
                )
            more = (
                "more than"
                if b["newcomer_friendly"] > AVG["newcomer_friendly"] + 0.03
                else "fewer than"
                if b["newcomer_friendly"] < AVG["newcomer_friendly"] - 0.03
                else "about as many as"
            )
            st.markdown(
                f"{freq(b['newcomer_friendly']).capitalize()} {role} ads are open to beginners, "
                f"{more} the average for data roles ({freq(AVG['newcomer_friendly'])})."
            )
            if st.button(
                f"See what {role} employers ask for", icon=":material/arrow_forward:"
            ):
                st.session_state["role_store"] = role
                st.session_state.pop("role_choice", None)
                st.switch_page(explore_page)

    # Everything else
    st.divider()
    st.subheader("How you fit every role")
    for r in results:
        c_role, c_bar, c_text = st.columns([3, 5, 4], vertical_alignment="center")
        c_role.markdown(f"**{r['role']}**" if r is results[0] else r["role"])
        c_bar.progress(r["match"])
        c_text.caption(
            f"{fit_label(r['match'])} · {len(r['have'])} of {r['n_key']} key skills"
        )

    with st.expander("Which key skills do you have and miss, per role?"):
        for r in results:
            st.markdown(f"**{r['role']}**")
            c1, c2 = st.columns(2, gap="large")
            c1.caption("You have")
            c1.markdown(", ".join(r["have"]["skill"]) or "none yet")
            c2.caption("Still missing, most asked for first")
            c2.markdown(
                ", ".join(
                    f"{s} ({freq(p)} ads)"
                    for s, p in zip(
                        r["missing"]["skill"], r["missing"]["share_required"]
                    )
                )
                or "–"
            )

    with st.expander("How is the fit calculated?"):
        st.markdown("""
- **Key skills** of a role are the skills that at least 1 in 10 of its ads list as a must-have.
- Roles are ranked by how much of this demand you cover. A skill that 6 in 10 ads require counts more
  than one that 1 in 10 ads require. The bar shows this share.
- **Strong fit**: at least 60% of the demand · **Good start**: 40–60% · **Some overlap**: 20–40% · **Little overlap**: below 20%.
""")


# --- Page 3: role -> skills -------------------------------------------------------------------------------
def explore_page():
    st.title("What does a role ask for?")
    st.subheader("1 · Choose a role")
    if "role_choice" not in st.session_state:
        st.session_state["role_choice"] = st.session_state.get(
            "role_store", "Data Analyst"
        )
    role = (
        st.segmented_control(
            "Role", ROLES, key="role_choice", label_visibility="collapsed"
        )
        or "Data Analyst"
    )
    st.session_state["role_store"] = role
    b = barriers.loc[role]
    selected = selected_skills()
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

    left, right = st.columns([1, 1], gap="large")
    with left:
        st.subheader("2 · Must-have skills")
        with st.container(border=True):
            st.caption(f"A must-have in at least 1 in 4 {role} ads")
            skill_rows(top, selected, "share_required")
        if not selected:
            st.caption(
                "Tip: click your skills on the page “Find roles for my skills” to see which ones you already have."
            )
    with right:
        st.subheader("How easy is it to get in?")
        with st.container(border=True):
            m1, m2 = st.columns(2)
            m1.metric(
                "Open to beginners",
                freq(b["newcomer_friendly"]) + " ads",
                help=f"{b['newcomer_friendly']:.0%} of {role} ads: junior title, beginner wording "
                "('Berufseinsteiger', 'erste Erfahrung'), or at most 1–2 years of experience",
            )
            m1.caption(f"Average for data roles: {freq(AVG['newcomer_friendly'])}")
            m2.metric(
                "Ask for 3+ years",
                freq(b["years_3_plus"]) + " ads",
                help=f"{b['years_3_plus']:.0%} of {role} ads: three or more years, or 'several years'",
            )
            m2.caption(f"Average for data roles: {freq(AVG['years_3_plus'])}")
            m3, m4 = st.columns(2)
            m3.metric(
                "Mention a degree",
                freq(b["degree"]) + " ads",
                help=f"{b['degree']:.0%} of {role} ads mention a university degree",
            )
            m3.caption(
                f"{freq(b['alt_path']).capitalize()} also accept equivalent qualifications"
            )
            m4.metric(
                "Require fluent German",
                freq(b["german_fluent"]) + " ads",
                help=f"{b['german_fluent']:.0%} of {role} ads: fließend, verhandlungssicher, muttersprachlich or C1/C2",
            )
            m4.caption(
                f"{freq(b['english_ad']).capitalize()} ads are written in English"
            )

    st.divider()
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**Also common**")
        st.caption("A must-have in 1 in 4 to 1 in 10 ads")
        skill_rows(common, selected, "share_required")
    with c2:
        st.markdown("**Bonus skills**")
        st.caption("Often listed as “nice to have”")
        skill_rows(
            bonus, selected, "share_nice", suffix=" as a bonus", mark_missing=False
        )

    with st.expander("See the exact numbers"):
        table = rs.nlargest(15, "share_mentioned")[
            ["skill", "share_required", "share_nice"]
        ].assign(
            share_required=lambda d: 100 * d["share_required"],
            share_nice=lambda d: 100 * d["share_nice"],
        )
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={
                "skill": "Skill",
                "share_required": st.column_config.ProgressColumn(
                    "Must-have in", format="%.0f%% of ads", min_value=0, max_value=100
                ),
                "share_nice": st.column_config.ProgressColumn(
                    "Only a bonus in",
                    format="%.0f%% of ads",
                    min_value=0,
                    max_value=100,
                ),
            },
        )
        st.caption(
            f"Based on {int(b['n_ads'])} {role} ads. A skill counts as a bonus when every mention in the ad is "
            "hedged ('idealerweise', 'von Vorteil', 'a plus') or listed under a heading such as 'Nice-to-have'."
        )


# --- App ----------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Which data job fits you?", page_icon="📊", layout="wide")

start_page = st.Page(start_page, title="Start", icon=":material/home:", default=True)
find_page = st.Page(
    find_page,
    title="Find roles for my skills",
    icon=":material/person_search:",
    url_path="find",
)
explore_page = st.Page(
    explore_page,
    title="What does a role ask for?",
    icon=":material/work:",
    url_path="explore",
)
st.navigation([start_page, find_page, explore_page], position="top").run()

st.divider()
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
  perceptually uniform and readable with colour-vision deficiencies; light and dark mode via ⋮ → Settings.
- **Code and full analysis:** [{GITHUB}]({GITHUB})
""")
