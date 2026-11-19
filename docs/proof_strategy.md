# 📅 6-Day Proof-of-Work & Portfolio Building Strategy

Follow this step-by-step roadmap to build and document your project on GitHub so it stands out to technical recruiters and course evaluators.

---

## 🗓️ Day 1: Foundation & Project Architecture Setup
- **Tasks:**
  - Initialize local Git repository in `E:\IIT PROJECT\PYTHON 1`.
  - Create directory structure (`data/`, `resumes/`, `src/`, `outputs/`, `images/`, `docs/`).
  - Create `skills_database.json` and `job_description.txt`.
- **Git Commit Message:**
  `feat: initialize project structure, skills taxonomy database, and target job description`
- **Proof / Screenshot to Capture:**
  - VS Code or terminal showing the organized folder tree.

---

## 🗓️ Day 2: Multi-Format Document Ingestion & Text Extraction
- **Tasks:**
  - Implement `src/extractor.py` for PDF, DOCX, and TXT parsing.
  - Implement regex metadata extractor (Name, Email, Phone, Socials).
  - Implement `generate_samples.py` to auto-generate synthetic candidates.
- **Git Commit Message:**
  `feat: implement multi-format resume extractor (PDF/DOCX/TXT) with contact heuristic parser`
- **Proof / Screenshot to Capture:**
  - Terminal output of `generate_samples.py` showing generated PDF and DOCX files.

---

## 🗓️ Day 3: NLP Preprocessing & Domain Token Preservation
- **Tasks:**
  - Implement `src/cleaner.py` for tokenization, lowercasing, and stopword removal.
  - Add domain token preservation logic (`c++`, `c#`, `.net`, `node.js`).
  - Implement `src/matcher.py` for boundary-aware multi-word skill extraction.
- **Git Commit Message:**
  `feat: add NLP text preprocessor with technical symbol preservation and phrase matching`
- **Proof / Screenshot to Capture:**
  - Python console test showing cleaned tokens and extracted skills for John Doe.

---

## 🗓️ Day 4: TF-IDF Vectorization, Hybrid Scoring & Gap Analysis
- **Tasks:**
  - Implement `src/scorer.py` with Scikit-learn TF-IDF Vectorizer and Cosine Similarity.
  - Implement the 3-tier Hybrid Scoring equation and ATS Gating Rules.
  - Add candidate ranking logic.
- **Git Commit Message:**
  `feat: implement TF-IDF cosine similarity vectorizer and calibrated hybrid ATS scoring engine`
- **Proof / Screenshot to Capture:**
  - Terminal screenshot of candidate scores and missing must-haves.

---

## 🗓️ Day 5: Reporting Engine & Streamlit Recruiter Dashboard
- **Tasks:**
  - Implement `src/reporter.py` for CSV, JSON, and ASCII leaderboard outputs.
  - Build `app.py` Streamlit dashboard with candidate deep-dive inspection.
  - Verify end-to-end execution of `main.py` and `app.py`.
- **Git Commit Message:**
  `feat: build interactive Streamlit recruiter dashboard and automated CSV reporting system`
- **Proof / Screenshot to Capture:**
  - Streamlit browser view showing the interactive leaderboard and candidate score breakdown card.

---

## 🗓️ Day 6: Documentation, GitHub Repository & Video Demo
- **Tasks:**
  - Write comprehensive `README.md` with ASCII architecture and instructions.
  - Push repository to GitHub.
  - Record a 90-second Loom or screen recording walking through the tool.
  - Share on LinkedIn with project highlights!
- **Git Commit Message:**
  `docs: finalize production README, architecture documentation, and interview guide`
- **Proof / Screenshot to Capture:**
  - Published GitHub repository homepage preview.
