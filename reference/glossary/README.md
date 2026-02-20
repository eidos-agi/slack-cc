# Greenmark Glossary

Canonical terms, spellings, and definitions for Greenmark Waste Solutions. Used by the diarize skill to correct transcript errors and by anyone onboarding into the organization.

## Files

| File | What it covers | Primary consumer |
|------|---------------|-----------------|
| [transcription-corrections.md](transcription-corrections.md) | Known Fireflies mishearings → correct terms | Diarize skill |
| [systems.md](systems.md) | 15 vendor systems — correct names, abbreviations, what they do | Everyone |
| [entities.md](entities.md) | Business entities, locations, and their aliases | Everyone |
| [technology.md](technology.md) | Tech stack — Cerebro, data-daemon, Railway, etc. | Daniel, engineers |
| [financial.md](financial.md) | Accounting/finance terms Alex uses | Diarize skill, onboarding |
| [industry.md](industry.md) | Waste management vocabulary | Diarize skill, onboarding |

## People

People names, variants, and roles are in the [diarize cheat sheet](../stakeholders/diarize-cheatsheet.md). That file covers name misspellings (Lana → Lannis), decision authority, and speaker resolution rules.

## How Diarize Uses This

The diarize skill loads `transcription-corrections.md` during step 1 (locate and load). When extracting quotes and generating the README, it applies corrections from the table — replacing mangled terms with canonical spellings in the output while preserving the original transcript file.
