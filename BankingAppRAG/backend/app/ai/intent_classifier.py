import re
from typing import Literal
from app.core.guardrails import check_prompt_safety

IntentType = Literal["POLICY_DOC", "USER_SQL", "REFUSE_OOS"]

# Keywords indicating personal banking data requests
USER_SQL_KEYWORDS = [
    r"\bmy\s+balance\b",
    r"\baccount\s+balance\b",
    r"\bhow\s+much\s+(money|funds?|balance)\s+do\s+i\s+have\b",
    r"\bmy\s+cards?\b",
    r"\bcredit\s+cards?\b",
    r"\bcard\s+limit\b",
    r"\boutstanding\s+balance\b",
    r"\bmy\s+loans?\b",
    r"\bemi\s+(due|amount|schedule)\b",
    r"\bmy\s+account\s+number\b",
    r"\btransactions?\b",
    r"\btransaction\s+history\b",
    r"\bpassbook\b",
    r"\brecent\s+spends?\b",
    r"\bmy\s+kyc\s+status\b",
]

# Keywords indicating general policy, rulebook, or interest rate requests
POLICY_DOC_KEYWORDS = [
    r"\binterest\s+rates?\b",
    r"\bsavings?\s+rate\b",
    r"\bfixed\s+deposit\b",
    r"\bfd\b",
    r"\bhome\s+loan\s+rules?\b",
    r"\bloan\s+eligibility\b",
    r"\brules?\b",
    r"\bcompliance\b",
    r"\bltv\b",
    r"\bforeclosure\b",
    r"\bprepayment\b",
    r"\bprocessing\s+fee\b",
    r"\btenure\b",
    r"\bpenalty\b",
    r"\bpolicy\b",
    r"\bguidelines?\b",
    r"\bdocuments?\s+required\b",
    r"\bhow\s+to\s+apply\b",
    r"\bwhat\s+is\s+the\s+rate\b",
    r"\btax\s+saver\b",
]

def classify_intent(message: str) -> IntentType:
    """
    Classifies customer message into:
    - REFUSE_OOS: If prompt injection or out-of-scope
    - USER_SQL: If requesting user-scoped personal banking data
    - POLICY_DOC: If asking general banking policy or interest rate guidelines
    """
    # 1. Check prompt safety guardrails first----
    is_safe, _ = check_prompt_safety(message)
    if not is_safe:
        return "REFUSE_OOS"

    lower_msg = message.lower().strip()

    # 2. Check personal account data keywords
    for pattern in USER_SQL_KEYWORDS:
        if re.search(pattern, lower_msg):
            return "USER_SQL"

    # 3. Check general banking policy keywords
    for pattern in POLICY_DOC_KEYWORDS:
        if re.search(pattern, lower_msg):
            return "POLICY_DOC"

    # 4. Check for banking terms in general queries
    banking_domain_terms = [
        "bank", "rate", "loan", "deposit", "account", "credit", "debit",
        "mortgage", "cibil", "score", "statement", "customer", "branch"
    ]
    if any(term in lower_msg for term in banking_domain_terms):
        return "POLICY_DOC"

    # 5. Out of scope / generic queries unrelated to banking
    return "REFUSE_OOS"
