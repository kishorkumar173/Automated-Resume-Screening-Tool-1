"""
=============================================================================
Module: cleaner.py
Description: Cleans and preprocesses resume and job description text.
             Preserves domain tokens (C++, C#, Node.js, .NET) while removing
             noise, emails, phone numbers, URLs, and stopwords.
=============================================================================
"""

import re
from typing import List, Set

# Built-in lightweight English stopwords list (avoids NLTK download dependencies on new machines)
DEFAULT_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", 
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", 
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", 
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", 
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", 
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", 
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", 
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", 
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", 
    "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", 
    "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", 
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    # Resume boilerplate filler words to ignore during matching
    "curriculum", "vitae", "resume", "page", "phone", "email", "contact", "address", "profile"
}

# Domain token preservation map
TOKEN_REPLACEMENTS = {
    r"\bc\+\+\b": "cplusplus",
    r"\bc\#\b": "csharp",
    r"\b\.net\b": "dotnet",
    r"\bnode\.js\b": "nodejs",
    r"\bvue\.js\b": "vuejs",
    r"\breact\.js\b": "reactjs",
    r"\ba/b testing\b": "ab_testing",
    r"\bci/cd\b": "cicd",
}

TOKEN_RESTORATION = {
    "cplusplus": "c++",
    "csharp": "c#",
    "dotnet": ".net",
    "nodejs": "node.js",
    "vuejs": "vue.js",
    "reactjs": "react.js",
    "ab_testing": "a/b testing",
    "cicd": "ci/cd",
}


def preserve_special_tokens(text: str) -> str:
    """Safely map tokens like C++, C#, .NET so standard tokenizers do not strip them."""
    for pattern, replacement in TOKEN_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def restore_special_tokens(text: str) -> str:
    """Restore original token names if needed."""
    for token, original in TOKEN_RESTORATION.items():
        text = text.replace(token, original)
    return text


def clean_text(raw_text: str, remove_stopwords: bool = True) -> str:
    """
    Performs comprehensive text preprocessing:
    1. Lowercase conversion
    2. Preserves key technical acronyms/symbols
    3. Removes URLs, emails, phone numbers
    4. Strips bullets, non-alphanumeric noise (preserving underscores and dashes)
    5. Tokenizes and eliminates stopwords
    6. Normalizes whitespace
    """
    if not raw_text:
        return ""

    text = raw_text.lower()

    # Step 1: Preserve technical symbols
    text = preserve_special_tokens(text)

    # Step 2: Remove URLs and Links
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Step 3: Remove email addresses and phone numbers
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", text)
    text = re.sub(r"\(?\+?[0-9]{1,3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}", " ", text)

    # Step 4: Remove punctuation & symbols, replace bullet symbols
    text = re.sub(r"[•●▪■◆★✓✔\-\–\—|\\/()\[\]{}:;,\'\"`~@#$%^&*+=<>?]", " ", text)

    # Step 5: Normalize spaces
    tokens = text.split()

    # Step 6: Filter stopwords and short tokens
    if remove_stopwords:
        tokens = [token for token in tokens if token not in DEFAULT_STOPWORDS and len(token) > 1]

    cleaned = " ".join(tokens)
    return cleaned


def tokenize(text: str) -> List[str]:
    """Splits cleaned text into unique ordered token list."""
    cleaned = clean_text(text, remove_stopwords=True)
    return cleaned.split()
