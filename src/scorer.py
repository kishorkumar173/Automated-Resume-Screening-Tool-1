"""
=============================================================================
Module: scorer.py
Description: Calculates TF-IDF vectorization, Cosine Similarity, and computes
             a calibrated Hybrid ATS Score combining semantic similarity,
             hard skills match, and must-have gatekeeping.
=============================================================================
"""

from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.cleaner import clean_text


def compute_tfidf_similarity(
    cleaned_resumes: List[str],
    cleaned_jd: str
) -> List[float]:
    """
    Computes Cosine Similarity between Job Description and candidate resumes
    using TF-IDF with unigrams and bigrams.
    """
    corpus = [cleaned_jd] + cleaned_resumes
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_df=0.95,
        min_df=1,
        sublinear_tf=True
    )

    tfidf_matrix = vectorizer.fit_transform(corpus)
    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]
    
    similarity_scores = cosine_similarity(resume_vectors, jd_vector)
    return [round(float(score[0]), 4) for score in similarity_scores]


def compute_hybrid_score(
    tfidf_sim: float,
    skill_match_ratio: float,
    must_have_ratio: float,
    missing_must_have_count: int,
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Computes Calibrated Hybrid ATS Score:
    1. Calibrated Contextual Relevance (TF-IDF Cosine Similarity) [Weight: 30%]
       - In NLP document matching, resume-to-JD cosine similarity typically ranges from 0.05 to 0.40.
       - A similarity of 0.30+ represents exceptional contextual alignment.
       - Calibrated Context = min(1.0, tfidf_sim / 0.32)
    2. Overall Skill Match Ratio (Direct taxonomy overlap) [Weight: 40%]
    3. Must-Have Coverage Ratio (Core prerequisite gating) [Weight: 30%]

    Decision Rules:
    - SHORTLISTED  : Score >= 65% AND Missing Must-Haves == 0
    - UNDER REVIEW : Score >= 45% AND Missing Must-Haves <= 2
    - REJECTED     : Score < 45% OR Missing Must-Haves >= 3
    """
    if weights is None:
        weights = {
            "tfidf_weight": 0.30,
            "skill_weight": 0.40,
            "must_have_weight": 0.30,
        }

    w_tfidf = weights.get("tfidf_weight", 0.30)
    w_skill = weights.get("skill_weight", 0.40)
    w_must = weights.get("must_have_weight", 0.30)

    # Calibrate TF-IDF similarity to 0.0 - 1.0 contextual range
    calibrated_tfidf = min(1.0, tfidf_sim / 0.32)

    # Base weighted ATS score
    raw_ats_score = (
        (calibrated_tfidf * w_tfidf) +
        (skill_match_ratio * w_skill) +
        (must_have_ratio * w_must)
    ) * 100.0

    # ATS Gating Penalty: Penalize heavy missing must-haves
    if missing_must_have_count >= 3:
        raw_ats_score = min(raw_ats_score, 42.0)
    elif missing_must_have_count == 2:
        raw_ats_score = min(raw_ats_score, 58.0)

    final_score = round(max(0.0, min(100.0, raw_ats_score)), 2)

    # Decision Matrix
    if final_score >= 65.0 and missing_must_have_count == 0:
        status = "SHORTLISTED"
        tier = "Tier 1: High Match"
        reason = "Candidate satisfies all mandatory requirements and exhibits strong contextual & technical competency."
    elif final_score >= 45.0 and missing_must_have_count <= 2:
        status = "UNDER REVIEW"
        tier = "Tier 2: Moderate Match"
        reason = f"Candidate shows good potential with {missing_must_have_count} must-have skill gap(s). Flagged for hiring manager review."
    else:
        status = "REJECTED"
        tier = "Tier 3: Low Match / Critical Gap"
        if missing_must_have_count >= 3:
            reason = f"Candidate missing {missing_must_have_count} mandatory must-have core skills."
        else:
            reason = "Overall technical match and contextual relevance are below the qualification cutoff."

    return {
        "final_score": final_score,
        "tfidf_score_percent": round(tfidf_sim * 100.0, 2),
        "calibrated_tfidf_percent": round(calibrated_tfidf * 100.0, 2),
        "skill_match_percent": round(skill_match_ratio * 100.0, 2),
        "must_have_percent": round(must_have_ratio * 100.0, 2),
        "status": status,
        "tier": tier,
        "explanation": reason,
    }


def rank_candidates(candidate_evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks candidates descending by Final ATS Score,
    then by Must-Have coverage, and finally by TF-IDF similarity.
    """
    sorted_candidates = sorted(
        candidate_evaluations,
        key=lambda x: (
            x["score_details"]["final_score"],
            x["skill_analysis"]["must_have_coverage_ratio"],
            x["score_details"]["tfidf_score_percent"]
        ),
        reverse=True
    )

    for rank_idx, cand in enumerate(sorted_candidates, start=1):
        cand["rank"] = rank_idx

    return sorted_candidates
