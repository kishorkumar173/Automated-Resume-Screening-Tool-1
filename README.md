# 💼 Automated Resume Screening Tool (AI-Powered ATS)

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Scikit--Learn-1.7+-orange.svg)](https://scikit-learn.org/)
[![UI Framework](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)]()

> An industry-standard, explainable Natural Language Processing (NLP) and Machine Learning system that ingests resumes in multiple formats (PDF, DOCX, TXT), extracts applicant metadata and skills, maps them against target job descriptions, identifies must-have skill gaps, and calculates a fair, transparent ATS score via a Command-Line Interface (CLI) and an interactive Streamlit Recruiter Dashboard.

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Problem Statement & Industry Relevance](#-problem-statement--industry-relevance)
3. [ATS Workflow](#-ats-workflow)
4. [System Architecture](#-system-architecture)
5. [Key Features](#-key-features)
6. [Tech Stack](#-tech-stack)
7. [Repository Folder Structure](#-repository-folder-structure)
8. [Installation & Setup](#-installation--setup)
9. [How to Run the Project](#-how-to-run-the-project)
10. [Sample Simulation & Results](#-sample-simulation--results)
11. [GitHub Showcase & Proof-of-Work Guide](#-github-showcase--proof-of-work-guide)
12. [Interview Preparation Guide](#-interview-preparation-guide)

---

## 🚀 Project Overview

The **Automated Resume Screening Tool** is designed as a production-grade Applicant Tracking System (ATS) proof-of-work project.

In conventional recruitment, human recruiters spend an average of **6 to 10 seconds** skimming a resume or **15 to 20 hours** screening applicant pools for a single open role. Manual evaluation is prone to fatigue, keyword bias, and inconsistency.

This project delivers a complete, automated, end-to-end Python pipeline that:
- Ingests single or batch resumes across `.pdf`, `.docx`, and `.txt` files.
- Heuristically extracts candidate contact information (Name, Email, Phone, LinkedIn).
- Normalizes text with custom NLP filters that preserve domain tokens (e.g., `C++`, `C#`, `.NET`, `Node.js`).
- Matches extracted skills against a 100+ skill taxonomy.
- Separates target Job Descriptions into **Must-Have Core Skills** and **Good-to-Have Skills**.
- Calculates a calibrated **Hybrid ATS Score** (30% Contextual TF-IDF + 40% Overall Skills Overlap + 30% Must-Have Gating).
- Ranks candidates with explainable decisions (Shortlisted, Under Review, Rejected) and exports comprehensive CSV and JSON audit reports.

---

## 🏢 Problem Statement & Industry Relevance

### The Problem:
1. **High Volume Influx:** Corporate positions frequently attract 500+ applications within 48 hours.
2. **Keyword Stuffing & False Matches:** Candidates exploit naive ATS scanners by repeating buzzwords.
3. **Format Fragility:** Resumes formatted in tables, multi-column layouts, or Microsoft Word frequently break standard parsers.
4. **Lack of Explainability:** Black-box AI filters reject candidates without auditing justification.

### How ATS Systems Work in Industry:
Modern talent acquisition software (e.g., Workday, Greenhouse, Lever) uses information extraction and vector similarity to evaluate candidates across four pillars:
- **Core Skill Alignment:** Does the candidate demonstrate required technical competencies?
- **Gating Prerequisites:** Are non-negotiable must-haves met (e.g., SQL, Docker)?
- **Contextual Semantic Match:** Does the candidate's career narrative match the job domain?
- **Auditable Fair Scoring:** Is the decision transparent, objective, and reproducible?

---

## 🔄 ATS Workflow

```
[Resume Files (PDF/DOCX/TXT)]       [Job Description (TXT)]
               │                               │
               ▼                               ▼
       [Text Extractor]                [Requirement Parser]
        (pypdf / docx)                  (Must-Haves & Skills)
               │                               │
               ▼                               ▼
        [Text Cleaner]                  [Text Cleaner]
  (Lowercase, Remove Noise,         (Lowercase, Stopwords,
   Preserve C++, C#, .NET)            Normalize Tokens)
               │                               │
               ├───────────────────────────────┤
               ▼                               ▼
     [Skill Extraction]             [TF-IDF Vectorizer]
   (Taxonomy Phrase Match)          (Unigrams + Bigrams)
               │                               │
               ▼                               ▼
     [Skill Gap Analysis]           [Cosine Similarity]
  (Must-Have Gaps Identified)      (Contextual Score)
               │                               │
               └───────────────┬───────────────┘
                               ▼
                    [Hybrid Scoring Engine]
            (30% Context + 40% Skills + 30% Gating)
                               │
                               ▼
                    [Ranking & Gating Logic]
            (Shortlisted / Under Review / Rejected)
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
        [Interactive Streamlit]     [CSV & JSON Reports]
          Recruiter Dashboard        (Exported to outputs/)
```

---

## 🏗️ System Architecture

| Stage | Module | Input | Primary Logic | Output |
|---|---|---|---|---|
| **1. Ingestion** | `src/extractor.py` | `.pdf`, `.docx`, `.txt` | `pypdf`, `pdfplumber`, `python-docx` + regex contact heuristics | Raw text string, Candidate Name, Email, Phone |
| **2. Preprocessing** | `src/cleaner.py` | Raw text | Domain token preservation (`cplusplus`, `csharp`), URL/email removal, stopword filtering | Cleaned normalized token string |
| **3. Skill Matching** | `src/matcher.py` | Cleaned text, `skills_database.json` | Boundary-aware multi-word phrase matching, JD section parsing | Candidate skills, Matched skills, Missing Must-Haves |
| **4. Scoring** | `src/scorer.py` | Cleaned corpus, JD text | TF-IDF (1, 2 n-grams), Cosine similarity, Calibrated Hybrid weighting | Final ATS Score (0-100%), Tier, Explanation |
| **5. Reporting** | `src/reporter.py` | Ranked evaluations | Terminal ASCII formatter, CSV writer, JSON serializer | Terminal leaderboard, `screening_results.csv` |
| **6. User Interface** | `app.py` | Browser session | Streamlit reactive web widgets, file uploader, drill-down cards | Interactive recruiter dashboard |

---

## ✨ Key Features

- **Multi-Format Ingestion:** Seamlessly parses PDF documents, Microsoft Word files (`.docx`), and plaintext resumes.
- **Robust Tech Token Preservation:** Unlike naive cleaners that destroy symbols, custom regex mapping preserves `C++`, `C#`, `.NET`, and `Node.js`.
- **Pre-Compiled 100+ Skill Taxonomy:** Curated database encompassing Programming, Machine Learning, Web Backend, Cloud/DevOps, Databases, BI, and Soft Skills.
- **Explainable Gating Rules:** Identifies exactly which mandatory skills a candidate is missing, eliminating black-box bias.
- **Calibrated Hybrid Scoring:** Combines TF-IDF semantic context with exact skill overlap so concise high-quality resumes score accurately.
- **Synthetic Resume Generator Included:** Comes with a built-in generator script (`generate_samples.py`) that generates 5 realistic multi-tiered resumes out-of-the-box.
- **Dual Interface:** Run via high-speed CLI (`python main.py`) or via modern web GUI (`streamlit run app.py`).

---

## 💻 Tech Stack

- **Language:** Python 3.9 - 3.13
- **Data Manipulation:** `pandas`, `numpy`
- **Machine Learning & NLP:** `scikit-learn` (TF-IDF Vectorizer, Cosine Similarity)
- **Document Processing:** `pypdf`, `pdfplumber`, `python-docx`
- **PDF Generation (Synthetic Data):** `reportlab`
- **Web Dashboard:** `streamlit`

---

## 📁 Repository Folder Structure

```
Automated-Resume-Screening-Tool/
│
├── resumes/                                # Directory for candidate resumes (PDF, DOCX, TXT)
│   ├── resume_john_doe_senior_python.pdf   # Tier 1 Candidate (High Match)
│   ├── resume_priya_sharma_data_analyst.pdf# Tier 2 Candidate (Data Analyst / Medium)
│   ├── resume_michael_brown_java_backend.pdf# Tier 3 Candidate (Java Engineer / Partial)
│   ├── resume_alex_smith_frontend_dev.docx # Low Match (Frontend)
│   └── resume_emily_clark_digital_marketing.docx # Low Match (Marketing)
│
├── data/                                   # Data stores
│   ├── job_description.txt                 # Target Job Description file
│   └── skills_database.json                # Curated technical & soft skill taxonomy
│
├── src/                                    # Modular source code package
│   ├── __init__.py                         # Source package initializer
│   ├── extractor.py                        # Document parsers & contact extraction
│   ├── cleaner.py                          # NLP text cleaning & token preservation
│   ├── matcher.py                          # Skill phrase extraction & gap analysis
│   ├── scorer.py                           # TF-IDF, Cosine similarity & hybrid score
│   └── reporter.py                         # CSV, JSON & terminal output formatters
│
├── outputs/                                # Generated screening artifacts
│   ├── screening_results.csv               # Exported recruiter evaluation table
│   └── screening_summary.json              # Full hierarchical JSON audit
│
├── images/                                 # Screenshots and architecture diagrams
│
├── docs/                                   # Supplemental guides
│   ├── interview_guide.md                  # Top 10 interview questions & model answers
│   └── proof_strategy.md                   # 6-Day proof-of-work commit strategy
│
├── generate_samples.py                     # Synthetic PDF & DOCX resume generator
├── main.py                                 # Command-line entrypoint
├── app.py                                  # Interactive Streamlit Web App
├── requirements.txt                        # Pinned dependencies
├── .gitignore                              # Git exclusion rules
└── README.md                               # Project documentation
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9 or higher installed on your system.
- Git installed.

### 1. Clone or Open the Repository
```bash
cd "E:\IIT PROJECT\PYTHON 1"
```

### 2. Create and Activate Virtual Environment (Recommended)

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Project

### Option A: Run via Command-Line Interface (CLI)
To run the automated pipeline across all resumes in the `resumes/` folder against `data/job_description.txt`:

```bash
python main.py
```

**Expected Terminal Output:**
```
================================================================================
      INITIALIZING AUTOMATED RESUME SCREENING & ATS SYSTEM
================================================================================
[*] Loading skills taxonomy from: skills_database.json
    -> Cataloged 101 unique technical & soft skills.
[*] Reading Job Description from: job_description.txt
    -> Identified 23 Total Required Skills
    -> Flagged 7 Must-Have Core Skills: docker, fastapi, machine learning, pandas, python, scikit-learn, sql

[*] Processing 5 Candidate Resumes...
    [1/5] Ingesting: resume_alex_smith_frontend_dev.docx... OK
    [2/5] Ingesting: resume_emily_clark_digital_marketing.docx... OK
    [3/5] Ingesting: resume_john_doe_senior_python.pdf... OK
    [4/5] Ingesting: resume_michael_brown_java_backend.pdf... OK
    [5/5] Ingesting: resume_priya_sharma_data_analyst.pdf... OK

[*] Calculating TF-IDF Vectorization and Cosine Similarities...

=========================================================================================================
                    AUTOMATED RESUME SCREENING & ATS LEADERBOARD
=========================================================================================================
Total Candidates Evaluated : 5
Total Required Skills      : 23 (agile, aws, ci/cd, data pipelines, docker, fastapi...)
Must-Have Core Skills      : 7 (docker, fastapi, machine learning, pandas, python, scikit-learn, sql)
---------------------------------------------------------------------------------------------------------
Rank  | Candidate Name       | Score   | Status        | TF-IDF  | Skills  | Must-Have | Missing Gaps      
---------------------------------------------------------------------------------------------------------
1     | John Doe             | 81.3%   | [PASS] SHORTLISTED | 25.1%   | 69.6%   | 100.0%    | None              
2     | Michael Brown        | 38.5%   | [REJ ] REJECTED | 10.7%   | 39.1%   | 42.9%     | fastapi, machine  
3     | Priya Sharma         | 34.3%   | [REJ ] REJECTED | 7.1%    | 26.1%   | 57.1%     | docker, fastapi + 
4     | Alex Smith           | 3.1%    | [REJ ] REJECTED | 1.4%    | 4.3%    | 0.0%      | docker, fastapi + 
5     | Emily Clark          | 0.1%    | [REJ ] REJECTED | 0.1%    | 0.0%    | 0.0%      | docker, fastapi + 
=========================================================================================================
SUMMARY DECISION: 1 Shortlisted | 0 Under Review | 4 Rejected
=========================================================================================================

[+] Full ATS Report exported to CSV  : outputs/screening_results.csv
[+] Screening Summary exported to JSON: outputs/screening_summary.json
```

---

### Option B: Run via Streamlit Web Dashboard
Launch the interactive web UI:

```bash
streamlit run app.py
```
Your default web browser will open at `http://localhost:8501`.

**Dashboard Features:**
- Adjust scoring weights dynamically via sidebar sliders.
- Toggle between built-in sample resumes or upload your own files via drag-and-drop.
- View interactive KPI metric cards (Total Screened, Shortlisted, Review, Rejected).
- Inspect candidate skill gap pills (Green for matched skills, Red for missing must-haves).
- Download the generated candidate screening report with one click (`ats_screening_results.csv`).

---

## 📊 Sample Simulation & Results

### Evaluated Candidate Breakdown:

| Rank | Candidate | Format | Match Score | Status | Key Matched Skills | Flagged Must-Have Gaps |
|:---:|:---|:---:|:---:|:---:|:---|:---|
| **#1** | **John Doe** | PDF | **81.3%** | **SHORTLISTED** | Python, Scikit-learn, FastAPI, SQL, Docker, Pandas, AWS, CI/CD | *None (All 7 Must-Haves Met)* |
| **#2** | **Michael Brown** | PDF | **38.5%** | **REJECTED** | Java, Spring Boot, SQL, PostgreSQL, Docker, AWS, Git | Missing: FastAPI, Scikit-learn, ML, Pandas |
| **#3** | **Priya Sharma** | PDF | **34.3%** | **REJECTED** | Python, Pandas, SQL, Tableau, Power BI, Statistics | Missing: Docker, FastAPI, Scikit-learn |
| **#4** | **Alex Smith** | DOCX | **3.1%** | **REJECTED** | JavaScript, TypeScript, React, HTML, CSS, Node.js | Missing: All 7 Core Must-Haves |
| **#5** | **Emily Clark** | DOCX | **0.1%** | **REJECTED** | SEO, Google Ads, Content Marketing | Missing: All 7 Core Must-Haves |

---

## 📸 GitHub Showcase & Proof-of-Work Guide

To demonstrate proof-of-work on your GitHub portfolio:

1. **Initialize Git & Push:**
   ```bash
   git init
   git add .
   git commit -m "feat: complete automated resume screening tool with NLP engine and Streamlit UI"
   git branch -M main
   git remote add origin https://github.com/<your-username>/Automated-Resume-Screening-Tool.git
   git push -u origin main
   ```

2. **Screenshots to Include in `images/`:**
   - `images/terminal_leaderboard.png`: Terminal output running `python main.py`.
   - `images/streamlit_dashboard.png`: Browser view of Streamlit app showing metrics and leaderboard.
   - `images/candidate_drilldown.png`: Score breakdown and matched vs missing skill badges.
   - `images/csv_report_preview.png`: Excel or spreadsheet view of `outputs/screening_results.csv`.

---

## 🎯 Interview Preparation Guide

A detailed 10-question technical & HR interview prep guide is available in [`docs/interview_guide.md`](docs/interview_guide.md), including:
- "Explain your project" using the STAR framework.
- Why TF-IDF and Cosine Similarity are preferred over naive keyword counting.
- Why hybrid scoring avoids the failure modes of pure vector similarity.
- How to handle ReDoS and catastrophic backtracking in regex parsers.
- Scaling to 100,000+ resumes using Celery, Redis, and vector databases.
