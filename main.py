"""
=============================================================================
Project Title : Automated Resume Screening Tool
Entrypoint    : main.py
Description   : Full end-to-end command-line pipeline for resume ingestion,
                parsing, skill extraction, TF-IDF scoring, gap analysis,
                candidate ranking, and CSV report generation.
=============================================================================
"""

import os
import sys
import argparse
from typing import List, Dict, Any

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
from src.reporter import (
    export_to_csv,
    export_to_json,
    print_terminal_summary,
)


def run_screening_pipeline(
    resumes_dir: str = "resumes",
    jd_path: str = "data/job_description.txt",
    skills_db_path: str = "data/skills_database.json",
    output_csv: str = "outputs/screening_results.csv",
    output_json: str = "outputs/screening_summary.json",
    custom_must_haves: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Executes the automated ATS screening workflow across all resumes.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    resumes_dir = os.path.join(base_dir, resumes_dir)
    jd_path = os.path.join(base_dir, jd_path)
    skills_db_path = os.path.join(base_dir, skills_db_path)
    output_csv = os.path.join(base_dir, output_csv)
    output_json = os.path.join(base_dir, output_json)

    print("\n" + "=" * 80)
    print("      INITIALIZING AUTOMATED RESUME SCREENING & ATS SYSTEM")
    print("=" * 80)

    # 1. Verify and Load Skills Taxonomy
    if not os.path.exists(skills_db_path):
        raise FileNotFoundError(f"Skills taxonomy database missing at: {skills_db_path}")
    print(f"[*] Loading skills taxonomy from: {os.path.basename(skills_db_path)}")
    skills_db = load_skills_database(skills_db_path)
    all_known_skills = flatten_skills(skills_db)
    print(f"    -> Cataloged {len(all_known_skills)} unique technical & soft skills.")

    # 2. Verify and Load Job Description
    if not os.path.exists(jd_path):
        raise FileNotFoundError(f"Job Description file missing at: {jd_path}")
    print(f"[*] Reading Job Description from: {os.path.basename(jd_path)}")
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_raw_text = f.read()

    # 3. Parse Job Requirements and Gating Must-Haves
    jd_info = parse_job_requirements(jd_raw_text, all_known_skills, custom_must_haves)
    cleaned_jd_text = clean_text(jd_raw_text)
    print(f"    -> Identified {len(jd_info['all_required_skills'])} Total Required Skills")
    print(f"    -> Flagged {len(jd_info['must_have_skills'])} Must-Have Core Skills: {', '.join(jd_info['must_have_skills'])}")

    # 4. Ingest Resumes
    if not os.path.exists(resumes_dir) or not os.listdir(resumes_dir):
        print("[!] No resumes found. Auto-generating 5 industry-standard sample resumes...")
        from generate_samples import generate_all_sample_resumes
        generate_all_sample_resumes()

    valid_extensions = {".pdf", ".docx", ".doc", ".txt"}
    resume_files = [
        f for f in os.listdir(resumes_dir)
        if os.path.splitext(f)[1].lower() in valid_extensions
    ]

    if not resume_files:
        raise ValueError(f"No valid resumes (.pdf, .docx, .txt) found in {resumes_dir}")

    print(f"\n[*] Processing {len(resume_files)} Candidate Resumes...")

    extracted_records = []
    cleaned_resumes_corpus = []

    for idx, fname in enumerate(resume_files, start=1):
        fpath = os.path.join(resumes_dir, fname)
        print(f"    [{idx}/{len(resume_files)}] Ingesting: {fname}...", end=" ")
        
        try:
            parsed_data = extract_resume(fpath)
            candidate_cleaned_text = clean_text(parsed_data["raw_text"])
            
            # Extract skills for candidate
            cand_skills = extract_skills_from_text(parsed_data["raw_text"], all_known_skills)
            
            # Analyze gap vs JD
            gap_analysis = analyze_candidate_skills(cand_skills, jd_info)

            extracted_records.append({
                "extractor_data": parsed_data,
                "cleaned_text": candidate_cleaned_text,
                "skill_analysis": gap_analysis
            })
            cleaned_resumes_corpus.append(candidate_cleaned_text)
            print("OK")
        except Exception as err:
            print(f"FAILED ({str(err)})")

    # 5. TF-IDF Vectorization & Cosine Similarity
    print("\n[*] Calculating TF-IDF Vectorization and Cosine Similarities...")
    tfidf_similarities = compute_tfidf_similarity(cleaned_resumes_corpus, cleaned_jd_text)

    # 6. Hybrid ATS Scoring & Candidate Gatekeeping
    candidate_evaluations = []
    for cand_rec, tfidf_sim in zip(extracted_records, tfidf_similarities):
        skills_gap = cand_rec["skill_analysis"]
        
        score_details = compute_hybrid_score(
            tfidf_sim=tfidf_sim,
            skill_match_ratio=skills_gap["skill_match_ratio"],
            must_have_ratio=skills_gap["must_have_coverage_ratio"],
            missing_must_have_count=skills_gap["missing_must_haves_count"]
        )

        candidate_evaluations.append({
            "extractor_data": cand_rec["extractor_data"],
            "skill_analysis": skills_gap,
            "score_details": score_details
        })

    # 7. Candidate Ranking
    ranked_results = rank_candidates(candidate_evaluations)

    # 8. Output Display and Reporting
    print_terminal_summary(ranked_results, jd_info)
    
    csv_saved_path = export_to_csv(ranked_results, output_csv)
    json_saved_path = export_to_json(ranked_results, output_json)

    print(f"[+] Full ATS Report exported to CSV  : {csv_saved_path}")
    print(f"[+] Screening Summary exported to JSON: {json_saved_path}\n")

    return ranked_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Resume Screening Tool CLI")
    parser.add_argument("--resumes", type=str, default="resumes", help="Path to resumes folder")
    parser.add_argument("--jd", type=str, default="data/job_description.txt", help="Path to Job Description file")
    parser.add_argument("--skills", type=str, default="data/skills_database.json", help="Path to skills database")
    parser.add_argument("--output", type=str, default="outputs/screening_results.csv", help="Output CSV path")
    args = parser.parse_args()

    run_screening_pipeline(
        resumes_dir=args.resumes,
        jd_path=args.jd,
        skills_db_path=args.skills,
        output_csv=args.output
    )
