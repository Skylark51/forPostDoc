from __future__ import annotations
import sqlite3, json
from pathlib import Path
from .models import GaussianRecord

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS projects (
  project_key TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  drive_folder_id TEXT NOT NULL,
  spreadsheet_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS gaussian_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_key TEXT NOT NULL,
  filename TEXT NOT NULL,
  source_path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  normal_termination INTEGER NOT NULL,
  charge INTEGER,
  multiplicity INTEGER,
  method_basis TEXT,
  job_types_json TEXT NOT NULL,
  electronic_energy_hartree REAL,
  xyz TEXT,
  raw_metadata_json TEXT NOT NULL,
  imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_key, sha256),
  FOREIGN KEY(project_key) REFERENCES projects(project_key)
);
CREATE INDEX IF NOT EXISTS idx_gaussian_project ON gaussian_files(project_key);
CREATE INDEX IF NOT EXISTS idx_gaussian_filename ON gaussian_files(filename);
"""

class ResearchDatabase:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def upsert_project(self, project) -> None:
        self.conn.execute("""INSERT INTO projects(project_key,title,drive_folder_id,spreadsheet_id) VALUES(?,?,?,?) ON CONFLICT(project_key) DO UPDATE SET title=excluded.title, drive_folder_id=excluded.drive_folder_id, spreadsheet_id=excluded.spreadsheet_id""", (project.key, project.title, project.drive_folder_id, project.sheet.spreadsheet_id))
        self.conn.commit()

    def add_gaussian_record(self, record: GaussianRecord) -> tuple[bool, int]:
        cur = self.conn.execute("""INSERT OR IGNORE INTO gaussian_files(project_key,filename,source_path,sha256,normal_termination,charge,multiplicity,method_basis,job_types_json,electronic_energy_hartree,xyz,raw_metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", (record.project_key, record.filename, str(record.source_path), record.sha256, int(record.normal_termination), record.charge, record.multiplicity, record.method_basis, json.dumps(record.job_types, ensure_ascii=False), record.electronic_energy_hartree, record.xyz, json.dumps(record.raw_metadata, ensure_ascii=False)))
        self.conn.commit()
        if cur.rowcount:
            return True, int(cur.lastrowid)
        row = self.conn.execute("SELECT id FROM gaussian_files WHERE project_key=? AND sha256=?", (record.project_key, record.sha256)).fetchone()
        return False, int(row["id"])

    def list_gaussian_files(self, project_key: str):
        return self.conn.execute("SELECT id,filename,normal_termination,charge,multiplicity,method_basis,electronic_energy_hartree,imported_at FROM gaussian_files WHERE project_key=? ORDER BY id DESC", (project_key,)).fetchall()

    def get_xyz(self, file_id: int) -> str | None:
        row = self.conn.execute("SELECT xyz FROM gaussian_files WHERE id=?", (file_id,)).fetchone()
        return None if row is None else row["xyz"]
