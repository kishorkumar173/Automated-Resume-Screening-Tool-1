"""
=============================================================================
Module: extractor.py
Description: Ingests resumes in PDF, DOCX, and TXT formats.
             Extracts raw text and metadata (Name, Email, Phone, Social links).
=============================================================================
"""

import os
import re
from typing import Dict, Any, Optional


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pypdf for high-speed parsing,
    with fallback to pdfplumber if text is sparse.
    """
    extracted_text = []

    # Attempt 1: pypdf (fastest and lightweight)
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)
        if extracted_text and len(" ".join(extracted_text).strip()) > 50:
            return "\n".join(extracted_text)
    except Exception:
        pass

    # Attempt 2: pdfplumber fallback
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)
        if extracted_text:
            return "\n".join(extracted_text)
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF '{file_path}': {str(e)}")

    return "\n".join(extracted_text)


def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a Word document (.docx) including body paragraphs and tables.
    """
    try:
        import docx
        doc = docx.Document(file_path)
        full_text = []

        # Extract text from paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))

        return "\n".join(full_text)
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX '{file_path}': {str(e)}")


def extract_text_from_txt(file_path: str) -> str:
    """
    Extracts plain text with multi-encoding fallback (UTF-8, Latin-1, CP1252).
    """
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Could not decode text file '{file_path}' using supported encodings.")


def extract_candidate_info(raw_text: str, file_name: str) -> Dict[str, Optional[str]]:
    """
    Extracts candidate contact information and name from raw resume text.
    """
    # Email regex pattern
    email_pattern = r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b"
    email_match = re.search(email_pattern, raw_text)
    email = email_match.group(0) if email_match else "Not Found"

    # Linear non-backtracking phone regex pattern
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    phone_match = re.search(phone_pattern, raw_text)
    phone = phone_match.group(0).strip() if phone_match else "Not Found"

    # LinkedIn / GitHub URLs
    linkedin_match = re.search(r"(linkedin\.com/in/[a-zA-Z0-9_-]+)", raw_text, re.IGNORECASE)
    github_match = re.search(r"(github\.com/[a-zA-Z0-9_-]+)", raw_text, re.IGNORECASE)
    linkedin = f"https://{linkedin_match.group(0)}" if linkedin_match else "Not Found"
    github = f"https://{github_match.group(0)}" if github_match else "Not Found"

    # Heuristic for Name: First non-empty line of resume, excluding standard keywords
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    candidate_name = None
    for line in lines[:5]:
        lower_line = line.lower()
        if any(skip in lower_line for skip in ["resume", "curriculum vitae", "cv", "profile", "contact", "email", "phone", "summary"]):
            continue
        # If line is short and looks like a name (words, letters, spaces)
        if 2 <= len(line.split()) <= 4 and re.match(r"^[A-Za-z\s.'-]+$", line):
            candidate_name = line.strip()
            break

    if not candidate_name:
        # Fallback to sanitized file name
        base = os.path.splitext(file_name)[0]
        cleaned_base = re.sub(r"[_-]", " ", base)
        candidate_name = cleaned_base.title()

    return {
        "name": candidate_name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
    }


def extract_resume(file_path: str) -> Dict[str, Any]:
    """
    Main dispatch function: Identifies file type, extracts text, and extracts metadata.
    Returns a unified dictionary with filename, text, and parsed contact info.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_name = os.path.basename(file_path)
    extension = os.path.splitext(file_name)[1].lower()

    if extension == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif extension in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(file_path)
    elif extension == ".txt":
        raw_text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format '{extension}'. Please provide .pdf, .docx, or .txt.")

    contact_info = extract_candidate_info(raw_text, file_name)

    return {
        "file_name": file_name,
        "file_path": file_path,
        "file_type": extension,
        "raw_text": raw_text,
        "word_count": len(raw_text.split()),
        "candidate_name": contact_info["name"],
        "email": contact_info["email"],
        "phone": contact_info["phone"],
        "linkedin": contact_info["linkedin"],
        "github": contact_info["github"],
    }
