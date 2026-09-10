# Computational Chemistry Report Assistant (CCRA)

Project-first Windows GUI and lightweight web tools for organizing Gaussian calculations, Google Drive/Sheets, reaction-coordinate figures, and Supporting Information data.

## Architecture priority
CCRA treats **Project → Module → Files/Data** as the primary hierarchy. Scientific analysis and report-generation data are attached to a project instead of operating as stand-alone utilities.

Current configured projects:
- 1. Deformylation_UNIST
- 2. FeNO6_UNIST
- 4. CoNO7_UNIST
- 5. Co_sidearm
- 6. Mn(IV)-dichloride

Each project definition stores its current Google Drive folder ID, Google Sheet ID, workbook tab schema, and module list.

## Privacy boundary
This repository is public. It stores code, Drive/Sheet identifiers, and workbook **schema only**. It does not commit spreadsheet cell contents, Gaussian outputs, OAuth credentials, tokens, SI documents, or private raw research data.

## Data model
Project → Google Drive folder / Google Sheet / modules / Gaussian files / Reaction Coordinate diagrams / SI documents.

Imported Gaussian outputs are indexed in `~/.ccra/research.db`. Reaction-coordinate diagrams are stored under `~/.ccra/reaction_diagrams/<project>/`. Local SI documents are stored under `~/.ccra/si_documents/<project>/`. Original calculation files are never modified.

## Run the local GUI
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
ccra
```

Google Drive/Sheets OAuth for the local GUI:
```bash
pip install -e .[google]
```
Place a Google Cloud OAuth Desktop-app `credentials.json` either in the current working directory or at `~/.ccra/credentials.json`. The generated token is kept at `~/.ccra/token.json` and is not committed.

## SI Generator
The SI Generator is available in two forms using the same project-first workflow.

### Web
Open:

`https://skylark51.github.io/forPostDoc/si-generator.html`

The web application is dependency-light: no React/Vue/jQuery and no large document library. The DOCX package is generated directly in the browser, and the Google Identity script is loaded only when Drive connection is requested.

Implemented SI tables are based on the supplied SI Generator document structure:
- Absolute Energy
- Relative Energy
- Mulliken Spin Density Distribution
- Selected Geometry

Web features:
- project and module binding
- multiple SI documents per project
- structure-row add/delete
- dynamic spin-density and geometry columns
- direct TSV paste from Excel / Google Sheets
- template-defined `ΔE Total = ΔE + ΔΔE` recalculation
- template-defined `ΔG` recalculation
- browser localStorage save
- JSON import/export
- real DOCX export
- copy current table as HTML + TSV for Word/Excel
- project Google Drive save/load

The deployed editor starts with **empty tables**. No example research values or dummy SI rows are bundled.

### Local GUI
Select a project and open the **SI Generator** tab. Local mode supports editable tables, project-scoped JSON persistence, DOCX export, relative-energy derived-column recalculation, and project Google Drive save/load.

Drive SI documents are stored as `CCRA-SI-<document-id>.json` in the project Drive folder. OAuth tokens and SI content remain outside this public repository.

### Browser Google Drive setup
The browser app asks for a Google OAuth Web Client ID. Add `https://skylark51.github.io` as an authorized JavaScript origin in the corresponding Google Cloud OAuth client. The Client ID is stored only in that browser's localStorage. The app requests Drive read access plus app-file write access when the user explicitly connects.

## Reaction Coordinate Editor
Select a project and open the **Reaction Coordinate** tab.

- direct canvas node / TS / edge creation
- drag, multi-select, duplicate, delete, Undo / Redo
- `chain`, `circular`, `branched`, `freeform` layouts
- alignment and distribution tools
- Gaussian raw-energy provenance links
- PNG / SVG / JSON / clipboard export

## Implemented foundation
- project tree + project-specific modules
- project Drive / Sheet bindings
- `.out/.log` multi-import + drag/drop
- SQLite storage and SHA-256 duplicate protection
- normal termination, charge, multiplicity, method/basis, job-type parsing
- final electronic energy extraction
- final Gaussian orientation → XYZ extraction
- Reaction Coordinate Editor
- SI Generator: web + local GUI
- project-scoped Google Drive SI synchronization

## Project catalog for GitHub Pages
The deployed web catalog is generated from the real project configs:
```bash
python scripts/build_project_catalog.py
```
This copies only `key`, `title`, `drive_folder_id`, and `modules` into `docs/project-catalog.json`.

## Tests
```bash
pytest -q
node --check docs/assets/si-docx.js
node --check docs/assets/si-generator.js
```
GitHub Actions runs the test suite on pull requests and pushes to `main`.

## Windows executable
```bat
scripts\build_exe.bat
```

Do not call the full application complete until 10 real regression cycles pass. See `REGRESSION_LOG.md`.
