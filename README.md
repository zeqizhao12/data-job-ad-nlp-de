# What Do German Employers Want from Data Professionals?

An NLP analysis of job ads in the German job market for data roles, collected from the job search platform of the Bundesagentur für Arbeit (German Federal Employment Agency).

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Status](https://img.shields.io/badge/status-in%20progress-yellow)

## Project Overview

**Problem.** Job ads for data roles usually list long and varied requirements. For career switchers and people newly entering the field, it is hard to tell which skills are actually expected and how expectations differ between data roles, which usually overlap in some areas but diverge in others.

**Goal.** Collect job ads for data roles from the job search platform of the Bundesagentur für Arbeit, extract the required skills
from the ad texts, in order to ultimately answer four questions:

1. Which skills are asked for most frequently?
2. Which skills tend to appear together as skill sets?
3. How do junior and senior roles differ?
4. How do Data Analyst and Data Scientist roles differ?

**Approach.** Data collection via API, text cleaning, skill extraction from
German-language texts, exploratory analysis and visualisation.

## Data

| | |
|---|---|
| **Source** | Job search of the Bundesagentur für Arbeit |
| **Collected** | 7 October 2026 |
| **Search terms** | Data Analyst, Datenanalyst, Data Scientist, Data Engineer, Dateningenieur, Business Intelligence, Machine Learning |
| **Size** | 2,119 ads with full text (2,542 search results, 2,121 after duplicate removal; 2 ads expired before their text could be fetched) |
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

## Project Structure

```
data-job-ad-nlp-de/
├── data/
│   └── raw/                  # collected ads (not in the repository)
├── notebooks/
│   ├── 00_api_test.ipynb     # testing the data source
│   └── 01_collect.ipynb      # collecting search results and full texts
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

## Progress

- [x] Project setup
- [x] Data source tested
- [x] Data collection
- [ ] Text cleaning
- [ ] Skill extraction
- [ ] Analysis and visualisation
- [ ] Final report

## Author

**Zeqi Zhao** — PhD in linguistics (Georg-August-Universität Göttingen),
transitioning into data science.

[Website](https://zeqizhao12.github.io/) ·
[LinkedIn](https://www.linkedin.com/in/zeqi-zhao-13a392402)

This project was created as part of the StackFuel Data Science portfolio
programme.
