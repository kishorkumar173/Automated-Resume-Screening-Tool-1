"""
=============================================================================
Project Title : Automated Resume Screening Tool
Module        : app.py
Description   : Modern Streamlit Web Application & Recruiter Dashboard
                for automated resume ingestion, screening, gap analysis,
                interactive scoring, candidate ranking, and CSV reporting.
=============================================================================
"""

import os
import sys
import tempfile
import pandas as pd
import streamlit as st

# Add project root to system path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.extractor import extract_resume
from src.cleaner import clean_text
from src.matcher import (
    load_skills_database,
    flatten_skills,
    extract_skills_from_text,
    parse_job_requirements,
    analyze_candidate_skills,
)
from src.scorer import (
    compute_tfidf_similarity,
    compute_hybrid_score,
    rank_candidates,
)
from src.reporter import export_to_csv


# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Automated Resume Screening Tool | HR Tech ATS",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .badge-pass {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-review {
        background-color: #FEF9C3;
        color: #854D0E;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-fail {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Helper Functions & Caching
# -----------------------------------------------------------------------------
@st.cache_resource
def get_cached_skills_db():
    db_path = os.path.join(BASE_DIR, "data", "skills_database.json")
    return load_skills_database(db_path)


def load_default_jd():
    jd_path = os.path.join(BASE_DIR, "data", "job_description.txt")
    if os.path.exists(jd_path):
        with open(jd_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# -----------------------------------------------------------------------------
# Sidebar: Settings & Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
    st.title("ATS Engine Control")
    st.caption("Configurable scoring weights & threshold criteria")

    st.subheader("⚖️ Scoring Weights")
    w_skill = st.slider("Skill Match Weight", min_value=0.1, max_value=0.7, value=0.40, step=0.05)
    w_must = st.slider("Must-Have Core Weight", min_value=0.1, max_value=0.7, value=0.30, step=0.05)
    w_tfidf = st.slider("Contextual (TF-IDF) Weight", min_value=0.1, max_value=0.7, value=0.30, step=0.05)

    total_weight = w_skill + w_must + w_tfidf
    if round(total_weight, 2) != 1.0:
        st.warning(f"Weights sum to {total_weight:.2f}. Normalizing to 100% automatically.")

    weights_dict = {
        "skill_weight": w_skill / total_weight,
        "must_have_weight": w_must / total_weight,
        "tfidf_weight": w_tfidf / total_weight,
    }

    st.divider()
    st.subheader("⚙️ Resume Ingestion Mode")
    ingest_mode = st.radio("Choose Input Source:", ["Use 5 Built-in Realistic Resumes", "Upload Custom Resumes"])

    uploaded_files = []
    if ingest_mode == "Upload Custom Resumes":
        uploaded_files = st.file_uploader(
            "Upload Resumes (.pdf, .docx, .txt)",
            type=["pdf", "docx", "doc", "txt"],
            accept_multiple_files=True
        )

    st.divider()
    st.markdown("👨‍💻 **Project:** Automated Resume Screening Tool")
    st.markdown("📌 **Author:** Proof-of-Work Portfolio Project")


# -----------------------------------------------------------------------------
# Main Dashboard UI
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">💼 Automated Resume Screening & ATS Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Industry-oriented ML/NLP screening engine with TF-IDF semantic matching, skill gap discovery, and explainable candidate ranking.</div>', unsafe_allow_html=True)

skills_db = get_cached_skills_db()
all_known_skills = flatten_skills(skills_db)

# Tab navigation
tab_screen, tab_jd, tab_taxonomy = st.tabs(["🚀 Screening & Ranking", "📝 Job Description & Must-Haves", "📚 Skills Taxonomy"])


# -----------------------------------------------------------------------------
# TAB 2: Job Description & Must-Haves Setup
# -----------------------------------------------------------------------------
with tab_jd:
    st.subheader("Job Description Configuration")
    col_jd1, col_jd2 = st.columns([2, 1])
    
    with col_jd1:
        default_jd_text = load_default_jd()
        jd_input_text = st.text_area(
            "Enter / Edit Target Job Description:",
            value=default_jd_text,
            height=320
        )

    with col_jd2:
        st.info("💡 **Gating Criteria**\nCandidate resumes will be automatically checked for these Must-Have skills. Any gap will be flagged as an ATS alert.")
        
        parsed_default = parse_job_requirements(jd_input_text, all_known_skills)
        default_must = parsed_default["must_have_skills"]

        selected_must_haves = st.multiselect(
            "Selected Must-Have Skills:",
            options=sorted(list(all_known_skills)),
            default=[s for s in default_must if s in all_known_skills]
        )
        st.write(f"Total Must-Haves: **{len(selected_must_haves)}**")


# -----------------------------------------------------------------------------
# TAB 3: Skills Taxonomy Viewer
# -----------------------------------------------------------------------------
with tab_taxonomy:
    st.subheader("Internal Skills Taxonomy Database")
    st.caption("Standardized skill ontology categorized across technology domains.")
    
    cat_cols = st.columns(3)
    categories = list(skills_db.keys())
    for idx, cat in enumerate(categories):
        col_target = cat_cols[idx % 3]
        with col_target:
            with st.expander(f"📁 {cat.replace('_', ' ').title()} ({len(skills_db[cat])})", expanded=True):
                st.write(", ".join(skills_db[cat]))


# -----------------------------------------------------------------------------
# TAB 1: Screening & Ranking Leaderboard
# -----------------------------------------------------------------------------
with tab_screen:
    # Action Trigger
    btn_col1, btn_col2 = st.columns([1, 4])
    with btn_col1:
        run_screening = st.button("⚡ Run Screening Engine", type="primary", use_container_width=True)

    # Process resumes
    resume_records = []
    
    if ingest_mode == "Use 5 Built-in Realistic Resumes":
        resumes_folder = os.path.join(BASE_DIR, "resumes")
        if os.path.exists(resumes_folder):
            for fname in os.listdir(resumes_folder):
                if os.path.splitext(fname)[1].lower() in [".pdf", ".docx", ".doc", ".txt"]:
                    fpath = os.path.join(resumes_folder, fname)
                    resume_records.append((fname, fpath, False))
    else:
        if uploaded_files:
            for uf in uploaded_files:
                # Save temporarily to disk for extraction
                suffix = os.path.splitext(uf.name)[1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(uf.getbuffer())
                    tmp_path = tmp_file.name
                resume_records.append((uf.name, tmp_path, True))

    if run_screening or "last_ranked_results" in st.session_state:
        if not resume_records:
            st.error("No resumes available to screen! Please upload files or select 'Use 5 Built-in Realistic Resumes'.")
        else:
            with st.spinner("Extracting text, cleaning tokens, mapping skills, and computing TF-IDF similarity..."):
                jd_info = parse_job_requirements(
                    jd_input_text,
                    all_known_skills,
                    custom_must_haves=selected_must_haves if selected_must_haves else None
                )
                cleaned_jd = clean_text(jd_input_text)

                extracted_data_list = []
                cleaned_corpus = []

                for fname, fpath, is_temp in resume_records:
                    try:
                        parsed = extract_resume(fpath)
                        parsed["file_name"] = fname  # Ensure original uploaded name
                        cleaned = clean_text(parsed["raw_text"])
                        cand_skills = extract_skills_from_text(parsed["raw_text"], all_known_skills)
                        gap_info = analyze_candidate_skills(cand_skills, jd_info)

                        extracted_data_list.append({
                            "extractor_data": parsed,
                            "cleaned_text": cleaned,
                            "skill_analysis": gap_info
                        })
                        cleaned_corpus.append(cleaned)
                    finally:
                        if is_temp and os.path.exists(fpath):
                            try:
                                os.remove(fpath)
                            except Exception:
                                pass

                # TF-IDF
                tfidf_sims = compute_tfidf_similarity(cleaned_corpus, cleaned_jd)

                # Scoring
                evaluated = []
                for cand_item, sim in zip(extracted_data_list, tfidf_sims):
                    gap = cand_item["skill_analysis"]
                    score_res = compute_hybrid_score(
                        tfidf_sim=sim,
                        skill_match_ratio=gap["skill_match_ratio"],
                        must_have_ratio=gap["must_have_coverage_ratio"],
                        missing_must_have_count=gap["missing_must_haves_count"],
                        weights=weights_dict
                    )
                    evaluated.append({
                        "extractor_data": cand_item["extractor_data"],
                        "skill_analysis": gap,
                        "score_details": score_res
                    })

                ranked = rank_candidates(evaluated)
                st.session_state["last_ranked_results"] = ranked
                st.session_state["last_jd_info"] = jd_info

    # Display results if available
    if "last_ranked_results" in st.session_state:
        ranked = st.session_state["last_ranked_results"]
        jd_info = st.session_state["last_jd_info"]

        # Top Metric Cards
        total_cand = len(ranked)
        shortlisted = sum(1 for c in ranked if c["score_details"]["status"] == "SHORTLISTED")
        under_review = sum(1 for c in ranked if c["score_details"]["status"] == "UNDER REVIEW")
        rejected = sum(1 for c in ranked if c["score_details"]["status"] == "REJECTED")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Resumes Screened", total_cand)
        m2.metric("✅ Shortlisted (Tier 1)", shortlisted)
        m3.metric("⚠️ Under Review (Tier 2)", under_review)
        m4.metric("❌ Rejected (Tier 3)", rejected)

        st.divider()

        # Leaderboard Table
        st.subheader("🏆 Candidate Screening Leaderboard")
        table_rows = []
        for c in ranked:
            ext = c["extractor_data"]
            sc = c["score_details"]
            sk = c["skill_analysis"]

            table_rows.append({
                "Rank": c["rank"],
                "Candidate Name": ext["candidate_name"],
                "Final ATS Score": f"{sc['final_score']:.1f}%",
                "Status": sc["status"],
                "Tier": sc["tier"],
                "TF-IDF Context": f"{sc['tfidf_score_percent']:.1f}%",
                "Skill Match": f"{sc['skill_match_percent']:.1f}%",
                "Must-Have Coverage": f"{sc['must_have_percent']:.1f}%",
                "Missing Gaps": ", ".join(sk["missing_must_haves"]) if sk["missing_must_haves"] else "None (All Met)",
                "File": ext["file_name"]
            })

        df_leaderboard = pd.DataFrame(table_rows)
        st.dataframe(df_leaderboard, use_container_width=True, hide_index=True)

        # Download CSV
        csv_path = os.path.join(BASE_DIR, "outputs", "screening_results.csv")
        export_to_csv(ranked, csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            csv_bytes = f.read()

        st.download_button(
            label="📥 Download Screening Report (CSV)",
            data=csv_bytes,
            file_name="ats_screening_results.csv",
            mime="text/csv",
        )

        st.divider()

        # Candidate Detailed Drilldown
        st.subheader("🔍 Candidate Deep-Dive & Skill Gap Analysis")
        candidate_names = [f"Rank {c['rank']}: {c['extractor_data']['candidate_name']}" for c in ranked]
        selected_idx = st.selectbox("Select Candidate to Inspect:", range(len(candidate_names)), format_func=lambda x: candidate_names[x])

        selected_candidate = ranked[selected_idx]
        sel_ext = selected_candidate["extractor_data"]
        sel_sc = selected_candidate["score_details"]
        sel_sk = selected_candidate["skill_analysis"]

        c_col1, c_col2 = st.columns([1, 2])
        
        with c_col1:
            st.markdown(f"### {sel_ext['candidate_name']}")
            status_color = "badge-pass" if sel_sc['status'] == "SHORTLISTED" else ("badge-review" if sel_sc['status'] == "UNDER REVIEW" else "badge-fail")
            st.markdown(f'<span class="{status_color}">{sel_sc["status"]} ({sel_sc["tier"]})</span>', unsafe_allow_html=True)
            
            st.markdown(f"""
            - **Email:** `{sel_ext['email']}`
            - **Phone:** `{sel_ext['phone']}`
            - **LinkedIn:** [{sel_ext['linkedin']}]({sel_ext['linkedin']})
            - **File:** `{sel_ext['file_name']}` ({sel_ext['file_type']})
            - **Word Count:** {sel_ext['word_count']} words
            """)

            st.progress(sel_sc['final_score'] / 100.0, text=f"Overall ATS Score: {sel_sc['final_score']:.1f}%")

        with c_col2:
            st.markdown("#### 🎯 Score Component Breakdown")
            sc_b1, sc_b2, sc_b3 = st.columns(3)
            sc_b1.metric("TF-IDF Semantic Match", f"{sel_sc['tfidf_score_percent']:.1f}%")
            sc_b2.metric("Overall Skills Match", f"{sel_sc['skill_match_percent']:.1f}%")
            sc_b3.metric("Must-Have Coverage", f"{sel_sc['must_have_percent']:.1f}%")

            st.markdown("#### 📋 Explainable Recruiter Assessment")
            st.info(f"**ATS Auditor Explanation:**\n{sel_sc['explanation']}")

            col_matched, col_gaps = st.columns(2)
            with col_matched:
                st.markdown(f"**✅ Matched Skills ({len(sel_sk['matched_skills'])}):**")
                if sel_sk["matched_skills"]:
                    st.write(", ".join([f"`{s}`" for s in sel_sk["matched_skills"]]))
                else:
                    st.write("*None*")

            with col_gaps:
                st.markdown(f"**🚨 Missing Must-Haves ({len(sel_sk['missing_must_haves'])}):**")
                if sel_sk["missing_must_haves"]:
                    st.error(", ".join([f"`{s}`" for s in sel_sk["missing_must_haves"]]))
                else:
                    st.success("All Must-Have Requirements Satisfied!")

        with st.expander("📄 View Extracted Raw Resume Text"):
            st.text(sel_ext["raw_text"])
    else:
        st.info("👆 Click **'⚡ Run Screening Engine'** above to process all resumes against the Job Description.")
