# Ilves P2017 – District League 2026

Match schedule and live results page for Ilves junior football P2017 teams competing in the 2026 district league season.

**Live site:** https://wessmanjere.github.io/Ilves/

## Teams

| Division | Teams |
|---|---|
| P9 Level 1 | Keltainen A · Keltainen B · Keltainen C · Keltavihreä A · Keltavihreä B · Vihreä A |
| P9 Level 2 | Vihreä B |
| P10 Level 1 | Ilves / P2017 |

## Features

- Match schedules grouped by round and date
- Venue links to Google Maps
- Live results fetched automatically from the Palloliitto API (runs hourly via GitHub Actions)
- Downloadable calendar files (.ics) for each team
- Mobile-optimised layout

## Data source

Results are fetched from [tulospalvelu.palloliitto.fi](https://tulospalvelu.palloliitto.fi) using the Torneopal REST API.
The `fetch_results.py` script runs on a scheduled GitHub Actions workflow and updates `results.json` automatically.
