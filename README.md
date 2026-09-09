# Computational Chemistry Report Assistant (CCRA)

Project-first Windows GUI for organizing Gaussian calculations, Google Drive/Sheets, extracted XYZ structures, raw energies, and report-generation modules.

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
Project → Google Drive folder / Google Sheet / modules / Gaussian files / Reaction Coordinate diagrams.
Imported outputs are indexed in `~/.ccra/research.db` with SHA256, normal termination, charge, multiplicity, method/basis, final electronic energy, and final-orientation XYZ. Original files are never modified.
Reaction-coordinate diagrams are stored locally under `~/.ccra/reaction_diagrams/<project>/` as editable JSON.

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

## Reaction Coordinate Editor
Select a project and open the **Reaction Coordinate** tab. The editor is designed around direct canvas manipulation rather than form-heavy input.

- double-click empty canvas: add an intermediate
- `노드` / `TS`: click empty canvas to add that item type
- `연결`: click source node, then target node
- drag nodes freely; optional grid snapping
- double-click a node to rename it
- multi-select by rubber-band; delete, duplicate, align, distribute
- Undo / Redo, zoom, fit-to-view
- layouts: `chain`, `circular`, `branched`, `freeform`
- templates: Linear, Circular, Branched, Rebound/Radical-coupling
- node properties: energy, unit, spin, multiplicity, subtitle, notes
- edge properties: normal/curved/dashed/reversible/no-arrow, label, barrier
- display toggles: energy, local barrier, spin/multiplicity, subtitle, arrows, curved connectors
- imported Gaussian files can be linked to a node with filename/file ID/raw electronic energy provenance
- export: PNG, SVG, JSON, clipboard image

The editor never modifies Gaussian output files. A manual relative energy can coexist with linked raw Gaussian energy; applying the raw `Eh` value is an explicit user action.

## Implemented foundation
- project tree + project-specific modules
- links to each current Drive folder and Google Sheet
- current workbook tab schemas
- `.out/.log` multi-import + drag/drop
- background import thread
- SQLite storage and SHA-256 duplicate protection
- normal termination, charge, multiplicity, method/basis, job-type parsing
- final electronic energy extraction
- final Gaussian orientation → XYZ extraction
- Reaction Coordinate Editor
- optional local OAuth adapter for Drive folder listing and Sheets reads

## Tests
```bash
pytest -q
```
GitHub Actions runs the test suite on pull requests and pushes to `main`.

## Windows executable
```bat
scripts\build_exe.bat
```

Do not call the full application complete until 10 real regression cycles pass. See `REGRESSION_LOG.md`.
