#!/usr/bin/env python3
"""Write TÜİK's inflation into params.json, from TCMB's EVDS service.

The app reads params.json about once a month; this keeps the TÜİK half of it
current without anyone typing a number. Two figures come out of the consumer
price index (TP.FG.J0):

  annual_percent   this month's index over the same month last year — the
                   headline rate.
  rent_cap_percent the twelve-month average over the previous twelve-month
                   average — the ceiling the law puts on a rent rise.

Nothing else in the file is touched: the ENAG reading and every tax year are
left exactly as they are. If anything looks wrong — a missing key, a short
series, a move too large to be real — the file is left alone and the job
fails loudly, because a wrong rate is worse than a stale one.

Usage: EVDS_API_KEY=... python3 update_tuik.py [params.json]
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import date

SERIES = "TP.FG.J0"
EVDS = "https://evds2.tcmb.gov.tr/service/evds/series={series}&startDate={start}&endDate={end}&type=json"
# A monthly index does not move by this much; anything larger is a bad read.
MAX_PLAUSIBLE_ANNUAL = 500.0


def fetch_index(key: str, months: int = 30) -> list[tuple[str, float]]:
    """The last `months` monthly index values, oldest first, as (YYYY-MM, value)."""
    today = date.today()
    start_year = today.year - (months // 12 + 1)
    url = EVDS.format(
        series=SERIES,
        start=f"01-01-{start_year}",
        end=today.strftime("%d-%m-%Y"),
    )
    request = urllib.request.Request(url, headers={"key": key, "User-Agent": "cari-takip-parametreler"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)

    field = SERIES.replace(".", "_")
    out: list[tuple[str, float]] = []
    for row in payload.get("items", []):
        raw = row.get(field)
        if raw in (None, "", "null"):
            continue
        # EVDS dates come as "MM-YYYY" for monthly series.
        month, year = row["Tarih"].split("-")
        out.append((f"{year}-{month}", float(str(raw).replace(",", "."))))
    return out[-months:]


def readings(index: list[tuple[str, float]]) -> dict[str, object]:
    if len(index) < 24:
        raise SystemExit(f"EVDS returned only {len(index)} months; need 24 for the twelve-month average.")

    values = [v for _, v in index]
    period = index[-1][0]

    annual = (values[-1] / values[-13] - 1) * 100
    this_year = sum(values[-12:]) / 12
    last_year = sum(values[-24:-12]) / 12
    cap = (this_year / last_year - 1) * 100

    for name, value in (("annual", annual), ("cap", cap)):
        if not 0 < value < MAX_PLAUSIBLE_ANNUAL:
            raise SystemExit(f"{name} came out as {value:.2f}% — refusing to write that.")

    return {
        "annual_percent": round(annual, 2),
        "rent_cap_percent": round(cap, 2),
        "period": period,
    }


def main() -> None:
    key = os.environ.get("EVDS_API_KEY")
    if not key:
        raise SystemExit("EVDS_API_KEY is not set. Add it as a repository secret.")

    path = sys.argv[1] if len(sys.argv) > 1 else "params.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    reading = readings(fetch_index(key))
    previous = data.get("inflation", {}).get("tuik", {})
    if previous == reading:
        print(f"TÜİK unchanged ({reading['period']}): nothing to write.")
        return

    data.setdefault("inflation", {})["tuik"] = reading
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"TÜİK {reading['period']}: annual {reading['annual_percent']}%, rent ceiling {reading['rent_cap_percent']}%")


if __name__ == "__main__":
    main()
