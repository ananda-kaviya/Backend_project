import sqlite3
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

DB_FILE = "registrations.db"
CAPACITY = 50

app = FastAPI(title="Backend Development Workshop - Registration API")


# ---------- Database ----------
def get_conn():
    # isolation_level=None -> we control transactions manually
    conn = sqlite3.connect(DB_FILE, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            college_department TEXT,
            registered_at TEXT NOT NULL
        )
    """)
    conn.close()


init_db()


# ---------- Input validation ----------
class RegistrationIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    college_department: Optional[str] = Field(default=None, max_length=150)


# ---------- Routes ----------
@app.get("/")
def home():
    return {"event": "Backend Development Workshop", "date": "20 October 2026",
            "capacity": CAPACITY, "docs": "/docs"}


@app.post("/register", status_code=201)
def register(data: RegistrationIn):
    conn = get_conn()
    try:
        # BEGIN IMMEDIATE locks the DB so two people can't grab the last seat at once
        conn.execute("BEGIN IMMEDIATE")

        count = conn.execute("SELECT COUNT(*) FROM registrations").fetchone()[0]
        if count >= CAPACITY:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=409, detail="Event is full")

        try:
            cur = conn.execute(
                "INSERT INTO registrations (name, email, college_department, registered_at) "
                "VALUES (?, ?, ?, ?)",
                (
                    data.name.strip(),
                    data.email.lower(),
                    data.college_department,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        except sqlite3.IntegrityError:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=409, detail="This email is already registered")

        conn.execute("COMMIT")
        return {
            "message": "Registration successful",
            "id": cur.lastrowid,
            "seats_filled": f"{count + 1} / {CAPACITY}",
        }
    finally:
        conn.close()


@app.get("/registrations")
def list_registrations():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM registrations ORDER BY id").fetchall()
    conn.close()
    return {
        "seats_filled": f"{len(rows)} / {CAPACITY}",
        "registrations": [dict(r) for r in rows],
    }


@app.get("/registrations/{reg_id}")
def get_registration(reg_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM registrations WHERE id = ?", (reg_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    return dict(row)
