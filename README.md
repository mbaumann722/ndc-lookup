# NDC Lookup & Validator

A small command-line tool that looks up National Drug Code (NDC) entries
against the public [openFDA NDC Directory](https://open.fda.gov/apis/drug/ndc/)
and flags whether a code is currently marketed, discontinued, or unrecognized —
the same basic question a claims processor asks before paying a pharmacy line item.

Built as a learning project: real problem shape, entirely public data
(openFDA + CMS's published HCPCS-to-NDC crosswalk format), no proprietary
logic or data from any employer.

## What it does

- **Single lookup** — `ndc-lookup check 0069-3060-04` returns product name,
  labeler, marketing category, and marketing start/end dates from openFDA.
- **Batch validation** — `ndc-lookup batch codes.csv` reads a column of NDC
  codes and writes a report: `ACTIVE`, `DISCONTINUED` (has an end date in the
  past), or `NOT_FOUND` (not in the FDA directory at all — often a format or
  typo issue).
- **HCPCS crosswalk match** — optionally cross-references a local CSV shaped
  like CMS's quarterly crosswalk file, to flag codes that are valid NDCs but
  have no corresponding billable HCPCS code.

## Why this lives on GitHub

This project doubles as a working example of what GitHub actually buys you
over a folder of scripts:

| Need | GitHub feature | Where |
|---|---|---|
| "What changed and why" history | Commits | `git log` |
| Try a risky change safely | Branches | e.g. `feature/fuzzy-matching` |
| Track known bugs / planned work | Issues | repo Issues tab |
| Auto-run tests on every push | Actions | `.github/workflows/ci.yml` |
| See the whole roadmap at a glance | Projects | repo Projects tab |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python -m ndc_lookup check 0069-3060-04
python -m ndc_lookup batch data/sample_codes.csv
```

## Running tests

```bash
pytest
```

## Data sources

- openFDA NDC Directory API — https://api.fda.gov/drug/ndc.json (no API key
  required for light use; a free key raises the rate limit)
- CMS HCPCS-to-NDC crosswalk — published quarterly at cms.gov; this repo
  ships a small hand-built sample in `data/sample_crosswalk.csv` shaped like
  the real file, not the real file itself
