# What Does It Take to Get a Data Job in Germany?

A text-mining project on German job ads, with data roles as the case study: turning
unstructured ad texts into structured information about roles, skills and entry
requirements, and checking each extraction step against human judgement. The ads are
collected from the job search platform of the Bundesagentur für Arbeit (German
Federal Employment Agency).

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Status](https://img.shields.io/badge/status-complete-brightgreen)
[![Live app](https://img.shields.io/badge/live%20app-Streamlit-FF4B4B)](https://data-jobs-de.streamlit.app/)

**Live app: [data-jobs-de.streamlit.app](https://data-jobs-de.streamlit.app/)** — click the skills you have and see which data role fits you best and what to learn next.

## Project Overview

**Problem.** Job ads for data roles list long and varied requirements. For
people entering the field — graduates and career switchers — it is hard to tell
which skills are really required, which are only nice to have, and how open
employers are to newcomers.

**Goal.** Collect job ads for data roles in Germany and answer three questions
from the perspective of a newcomer:

1. Which skills are required, and which are only nice to have?
2. How open are ads to newcomers — in terms of experience, degree and German
   level?
3. How do expectations differ between data roles (Analyst, Scientist, Engineer,
   BI, ML / AI) and between junior and senior ads?

**Approach.** The project turns unstructured job ad texts into structured information about data roles, 
skills and entry requirements:
- **Data collection** via API, with retries and resumable downloads, in two snapshots six weeks apart.
- **Near-duplicate detection** with text similarity to identify and remove repeated ads, also across the two snapshots.
- **Rule-based text classification** of job titles, evaluated against a hand-labelled sample by two annotators (precision, recall, Cohen's kappa).
- **Skill and requirement extraction** from German and English ad texts with a regex dictionary, including German compounds like "Pythonkenntnisse".
- **Hedge detection** to separate required from nice-to-have skills, using cue words ("von Vorteil", "a plus") and section headings.
- **Language identification** of each ad (German or English) with a function-word count, cross-checked with a statistical language detector (lingua).
- **Human validation** of every extraction step with stratified spot checks, instead of checking automated output with another model.
- **Statistical comparison** of roles and seniority levels: shares with Wilson confidence intervals, log-odds ratios for role-typical skills, Fisher's exact test for the small junior group (Benjamini–Hochberg adjusted).
- **Robustness checks:** results recomputed with duplicates weighted, old ads removed, every employer weighted equally, and with each snapshot's contribution separated.

**Product.** A [web app](https://data-jobs-de.streamlit.app/) for career switchers and newcomers that works in two directions:

- **Skills → roles:** click your skills and see how well you fit each data role, which key skills you already have, and the three to learn next.
- **Role → skills:** choose a role and see its must-have and bonus skills, and how open it is to beginners (experience, degree, German).

## Data

| | |
|---|---|
| **Source** | Job search of the Bundesagentur für Arbeit |
| **Collected** | Two snapshots: 7 October and 19 November 2026 |
| **Search terms** | Data Analyst, Datenanalyst, Data Scientist, Data Engineer, Dateningenieur, Business Intelligence, Machine Learning; in the second snapshot also AI Engineer, MLOps |
| **Size** | 3,570 ads with full text: 2,119 from 7 October (2,121 unique search results; 2 ads expired before their text could be fetched) and 1,451 new ads from 19 November (2,306 unique search results, 855 of them already collected in October) |
| **After cleaning** | 3,170 ads (3,460 with a location in Germany; 203 exact and 87 near-duplicate copies removed, most of them ads published again between the two snapshots) |
| **Data roles** | 1,777 ads pass the title rule; 1,768 after removing ads that matched only through an employer name ("NTT DATA"): 1,062 from the first snapshot, 706 from the second |
| **Content** | Title, employer, location, contract type, home office option, publication date, full ad text |

The Bundesagentur does not offer an official public API. Access follows the
documentation of the community project [bundesAPI](https://github.com/bundesAPI/jobsuche-api). 
*Note: Because the interface is unofficial, it may change without notice.*

The raw data is **not** included in this repository: the ads belong to the
Bundesagentur and the publishing employers. Running the collection notebook
recreates the dataset. Since the job market changes daily, a new run will return
a different set of ads.

**Why two snapshots?** One day of the job search holds only about 2,100 ads for
these terms; the collection already gets every result. Ads turn over quickly, so
a second collection six weeks later added 1,451 new ads and raised the number of
data-role ads from 1,062 to 1,768. The two new search terms brought in 156 of
these, almost all ML / AI roles, which changes the role mix (see the robustness
checks below).

## Findings

### Data-role filter

A search for data jobs does not return only data jobs, so ads are filtered with a
rule on the **job title** (not the ad text, which would make the later skill counts
confirm the selection). The rule was evaluated against a random sample of 100
hand-labelled ads from the first snapshot:

| | Version 1 | Version 3 (final) |
|---|---|---|
| Precision | 0.79 | **0.88** |
| Recall | 0.85 | **0.85** (44 of 52 data roles) |
| Ads kept (both snapshots) | 1,842 | **1,777** |

A second annotator (a senior data analyst) labelled 30 of the ads independently with
the same codebook. Agreement was only fair (Cohen's kappa 0.37 for three categories,
0.35 binary): the boundary between a data role and an adjacent role (e.g. data
governance, teaching) is unclear even for humans. This is reported as a limitation.

### Roles, seniority and skills

- **Roles (from the title):** ML / AI 507, Data Engineer 395, Data Analyst 383,
  BI 175, Data Scientist 172, other 136. ML / AI became the largest role mainly
  through the new search term "AI Engineer".
- **Seniority is rarely stated.** Only 76 titles say junior, 434 say senior, and
  1,258 give no level, so for newcomers the requirements in the ad text matter more
  than the title.
- **Skills** are extracted with a dictionary of 46 skills (German and English
  variants). A stratified spot check found 108 of 110 hits correct.
- **Python (46%) and SQL (41%)** are the most frequent skills, followed by machine
  learning and data modelling (28% each) and LLM / GenAI (22%; 14% in the first
  snapshot, 33% in the second).

![Top skills](reports/figures/top_skills.png)

### Required vs. nice-to-have

A mention counts as *nice-to-have* if the sentence or bullet contains a hedge cue
("von Vorteil", "idealerweise", "a plus") or sits under a heading such as
"Nice-to-have". A spot check of 30 mentions found 28 correct. **Python and SQL are
required in more than 80% of their mentions**, while tools such as Airflow and
Kafka are more often only a plus (25% of mentions).

### Each role has a clear skill profile

The most typical skills of each role (log-odds ratio, role vs. all other ads):

| Role | Most typical skills |
|---|---|
| Data Analyst | Excel, VBA, Tableau, Power BI, R |
| BI / Analytics | Qlik, DAX / Power Query, SAP, data modelling, data warehouse |
| Data Scientist | statistics, scikit-learn, machine learning, R, Python |
| Data Engineer | dbt, Kafka, Airflow, ETL / ELT, Spark |
| ML / AI Engineer | LLM / GenAI, deep learning, TensorFlow, PyTorch, computer vision |

These profiles match common role descriptions, which also supports the title-based
role assignment.

![Skills by role](reports/figures/role_heatmap.png)

### Entry barriers: junior ads lower the experience bar, not the degree bar

Experience, degree and German level are extracted from the ad text (53 of 58
manually checked items correct). Most ads give no number of years (997 of 1,768),
and 496 ask for "several years". 1,371 ads mention a university degree, but 571 also
name an alternative path ("oder vergleichbare Qualifikation").

- **Junior titles lower the experience bar:** only 2.6% of junior ads ask for three
  or more (or "several") years, compared with 64.5% of senior ads, and 51.3% contain
  an entry signal ("Berufseinsteiger", "erste Erfahrung"; senior: 5.1%). Both
  differences are significant (Fisher's exact test, adjusted p < 0.001).
- **They do not lower the degree bar:** junior ads mention a degree even more often
  than senior ads (82.9% vs. 68.7%, adjusted p = 0.03). With the first snapshot
  alone (55 junior ads), this difference was not significant.
- **Data Analyst is the most accessible role:** 27.9% of its ads are
  newcomer-friendly (junior title, entry signal or at most 1–2 years), compared with
  19.2% overall. It is the only role whose 95% confidence interval lies above the
  average. The share is lower in the second snapshot (16.0%) than in the first
  (21.3%); two snapshots cannot tell whether this is a trend.

![Newcomer-friendly ads by role](reports/figures/newcomer_by_role.png)

### German: the language of the ad matters

46% of the ads do not mention German at all, but most of these are written in German
and expect it implicitly. The language of each ad was identified with two methods,
which agree on 1,767 of 1,768 ads.

- **230 ads (13.0%) are written in English**, and 79.1% of them do not mention German.
  That leaves about one ad in ten (182 of 1,768) that is in English and states no
  German requirement.
- **Among the named roles, English-language ads are most common for Data Analyst
  (17.5%) and ML / AI (14.2%)**, and rare for BI / Analytics (2.3%).
- **German level is grouped by the common German CV scale**, in which "gute" and
  "sehr gute Kenntnisse" form one level and "fließend" is the next step. A native
  speaker reviewed the scale and the hedge words. Fluent German or higher is
  required in 23.6% of all ads.

![German requirement by language](reports/figures/german_by_language.png)

### The results are robust

Weighting ads by their duplicates, leaving out the 45 ads older than a year, or
weighting each of the 977 employers equally changes the newcomer-friendly share by
at most 0.4 percentage points (19.0–19.6% vs. 19.2%). Skill shares keep almost the
same ranking (Spearman 0.984–0.999); the largest change is 3.3 percentage points
(Power BI, with employers weighted equally).

The second snapshot matters more than any cleaning decision. With the first
snapshot only, LLM / GenAI is 7.4 percentage points lower and 21.3% of ads are
newcomer-friendly; without the 156 ads that only the new search terms found,
LLM / GenAI is 3.4 points lower and the newcomer-friendly share is 19.5%. Overall
shares depend on the mix of roles; comparisons between roles do not.

### From data collection

- **German and English titles find different ads.** "Datenanalyst" found 10 ads
  that "Data Analyst" did not — over half of its results. For "Dateningenieur",
  all results were also found by "Data Engineer".
- **Skills appear throughout the ad, not only in the requirements.** Task
  descriptions already name tools such as Power BI, SQL and DAX, so skill
  extraction must cover the full text.
- **Some duplicates are invisible to the reference number.** Recruitment
  agencies sometimes post the same job twice under different IDs; these must be
  removed by comparing texts. Between the two snapshots this is common: 120 texts
  from 7 October appeared again under a new reference number on 19 November.
- **Ads turn over quickly.** Only 855 of the 2,121 ads from 7 October were found
  again six weeks later, so a second collection adds far more data than new
  search terms would.
- A data search does not return only data jobs. Only 59% of the cleaned ads have a data 
term in the title. The official occupation code is not a reliable filter either: some ads 
coded as data occupations are hardware or mechanical engineering jobs.

## The Web App

**[data-jobs-de.streamlit.app](https://data-jobs-de.streamlit.app/)** · built with Streamlit, deployed on Streamlit Community Cloud.

**From analysis to app.** `04_analysis.ipynb` exports two aggregated tables, and the app computes everything from them; no ad text reaches the app.

| Table | Rows | Content |
|---|---|---|
| `app/data/role_skills.csv` | 276 (6 roles × 46 skills) | share of each role's ads that mention, require, or only hedge each skill |
| `app/data/role_barriers.csv` | 6 (one per role) | newcomer-friendly, 3+ years, degree, alternative path, fluent German, English-language ad |

**How the fit score works.**

1. A role's **key skills** are those required in at least 1 in 10 of its ads.
2. Each key skill is **weighted** by how often it is required.
3. **Fit score** = weights of the key skills you have ÷ weights of all key skills. Labels: at least 60% *Strong fit*, 40–60% *Good start*, 20–40% *Some overlap*, below 20% *Little overlap*.

*Example:* with Python, SQL, Excel and Statistics, Data Analyst has 8 key skills; the four selected ones are required in 31.9%, 26.1%, 23.0% and 19.3% of Data Analyst ads (sum 100.3), all eight sum to 180.6, so the fit is 100.3 ÷ 180.6 = 56% (*Good start*). The most required missing skill is Power BI (27.2%), shown as "3 in 10 ads".

**Design decisions.**

- **Natural frequencies:** shares are shown as "3 in 10 ads" with an icon array of 10 squares instead of percentages, which is easier to read for non-experts.
- **Accessible colours:** light and dark themes based on Fabio Crameri's scientific colour map *oslo*, readable with colour-vision deficiencies.
- **Privacy:** only aggregated numbers are published; the ad texts stay out of the repository.

## Limitations

- **Data source:** two snapshots, six weeks apart, from one platform (Bundesagentur
  für Arbeit); ads on LinkedIn, StepStone and company sites are not included.
  Results describe this sample, not the whole market.
- **Pooled snapshots with different search terms:** the second snapshot added
  "AI Engineer" and "MLOps", which raises the share of ML / AI ads. Overall shares
  depend on this mix; the robustness checks show by how much.
- **Manual checks on the first snapshot only:** all hand-labelled samples were drawn
  before the second snapshot was added; the same rules were applied to the new ads
  without a separate spot check.
- **Fuzzy boundary of "data role":** two annotators agreed only fairly (kappa 0.37).
- **Rules, not a model:** the dictionary only finds what it lists. Every step is
  spot-checked by hand to measure how much this matters.
- **Scope of hedge cues:** "von Vorteil" can refer to a different skill in the same
  sentence, so a required skill may be counted as nice-to-have. The same applies to
  German level words ("Fluent English required, German skills are a plus").
- **Degree mentioned, not required:** "idealerweise ein Studium" counts as a degree.
- **German level scale:** the grouping follows a common CV convention, not an
  official standard.
- **Small junior group:** only 76 ads have a junior title, so differences need
  large effects to be significant.
- **Rounding in the app:** "3 in 10 ads" rounds to whole tenths, so small differences
  disappear (25% and 34% both show as 3 in 10); exact values are in the app's tables.

## Future Work

- Syntactic analysis to resolve which skill a hedge cue refers to
- A text classifier (e.g. TF-IDF + logistic regression) as a comparison to the rule-based baseline
- A second labelling round with a sharper codebook for adjacent roles
- Skill co-occurrence networks
- A spot check of the second snapshot, especially the ML / AI ads from the new search terms
- Regular collection to track changes over time (the newcomer-friendly share was 21% in the first snapshot and 16% in the second)

## Project Structure

```
data-job-ad-nlp-de/
├── data/
│   ├── raw/                  # collected ads, second snapshot in raw/2026-11-19/ (not in the repository)
│   └── processed/            # cleaned data (not in the repository)
├── notebooks/
│   ├── 00_api_test.ipynb     # testing the data source
│   ├── 01_collect.ipynb      # collecting search results and full texts
│   ├── 02_cleaning.ipynb     # cleaning, data-role filter and its evaluation
│   ├── 03_extraction.ipynb   # roles, seniority, skills, required vs. nice-to-have, entry barriers, ad language
│   └── 04_analysis.ipynb     # confidence intervals, role comparison, junior vs. senior, robustness checks
├── app/
│   ├── app.py                # Streamlit web app
│   ├── requirements.txt      # app dependencies for Streamlit Community Cloud
│   └── data/                 # aggregated tables for the web app (no ad texts)
├── .streamlit/
│   └── config.toml           # app themes (light and dark)
├── reports/
│   └── figures/              # charts used in the README and report
├── src/                      # helper from the course template (not used by the notebooks)
├── pyproject.toml            # dependencies (managed with uv)
└── README.md
```

## Getting Started

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/zeqizhao12/data-job-ad-nlp-de.git
cd data-job-ad-nlp-de
uv sync
```

Then run the notebooks in order. `01_collect.ipynb` downloads the data into
`data/raw/` (first snapshot) and `data/raw/2026-11-19/` (second snapshot); each
snapshot takes about one second or more per ad, so plan for one to two hours.

The web app runs without the raw data, from the aggregated tables in `app/data/`:

```bash
uv run streamlit run app/app.py
```

## Tech Stack

- **Language:** Python 3.13
- **Data collection:** requests
- **Data processing:** pandas, regular expressions
- **Visualisation:** matplotlib
- **Environment:** uv, Jupyter, VS Code
- **Version control:** Git, GitHub
- **Statistics:** SciPy
- **Language identification:** lingua
- **Web app:** Streamlit, deployed on Streamlit Community Cloud

## Progress

- [x] Project setup
- [x] Data source tested
- [x] Data collection
- [x] Text cleaning
- [x] Location filter, exact and near-duplicate removal
- [x] Data-role filter, evaluated against 100 hand-labelled ads and a second annotator
- [x] Role and seniority assignment
- [x] Skill extraction (46 skills) and required vs. nice-to-have split
- [x] Entry barriers: experience, degree, German level, ad language
- [x] Analysis: shares with confidence intervals, role comparison, junior vs. senior, robustness checks
- [x] Web app: skills → roles, role → skills ([live](https://data-jobs-de.streamlit.app/))
- [x] Final presentation (23 October 2026)
- [x] Second snapshot (19 November 2026): 1,768 data-role ads instead of 1,062

## Author

**Zeqi Zhao** — PhD in linguistics (Georg-August-Universität Göttingen),
transitioning into data science.

[Website](https://zeqizhao12.github.io/) ·
[LinkedIn](https://www.linkedin.com/in/zeqi-zhao-13a392402)

This project was created as part of the StackFuel Data Science portfolio
programme.
