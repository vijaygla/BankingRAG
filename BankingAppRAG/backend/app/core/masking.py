import re
from typing import Any, Dict, List, Union

def mask_account_number(acc_num: str) -> str:
    """Masks bank account number, e.g., 1029384756 -> AC******4756 or AC*******1023"""
    if not acc_num:
        return "AC********"
    clean = str(acc_num).replace(" ", "").replace("-", "")
    prefix = "AC" if not clean.startswith("AC") else ""
    raw = clean.replace("AC", "")
    if len(raw) <= 4:
        return f"{prefix}****{raw}"
    return f"{prefix}{'*' * (len(raw) - 4)}{raw[-4:]}"

def mask_credit_card(card_num: str) -> str:
    """Masks card number, e.g., 4111222233334444 -> 4111********4444"""
    if not card_num:
        return "************"
    clean = str(card_num).replace(" ", "").replace("-", "")
    if len(clean) < 8:
        return f"{clean[:2]}******{clean[-2:]}" if len(clean) >= 4 else "********"
    return f"{clean[:4]}{'*' * (len(clean) - 8)}{clean[-4:]}"

def mask_email(email: str) -> str:
    """Masks email address, e.g., customer@domain.com -> c***r@domain.com"""
    if not email or "@" not in email:
        return "*****"
    parts = email.split("@")
    user, domain = parts[0], parts[1]
    if len(user) <= 2:
        masked_user = user[0] + "*"
    else:
        masked_user = user[0] + ("*" * (len(user) - 2)) + user[-1]
    return f"{masked_user}@{domain}"

def mask_phone(phone: str) -> str:
    """Masks phone number, e.g., 9876543210 -> ******3210"""
    if not phone:
        return "******"
    clean = str(phone).strip()
    if len(clean) <= 4:
        return "****"
    return f"{'*' * (len(clean) - 4)}{clean[-4:]}"

def mask_sensitive_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively traverses dictionary and masks common sensitive financial/PII keys"""
    masked = {}
    for k, v in data.items():
        k_lower = k.lower()
        if isinstance(v, dict):
            masked[k] = mask_sensitive_dict(v)
        elif isinstance(v, list):
            masked[k] = [mask_sensitive_dict(item) if isinstance(item, dict) else item for item in v]
        elif "account_number" in k_lower or "account_no" in k_lower:
            masked[k] = mask_account_number(str(v))
        elif "card_number" in k_lower or "card_no" in k_lower:
            masked[k] = mask_credit_card(str(v))
        elif "email" in k_lower and isinstance(v, str):
            masked[k] = mask_email(v)
        elif "phone" in k_lower and isinstance(v, str):
            masked[k] = mask_phone(v)
        else:
            masked[k] = v
    return masked

def mask_text_pii(text: str) -> str:
    """Regex-based masking for raw string responses containing card numbers or accounts"""
    # 16-digit card patterns
    text = re.sub(r"\b(\d{4})[- ]?(\d{4})[- ]?(\d{4})[- ]?(\d{4})\b", r"\1********\4", text)
    # 10-digit standard account number patterns preceded by AC or Account
    text = re.sub(r"(?i)\b(AC|Account(?:\s+Number)?:?\s*)(\d{6,10})\b", 
                  lambda m: f"{m.group(1)}AC{'*' * (len(m.group(2))-4)}{m.group(2)[-4:]}", text)
    return text
