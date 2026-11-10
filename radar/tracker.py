# radar/tracker.py
"""Suivi de candidatures persistant via SQLite standard et export CSV."""

from __future__ import annotations
import csv
import io
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

VALID_STATUSES: List[str] = [
    "Non suivi",
    "À postuler",
    "Postulé",
    "Entretien",
    "Offre",
    "Refusé",
]

DEFAULT_DB_PATH = Path("radar_tracker.db")


def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    """Initialise la table SQLite de suivi si elle n'existe pas."""
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                program_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                notes TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def set_application_status(
    program_id: str,
    status: str,
    notes: str = "",
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    """Enregistre ou met à jour le statut et la note d'un programme (ou le supprime si 'Non suivi')."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Statut invalide : {status}. Valeurs autorisées : {VALID_STATUSES}")

    init_db(db_path)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(str(db_path)) as conn:
        if status == "Non suivi" and not notes.strip():
            conn.execute("DELETE FROM applications WHERE program_id = ?", (program_id,))
        else:
            conn.execute(
                """
                INSERT INTO applications (program_id, status, notes, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(program_id) DO UPDATE SET
                    status = excluded.status,
                    notes = excluded.notes,
                    updated_at = excluded.updated_at
                """,
                (program_id, status, notes.strip(), now_iso),
            )
        conn.commit()


def get_application(program_id: str, db_path: str | Path = DEFAULT_DB_PATH) -> Dict[str, str]:
    """Récupère le suivi pour un programme donné."""
    init_db(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        row = conn.execute(
            "SELECT program_id, status, notes, updated_at FROM applications WHERE program_id = ?",
            (program_id,),
        ).fetchone()
    if not row:
        return {"program_id": program_id, "status": "Non suivi", "notes": "", "updated_at": ""}
    return {
        "program_id": row[0],
        "status": row[1],
        "notes": row[2],
        "updated_at": row[3],
    }


def get_all_tracked(db_path: str | Path = DEFAULT_DB_PATH) -> Dict[str, Dict[str, str]]:
    """Retourne un dictionnaire {program_id: {status, notes, updated_at}} de toutes les entrées."""
    init_db(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        rows = conn.execute(
            "SELECT program_id, status, notes, updated_at FROM applications ORDER BY updated_at DESC"
        ).fetchall()
    return {
        r[0]: {"program_id": r[0], "status": r[1], "notes": r[2], "updated_at": r[3]}
        for r in rows
    }


def export_tracked_to_csv(programs: List[Any], db_path: str | Path = DEFAULT_DB_PATH) -> str:
    """Exporte les candidatures suivies (statut != 'Non suivi' ou note non vide) au format CSV."""
    tracked = get_all_tracked(db_path)
    prog_by_id = {str(getattr(p, "id", "")): p for p in programs}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["ID Programme", "Entreprise", "Programme", "Catégorie", "Villes", "Statut", "Notes", "Dernière MAJ", "Lien Officiel"]
    )

    for pid, data in tracked.items():
        if data["status"] == "Non suivi" and not data["notes"]:
            continue
        prog = prog_by_id.get(pid)
        firm = getattr(prog, "firm", "") if prog else ""
        title = getattr(prog, "program", "") if prog else ""
        category = getattr(prog, "category", "") if prog else ""
        locs = ", ".join(getattr(prog, "locations", []) or []) if prog else ""
        url = getattr(prog, "apply_url", "") if prog else ""

        writer.writerow([
            pid,
            firm,
            title,
            category,
            locs,
            data["status"],
            data["notes"],
            data["updated_at"],
            url,
        ])

    return output.getvalue()