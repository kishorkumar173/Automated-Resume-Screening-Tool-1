"""
=============================================================================
Module: matcher.py
Description: Performs taxonomy-driven skill extraction, multi-word phrase matching,
             and must-have gap analysis between resumes and job requirements.
=============================================================================
"""

import json
import os
import re
from typing import Dict, List, Set, Any, Tuple
from src.cleaner import clean_text, preserve_special_tokens, restore_special_tokens


def load_skills_database(filepath: str) -> Dict[str, List[str]]:
    """Loads curated skills taxonomy JSON."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Skills database not found at: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_skills(skills_db: Dict[str, List[str]]) -> Set[str]:
    """Flattens categorized skills dictionary into a unified lowercase set."""
    all_skills = set()
    for category, skills in skills_db.items():
        for skill in skills:
            all_skills.add(skill.lower().strip())
    return all_skills


def extract_skills_from_text(text: str, all_skills: Set[str]) -> List[str]:
    """
    Extracts recognized skills from text using boundary-aware regex.
    Prioritizes longer multi-word phrases (e.g. 'machine learning') before single words ('machine').
    """
    if not text:
        return []

    # Pre-process text to standardize case and preserve symbols like C++, C#, .NET
    normalized_text = preserve_special_tokens(text.lower())
    
    found_skills = set()
    
    # Sort skills by length descending so longer phrases match first
    sorted_skills = sorted(list(all_skills), key=len, reverse=True)

    for skill in sorted_skills:
        # Standardize skill token representation
        preserved_skill = preserve_special_tokens(skill)
        
        # Word-boundary regex pattern
        # Escape for regex safely
        escaped_pattern = r"\b" + re.escape(preserved_skill) + r"\b"
        if re.search(escaped_pattern, normalized_text):
            found_skills.add(skill)

    return sorted(list(found_skills))


def parse_job_requirements(
    jd_raw_text: str,
    all_skills: Set[str],
    custom_must_haves: List[str] = None
) -> Dict[str, Any]:
    """
    Analyzes the Job Description to identify all required skills,
    distinguishing Must-Have (core) skills from Good-to-Have (secondary) skills.
    """
    # 1. Extract all skills present anywhere in the JD
    all_jd_skills = extract_skills_from_text(jd_raw_text, all_skills)

    # 2. Identify Must-Have skills:
    must_haves = set()
    if custom_must_haves:
        for s in custom_must_haves:
            must_haves.add(s.lower().strip())
    else:
        # Heuristic section parser: Look for "must-have", "core", "required", "minimum" sections
        lines = jd_raw_text.split("\n")
        in_must_have_section = False
        must_have_buffer = []

        for line in lines:
            line_lower = line.lower().strip()
            if any(header in line_lower for header in ["must-have", "must have", "core skills", "core requirements", "minimum qualifications"]):
                in_must_have_section = True
                continue
            elif in_must_have_section and any(stop in line_lower for stop in ["good-to-have", "good to have", "nice to have", "preferred", "qualifications", "responsibilities", "overview"]):
                in_must_have_section = False
            
            if in_must_have_section:
                must_have_buffer.append(line)

        section_text = " ".join(must_have_buffer)
        extracted_from_section = extract_skills_from_text(section_text, all_skills)
        if extracted_from_section:
            must_haves = set(extracted_from_section)
        else:
            # Fallback: Top skills found in JD
            must_haves = set(all_jd_skills[:min(5, len(all_jd_skills))])

    # 3. Good-to-Have skills are remaining JD skills not in must-haves
    good_to_have = [s for s in all_jd_skills if s not in must_haves]

    return {
        "all_required_skills": all_jd_skills,
        "must_have_skills": sorted(list(must_haves)),
        "good_to_have_skills": sorted(good_to_have),
    }


def analyze_candidate_skills(
    candidate_skills: List[str],
    jd_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes exact overlap and gaps between candidate skills and job requirements.
    """
    cand_set = set(candidate_skills)
    req_set = set(jd_requirements["all_required_skills"])
    must_set = set(jd_requirements["must_have_skills"])
    good_set = set(jd_requirements["good_to_have_skills"])

    matched_skills = sorted(list(cand_set.intersection(req_set)))
    matched_must_haves = sorted(list(cand_set.intersection(must_set)))
    missing_must_haves = sorted(list(must_set.difference(cand_set)))
    missing_good_to_have = sorted(list(good_set.difference(cand_set)))
    additional_skills = sorted(list(cand_set.difference(req_set)))

    # Calculation metrics
    skill_match_ratio = len(matched_skills) / max(len(req_set), 1)
    must_have_coverage_ratio = len(matched_must_haves) / max(len(must_set), 1)

    return {
        "candidate_skills": candidate_skills,
        "matched_skills": matched_skills,
        "matched_must_haves": matched_must_haves,
        "missing_must_haves": missing_must_haves,
        "missing_good_to_have": missing_good_to_have,
        "additional_skills": additional_skills,
        "total_skills_found": len(candidate_skills),
        "matched_skills_count": len(matched_skills),
        "missing_must_haves_count": len(missing_must_haves),
        "skill_match_ratio": round(skill_match_ratio, 4),
        "must_have_coverage_ratio": round(must_have_coverage_ratio, 4),
    }
