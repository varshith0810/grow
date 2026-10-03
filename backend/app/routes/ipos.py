from __future__ import annotations

from datetime import datetime, timezone
import httpx
from fastapi import APIRouter

router = APIRouter()

NSE_BASE = "https://www.nseindia.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/154 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": NSE_BASE + "/market-data/all-upcoming-issues-ipo",
}

FALLBACK_OPEN = [
    {"company":"Nityas Gems & Jewellery","board":"Mainboard","open_date":"2026-09-30","close_date":"2026-10-05","price_band":"₹70–₹75","status":"open"},
    {"company":"Vishal Nirmiti","board":"Mainboard","open_date":"2026-09-30","close_date":"2026-10-05","price_band":"₹208–₹220","status":"open"},
    {"company":"EverestIMS Technologies","board":"SME","open_date":"2026-09-29","close_date":"2026-10-05","price_band":"₹80–₹85","status":"open"},
    {"company":"Shree TNB Polymers","board":"SME","open_date":"2026-09-28","close_date":"2026-10-05","price_band":"₹50–₹53","status":"open"},
    {"company":"Dove Soft","board":"SME","open_date":"2026-09-30","close_date":"2026-10-05","price_band":"₹104–₹111","status":"open"},
    {"company":"Omara Ventures","board":"SME","open_date":"2026-09-30","close_date":"2026-10-05","price_band":"₹296–₹311","status":"open"},
    {"company":"Sollfege Smart Electronics","board":"SME","open_date":"2026-09-30","close_date":"2026-10-05","price_band":"₹55","status":"open"},
    {"company":"SJP Ultrasonic","board":"SME","open_date":"2026-09-30","close_date":"2026-10-05","price_band":"₹67","status":"open"},
    {"company":"Eventions","board":"SME","open_date":"2026-09-30","close_date":"2026-10-05","price_band":"₹112–₹118","status":"open"},
    {"company":"Paramount Syntex","board":"SME","open_date":"2026-09-30","close_date":"2026-10-06","price_band":"₹119–₹127","status":"open"},
]
FALLBACK_UPCOMING = [
    {"company":"R K Fashion Accessories","board":"SME","open_date":"2026-10-05","close_date":None,"price_band":"TBA","status":"upcoming"},
    {"company":"Reliance JIO","board":"Mainboard","open_date":None,"close_date":None,"price_band":"TBA","status":"upcoming"},
]

def _date(value):
    if not value:
        return None
    text = str(value)
    for fmt in ("%d-%b-%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:11], fmt).date().isoformat()
        except ValueError:
            pass
    return text[:10]

def _price(value):
    if value is None or value == "":
        return "TBA"
    if isinstance(value, (int, float)):
        return f"₹{value:g}"
    return str(value).replace(" ", "")

def _map_issue(row, status):
    return {
        "company": row.get("companyName") or row.get("company") or row.get("name") or row.get("symbol") or "Unknown",
        "board": row.get("securityType") or row.get("series") or row.get("issueType") or "IPO",
        "open_date": _date(row.get("issueStartDate") or row.get("startDate")),
        "close_date": _date(row.get("issueEndDate") or row.get("endDate")),
        "price_band": _price(row.get("issuePrice") or row.get("priceBand")),
        "status": status,
        "subscription": row.get("noOfTime"),
    }

def _fetch():
    with httpx.Client(headers=HEADERS, timeout=12, follow_redirects=True) as client:
        client.get(NSE_BASE)
        current = client.get(NSE_BASE + "/api/ipo-current-issue")
        upcoming = client.get(NSE_BASE + "/api/all-upcoming-issues?category=ipo")
        current.raise_for_status()
        upcoming.raise_for_status()
        current_rows = current.json() if isinstance(current.json(), list) else []
        upcoming_rows = upcoming.json() if isinstance(upcoming.json(), list) else []
        return (
            [_map_issue(x, "open") for x in current_rows],
            [_map_issue(x, "upcoming") for x in upcoming_rows],
        )

@router.get("")
def ipos():
    try:
        open_issues, upcoming = _fetch()
        if open_issues or upcoming:
            return {"source":"NSE","updated_at":datetime.now(timezone.utc).isoformat(), "open":open_issues, "upcoming":upcoming}
    except Exception:
        pass
    return {"source":"NSE-fallback","updated_at":datetime.now(timezone.utc).isoformat(), "open":FALLBACK_OPEN, "upcoming":FALLBACK_UPCOMING}
