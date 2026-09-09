# Computational Chemistry Report Assistant (CCRA)

Project-first Windows GUI for organizing Gaussian calculations, Google Drive/Sheets, extracted XYZ structures, raw energies, and later report-generation modules.

## Architecture priority
CCRA treats **Project → Module → Files/Data** as the primary hierarchy. Scientific analysis is attached to a project record instead of operating as a stand-alone parser.

Current configured projects:
- 1. Deformylation_UNIST
- 2. FeNO6_UNIST
- 4. CoNO7_UNIST
- 5. Co_sidearm
- 6. Mn(IV)-dichloride

Each project definition stores its current Google Drive folder ID, Google Sheet ID, and workbook tab schema derived from the current workbooks.

## Privacy boundary
This repository is public. It stores code, Drive/Sheet identifiers, and workbook **schema only**. It does not commit spreadsheet cell contents, Gaussian outputs, OAuth credentials, tokens, or private raw research data.

## Data model
Project → Google Drive folder / Google Sheet / modules / Gaussian files.
Imported outputs are indexed in `~/.ccra/research.db` with SHA256, normal termination, charge, multiplicity, method/basis, final electronic energy, and final-orientation XYZ. Original files are never modified.

## Run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
ccra
```

Google Drive/Sheets OAuth:
```bash
pip install -e .[google]
```
Place a Google Cloud OAuth Desktop-app `credentials.json` locally. `credentials.json` and `token.json` are git-ignored.

## v0.1 implemented
- project tree + project-specific modules
- links to each current Drive folder and Google Sheet
- current workbook tab schemas
- `.out/.log` multi-import + drag/drop
- background import thread
- SQLite storage and SHA-256 duplicate protection
- normal termination, charge, multiplicity, method/basis, job-type parsing
- final electronic energy extraction
- final Gaussian orientation → XYZ extraction
- reserved project tabs for Energy, Spin Density, Geometry, TD-DFT/Frequency, Future Work
- optional local OAuth adapter for Drive folder listing and Sheets reads

## Tests
```bash
pytest -q
```

## Windows executable
```bat
scripts\build_exe.bat
```

Do not call the full application complete until 10 real regression cycles pass. See `REGRESSION_LOG.md`.
