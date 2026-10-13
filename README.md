# What Do German Employers Want from Data Professionals?

A text-mining project on German job ads, with data roles as the case study. The ads are collected from the job search platform of the Bundesagentur für Arbeit (German Federal Employment Agency).

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Status](https://img.shields.io/badge/status-in%20progress-yellow)

## Project Overview

**Problem.** Job ads for data roles list long and varied requirements. For
people entering the field — graduates and career switchers — it is hard to tell
which skills are really required, which are only nice to have, and how open
employers are to newcomers.

**Goal.** Collect job ads for data roles in Germany and answer four questions:

1. Which skills are required, and which are only nice to have?
2. How open are ads to newcomers — in terms of experience, degree and German
   level?
3. Which skills tend to appear together?
4. How do expectations differ between junior and senior roles, and between
   Data Analyst and Data Scientist?

**Approach.** The project turns unstructured job ad texts into structured information about data roles, 
skills and entry requirements:
- **Data collection** via API, with retries and resumable downloads.
- **Near-duplicate detection** with text similarity to identify and remove repeated ads.
- **Rule-based text classification** of job titles, evaluated against a hand-labelled sample by two annotators (precision, recall, cohen's kappa).
- **Skill and requirement extraction** from German and English ad texts, including dealing with German compounds like "Pythonkenntnisse". 
- **Statistical comparison** between data roles and experience levels (senior vs. junior), and entry conditions (experience, degree, German level).

**Planned product.** A small web app that works in two directions:

- **Skills → roles:** enter your skills and see which data roles match them best.
- **Role → skills:** choose a role and see its most required and nice-to-have skills.

## Data

| | |
|---|---|
| **Source** | Job search of the Bundesagentur für Arbeit |
| **Collected** | 7 October 2026 |
| **Search terms** | Data Analyst, Datenanalyst, Data Scientist, Data Engineer, Dateningenieur, Business Intelligence, Machine Learning |
| **Size** | 2,119 ads with full text (2,542 search results, 2,121 after duplicate removal; 2 ads expired before their text could be fetched) |
| **After cleaning** | 1,957 ads (2,031 with a location in Germany; 32 exact and 42 near-duplicate copies removed) |
| **Content** | Title, employer, location, contract type, home office option, publication date, full ad text |

The Bundesagentur does not offer an official public API. Access follows the
documentation of the community project [bundesAPI](https://github.com/bundesAPI/jobsuche-api). 
*Note: Because the interface is unofficial, it may change without notice.*

The raw data is **not** included in this repository: the ads belong to the
Bundesagentur and the publishing employers. Running the collection notebook
recreates the dataset. Since the job market changes daily, a new run will return
a different set of ads.

## Findings So Far (subject to change)

Early observations from data collection, to be examined in the analysis:

- **German and English titles find different ads.** "Datenanalyst" found 10 ads
  that "Data Analyst" did not — over half of its results. For "Dateningenieur",
  all results were also found by "Data Engineer".
- **Skills appear throughout the ad, not only in the requirements.** Task
  descriptions already name tools such as Power BI, SQL and DAX, so skill
  extraction must cover the full text.
- **Some duplicates are invisible to the reference number.** Recruitment
  agencies sometimes post the same job twice under different IDs; these must be
  removed by comparing texts.
- A data search does not return only data jobs. Only 57% of the cleaned ads have a data 
term in the title. The official occupation code is not a reliable filter either: some ads 
coded as data occupations are hardware or mechanical engineering jobs.

## Project Structure

```
data-job-ad-nlp-de/
├── data/
│   ├── raw/                  # collected ads (not in the repository)
│   └── processed/            # cleaned data (not in the repository)
├── notebooks/
│   ├── 00_api_test.ipynb     # testing the data source
│   ├── 01_collect.ipynb      # collecting search results and full texts
│   └── 02_cleaning.ipynb     # cleaning and preparing the ads
├── src/                      # reusable code
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
`data/raw/`; the full collection takes about 35 minutes.

## Tech Stack

- **Language:** Python 3.13
- **Data collection:** requests
- **Data processing:** pandas
- **Environment:** uv, Jupyter, VS Code
- **Version control:** Git, GitHub
- **Machine learning:** scikit-learn
- **Interactive web app:** Streamlit

## Progress

- [x] Project setup
- [x] Data source tested
- [x] Data collection
- [ ] Text cleaning (in progress)
- [x] Location filter, exact and near-duplicate removal
- [ ] Data-role filter: hand-labelling a random sample of 100 ads to evaluate the title rule (in progress)
- [ ] Skill and requirement extraction
- [ ] Analysis and visualisation
- [ ] Interactive web app: skills → roles, role → skills (planned)
- [ ] Final report

## Author

**Zeqi Zhao** — PhD in linguistics (Georg-August-Universität Göttingen),
transitioning into data science.

[Website](https://zeqizhao12.github.io/) ·
[LinkedIn](https://www.linkedin.com/in/zeqi-zhao-13a392402)

This project was created as part of the StackFuel Data Science portfolio
programme.
