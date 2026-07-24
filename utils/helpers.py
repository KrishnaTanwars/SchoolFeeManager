"""
Helper functions for validation, formatting, and UI helpers.
"""

import re
from datetime import datetime, date
from typing import Optional

def format_currency(amount: float) -> str:
    """Formats float to Indian currency representation (e.g. ₹ 1,50,000.00)."""
    if amount is None:
        amount = 0.0
    val_str = f"{amount:.2f}"
    parts = val_str.split('.')
    integer_part = parts[0]
    decimal_part = parts[1]

    # Indian comma grouping logic
    if len(integer_part) > 3:
        last3 = integer_part[-3:]
        other = integer_part[:-3]
        formatted_other = ""
        while len(other) > 2:
            formatted_other = "," + other[-2:] + formatted_other
            other = other[:-2]
        formatted_other = other + formatted_other
        formatted_int = formatted_other + "," + last3
    else:
        formatted_int = integer_part

    return f"₹ {formatted_int}.{decimal_part}"

def validate_indian_mobile(mobile: str) -> bool:
    """Validates 10-digit Indian mobile number."""
    if not mobile:
        return False
    clean_mobile = re.sub(r'[\s\-+]', '', mobile)
    if clean_mobile.startswith('91') and len(clean_mobile) == 12:
        clean_mobile = clean_mobile[2:]
    return bool(re.match(r'^[6-9]\d{9}$', clean_mobile))

def format_date(d: Optional[date] = None, fmt: str = "%d-%m-%Y") -> str:
    """Formats date to DD-MM-YYYY."""
    if d is None:
        d = date.today()
    if isinstance(d, datetime):
        d = d.date()
    return d.strftime(fmt)

def parse_date(date_str: str, fmt: str = "%d-%m-%Y") -> Optional[date]:
    """Parses date string formatted as DD-MM-YYYY."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, fmt).date()
    except ValueError:
        return None
