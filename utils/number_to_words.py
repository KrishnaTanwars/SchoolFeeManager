"""
Indian Currency and Number-to-Words Converter for Receipt Generation.
Converts amounts to format: "One Lakh Fifty Four Thousand Two Hundred Fifty Rupees Only"
"""

UNITS = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen"
]

TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"
]

def _convert_below_thousand(n: int) -> str:
    words = []
    if n >= 100:
        words.append(UNITS[n // 100] + " Hundred")
        n %= 100
    if n >= 20:
        words.append(TENS[n // 10])
        if n % 10 > 0:
            words.append(UNITS[n % 10])
    elif n > 0:
        words.append(UNITS[n])
    return " ".join(words)

def number_to_words_indian(amount: float) -> str:
    """
    Converts a float/int amount to Indian currency in words.
    Example: 1234567.89 -> One Crore Twenty Three Lakh Forty Five Thousand Six Hundred Seventy Eight Rupees and Eighty Nine Paise Only
    """
    if amount is None or amount < 0:
        return "Zero Rupees Only"
    
    amount_round = round(amount, 2)
    rupees = int(amount_round)
    paise = int(round((amount_round - rupees) * 100))

    if rupees == 0 and paise == 0:
        return "Zero Rupees Only"

    parts = []

    # Crores (1,00,00,000)
    crores = rupees // 10000000
    rupees %= 10000000

    # Lakhs (1,00,000)
    lakhs = rupees // 100000
    rupees %= 100000

    # Thousands (1,000)
    thousands = rupees // 1000
    rupees %= 1000

    # Remaining hundreds/tens/units
    remaining = rupees

    if crores > 0:
        parts.append(_convert_below_thousand(crores) + " Crore")
    if lakhs > 0:
        parts.append(_convert_below_thousand(lakhs) + " Lakh")
    if thousands > 0:
        parts.append(_convert_below_thousand(thousands) + " Thousand")
    if remaining > 0:
        parts.append(_convert_below_thousand(remaining))

    rupees_str = " ".join(parts).strip()
    if not rupees_str:
        rupees_str = "Zero"

    res = f"{rupees_str} Rupee" if rupees_str == "One" else f"{rupees_str} Rupees"

    if paise > 0:
        paise_str = _convert_below_thousand(paise)
        res += f" and {paise_str} Paise"

    res += " Only"
    return res
