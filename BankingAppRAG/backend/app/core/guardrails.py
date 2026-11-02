import re
from typing import Tuple

# Patterns representing prompt injection, jailbreaks, or out-of-scope hacking
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+prompts?",
    r"you\s+are\s+now\s+in\s+(developer|dan|jailbreak|unrestricted)\s+mode",
    r"act\s+as\s+(dan|an\s+unrestricted\s+ai|jailbreak|chaos)",
    r"system\s+prompt\s+override",
    r"reveal\s+(your\s+)?(system\s+prompt|hidden\s+rules|internal\s+instructions)",
    r"print\s+(your\s+)?(instructions|source\s+code)",
    r"bypass\s+(safety|security|guardrails|filters)",
    r"drop\s+database",
    r"exec(\s+xp_cmdshell|\s+sp_)",
]

# Patterns for SQL token guardrails
DISALLOWED_SQL_KEYWORDS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bMERGE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bCREATE\b",
    r"\bSHUTDOWN\b",
    r"\bXP_CMDSHELL\b",
    r";",
    r"--",
    r"/\*",
]

def check_prompt_safety(prompt: str) -> Tuple[bool, str]:
    """
    Scans user prompt for injection attempts or adversarial inputs.
    Returns (is_safe, refusal_reason).
    """
    clean_text = prompt.lower().strip()
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, clean_text, re.IGNORECASE):
            return False, "Security Guardrail Triggered: Potential prompt injection or unauthorized system override detected."
            
    return True, ""

# prompt injection
def validate_safe_sql_query(sql_query: str, current_user_id: int) -> Tuple[bool, str]:
    """
    Enforces strict SQL token guardrails:
    1. Only single SELECT statements allowed.
    2. No destructive / modifying keywords.
    3. User-scope check: query MUST contain user_id matching current_user_id.
    """
    cleaned_sql = sql_query.strip()
    
    # Must start with SELECT
    if not cleaned_sql.upper().startswith("SELECT"):
        return False, "Guardrail Violation: Only read-only SELECT queries are authorized."
        
    # Check for forbidden mutation keywords
    for keyword_pattern in DISALLOWED_SQL_KEYWORDS:
        if re.search(keyword_pattern, cleaned_sql, re.IGNORECASE):
            return False, f"Guardrail Violation: Forbidden SQL operation or character detected ({keyword_pattern})."
            
    # Check that user_id is properly scoped in query
    user_filter_patterns = [
        rf"user_id\s*=\s*{current_user_id}",
        rf":user_id",
        rf"@user_id"
    ]
    if not any(re.search(p, cleaned_sql, re.IGNORECASE) for p in user_filter_patterns):
        return False, "Guardrail Violation: Query is missing required scoped context filter (user_id)."
        
    return True, ""
