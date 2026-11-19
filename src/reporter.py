"""
=============================================================================
Module: reporter.py
Description: Generates structured CSV, JSON, and rich terminal output
             summarizing candidate evaluations, scores, and rankings.
=============================================================================
"""

import os
import csv
import json
from typing import List, Dict, Any


def export_to_csv(ranked_candidates: List[Dict[str, Any]], output_filepath: str) -> str:
    """
    Exports candidate ranking data into a clean, human-readable CSV report.
    """
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

    fieldnames = [
        "Rank",
        "Candidate Name",
        "File Name",
        "Email",
        "Phone",
        "Final ATS Score (%)",
        "Status",
        "Match Tier",
        "TF-IDF Similarity (%)",
        "Skill Match (%)",
        "Must-Have Coverage (%)",
        "Matched Skills",
        "Missing Must-Haves",
        "Candidate Skills Found",
        "Decision Explanation"
    ]

    with open(output_filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for cand in ranked_candidates:
            ext = cand["extractor_data"]
            skills = cand["skill_analysis"]
            score = cand["score_details"]

            writer.writerow({
                "Rank": cand["rank"],
                "Candidate Name": ext["candidate_name"],
                "File Name": ext["file_name"],
                "Email": ext["email"],
                "Phone": ext["phone"],
                "Final ATS Score (%)": score["final_score"],
                "Status": score["status"],
                "Match Tier": score["tier"],
                "TF-IDF Similarity (%)": score["tfidf_score_percent"],
                "Skill Match (%)": score["skill_match_percent"],
                "Must-Have Coverage (%)": score["must_have_percent"],
                "Matched Skills": ", ".join(skills["matched_skills"]) if skills["matched_skills"] else "None",
                "Missing Must-Haves": ", ".join(skills["missing_must_haves"]) if skills["missing_must_haves"] else "None (All Met)",
                "Candidate Skills Found": ", ".join(skills["candidate_skills"]) if skills["candidate_skills"] else "None",
                "Decision Explanation": score["explanation"]
            })

    return output_filepath


def export_to_json(ranked_candidates: List[Dict[str, Any]], output_filepath: str) -> str:
    """
    Exports complete hierarchical screening state to JSON for API integration.
    """
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(ranked_candidates, f, indent=2)
    return output_filepath


def print_terminal_summary(ranked_candidates: List[Dict[str, Any]], jd_info: Dict[str, Any]):
    """
    Prints an aesthetic, industry-grade ASCII summary table to the terminal.
    """
    print("\n" + "=" * 105)
    print("                    AUTOMATED RESUME SCREENING & ATS LEADERBOARD")
    print("=" * 105)
    print(f"Total Candidates Evaluated : {len(ranked_candidates)}")
    print(f"Total Required Skills      : {len(jd_info['all_required_skills'])} ({', '.join(jd_info['all_required_skills'])})")
    print(f"Must-Have Core Skills      : {len(jd_info['must_have_skills'])} ({', '.join(jd_info['must_have_skills'])})")
    print("-" * 105)

    header = f"{'Rank':<5} | {'Candidate Name':<20} | {'Score':<7} | {'Status':<13} | {'TF-IDF':<7} | {'Skills':<7} | {'Must-Have':<9} | {'Missing Gaps':<18}"
    print(header)
    print("-" * 105)

    for cand in ranked_candidates:
        name = cand["extractor_data"]["candidate_name"][:19]
        score = f"{cand['score_details']['final_score']:.1f}%"
        status = cand["score_details"]["status"]
        tfidf = f"{cand['score_details']['tfidf_score_percent']:.1f}%"
        skills_pct = f"{cand['score_details']['skill_match_percent']:.1f}%"
        must_pct = f"{cand['score_details']['must_have_percent']:.1f}%"
        
        missing = cand["skill_analysis"]["missing_must_haves"]
        missing_str = ", ".join(missing[:2]) if missing else "None"
        if len(missing) > 2:
            missing_str += f" +{len(missing)-2}"
        missing_str = missing_str[:17]

        # Status tag styling indicators
        tag = "[PASS]" if status == "SHORTLISTED" else ("[REV ]" if status == "UNDER REVIEW" else "[REJ ]")

        row = f"{cand['rank']:<5} | {name:<20} | {score:<7} | {tag} {status:<7} | {tfidf:<7} | {skills_pct:<7} | {must_pct:<9} | {missing_str:<18}"
        print(row)

    print("=" * 105)
    shortlisted_count = sum(1 for c in ranked_candidates if c["score_details"]["status"] == "SHORTLISTED")
    review_count = sum(1 for c in ranked_candidates if c["score_details"]["status"] == "UNDER REVIEW")
    rejected_count = sum(1 for c in ranked_candidates if c["score_details"]["status"] == "REJECTED")

    print(f"SUMMARY DECISION: {shortlisted_count} Shortlisted | {review_count} Under Review | {rejected_count} Rejected")
    print("=" * 105 + "\n")
