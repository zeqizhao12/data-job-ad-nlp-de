# What do German employers want from data people? 🔍

An NLP analysis of German job ads for data roles, collected from the job search
of the Bundesagentur für Arbeit.

## 📊 Project overview

**Problem:** Job ads for data roles list long and varied requirements. For
people entering the field, it is hard to tell which skills are actually expected
and how this differs between roles.

**Goal:** Collect job ads for data roles in Germany, extract the required skills
from the ad texts, and answer questions such as:

- Which skills are asked for most often?
- Which skills tend to appear together?
- How do junior and senior roles differ?
- How do Data Analyst and Data Scientist roles differ?

**Methods:** Data collection via API, text cleaning, skill extraction from
German-language texts, exploratory analysis and visualisation.

## 🗂️ Data source

The ads come from the job search of the Bundesagentur für Arbeit. There is no
official public API; access follows the documentation of the community project
[bundesAPI](https://github.com/bundesAPI/jobsuche-api). Since the interface is
unofficial, it may change without notice.

Raw data is not stored in this repository. It is downloaded by the collection
script.

## 🚧 Status

- [x] Project setup
- [x] Data source tested (`notebooks/00_api_test.ipynb`)
- [ ] Data collection script
- [ ] Text cleaning and skill extraction
- [ ] Analysis and visualisation

## Setup

```bash
git clone https://github.com/zeqizhao12/data-job-ad-nlp-de.git
cd data-job-ad-nlp-de
uv sync
```
