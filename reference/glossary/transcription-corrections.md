# Transcription Corrections

Known Fireflies mishearings and their corrections. The diarize skill loads this file and applies corrections when generating meeting READMEs.

**Rule:** Correct in the README output, never modify the original transcript file.

## Confirmed Corrections (from real transcripts)

| Fireflies transcribes | Correct term | Category | Source |
|----------------------|-------------|----------|--------|
| EIC | AIC (Holdings) | Company | Feb 11 block 39 |
| Green Marketway Solutions | Greenmark Waste Solutions | Company | Feb 19 block 25 |
| Green Bart | Greenmark | Company | Feb 19 block 107 |
| green marker | Greenmark | Company | Feb 19 block 925 |
| green marks | Greenmark | Company | Feb 19 ~block 612 |
| Collins | Collin Bird | Person | Feb 19 block 107 |
| Lana | Lannis (Nicholson) | Person | Feb 11 block 24 |
| Lance | Lannis (Nicholson) | Person | Feb 11 block 28, 70 |
| Navisoft | Navusoft | System | Feb 11 block 220, Feb 19 5+ instances |
| postgraph | Postgres / PostgreSQL | Technology | Feb 19 block 13 |
| Cerebra | Cerebro | Project | Feb 19 — inconsistent throughout |
| Quad | Claude | Technology | Feb 11 block 333 |
| Boo, North Carolina | Boone, North Carolina | Location | Feb 11 block 50 |
| Houlihan Loki | Houlihan Lokey | Company | Feb 11 block 91 |
| AICS | AIC's | Company | Feb 19 block 121 |

## Likely Corrections (watch for these)

| Pattern | Likely means | Why |
|---------|-------------|-----|
| "sage in tact" / "sage intact" | Sage Intacct | Fireflies splits the product name |
| "nav you soft" / "navu soft" | Navusoft | Fireflies breaks on unusual names |
| "hub spot" | HubSpot | Fireflies may split compound names |
| "fleet io" / "fleet" | Fleetio | May drop the "-io" or split it |
| "pay locality" / "pay locity" | Paylocity | Unusual name, likely to mangle |
| "three eye" / "3 eye" | 3rd Eye | Camera/telematics system |
| "samba" | Samba Safety | May drop "Safety" |
| "come erica" | Comerica | Bank name, may split |
| "web flow" | Webflow | May split |
| "rail way" | Railway | May split |
| "super base" / "supa base" | Supabase | Unusual name |
| "data demon" / "data daemon" | data-daemon | Extraction pipeline |

## How to Add Corrections

When processing a new transcript and finding a new mishearing:
1. Add it to the "Confirmed" table above with the source (meeting date + block number)
2. If you see a pattern from the "Likely" table confirmed, move it to "Confirmed"
3. Keep the "Likely" table as a watch list for terms not yet seen in real transcripts
