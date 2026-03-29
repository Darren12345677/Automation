from playwright.sync_api import Page

CITIBANK_NAME = "CITI"
CITIBANK_URL = "https://www.citibank.com.sg/personal-banking/deposits/fixed-deposit-account#tabs-5847e28654-item-eac3d14f73-tab"


# Tenure header text → normalised months.
# The Citibank table uses "1 Week", "2 Weeks", "1 Month" etc. as column headers.
_TENURE_HEADER_MAP: dict[str, int | float] = {
    "1 Week":   0.25,
    "2 Weeks":  0.5,
    "1 Month":  1,
    "2 Month":  2,
    "3 Month":  3,
    "6 Month":  6,
    "12 Month": 12,
    "24 Month": 24,
    "36 Month": 36,
}


def citibank_processor(page: Page) -> list[dict]:
    """
    Parses Citibank's wide tiered FD table:

      Placement Amount       | 1 Week | 2 Weeks | 1 Month | ... | 36 Month
      SGD10,000 - SGD50,000  | 0.20%  | 0.20%   | 0.60%   | ... | 0.10%
      ...

    Returns one record per (placement_tier, tenure) combination,
    shaped consistently with the other processors:

      {
        "placement_tier": "SGD10,000 - SGD50,000",
        "tenure_months":  6,
        "rate":           0.60,
        "min_deposit":    10_000,   # lower bound of the tier
      }
    """
    tables = page.locator("table").all()
    target_table = None

    # Identify the right table by its first header cell
    for table in tables:
        headers = table.locator("td").all_text_contents()
        headers = [h.strip() for h in headers]
        if headers and "Placement Amount" in headers[0]:
            target_table = table
            break

    if target_table is None:
        raise Exception("Citibank: could not find the FD rate table")

    # --- Parse data rows ---
    rows = target_table.locator("tbody tr").all()
    data = []
    headers = [c.strip() for c in rows[0].locator("td").all_text_contents()] # (column names)

    for i in range(1, len(rows)):
        row = [c.strip() for c in rows[i].locator("td").all_text_contents()]
        if len(row) != len(headers):
            continue

        placement_tier = row[0]  # e.g. "SGD10,000 - SGD50,000"
        min_deposit = _parse_min_deposit(placement_tier)

        for i in range(1, len(headers)):
            tenure_label = headers[i]          # e.g. "6 Month"
            tenure_months = _TENURE_HEADER_MAP.get(tenure_label)
            rate = _parse_rate(row[i])

            if tenure_months is None or rate is None:
                continue

            data.append({
                "placement_tier": placement_tier,
                "tenure_months":  tenure_months,
                "rate":           rate,
                "min_deposit":    min_deposit,
            })

    return data


# ── helpers ───────────────────────────────────────────────────────────────────

def _parse_rate(text: str) -> float | None:
    """'0.60%' → 0.60.  Returns None if no valid number found."""
    import re
    m = re.search(r"(\d+\.?\d*)\s*%", text)
    return float(m.group(1)) if m else None


def _parse_min_deposit(tier: str) -> int:
    """
    Extract the lower bound from a tier string.
    'SGD10,000 - SGD50,000' → 10000
    Falls back to 0 if parsing fails.
    """
    import re
    m = re.search(r"SGD([\d,]+)", tier)
    if m:
        return int(m.group(1).replace(",", ""))
    return 0
