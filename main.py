"""
AssetTrack API — IT Asset Management System
Built by Chantel Hlongwane | Portfolio Project
Stack: Python 3.11+, FastAPI, SQLite (via SQLAlchemy)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
import sqlite3, os, uuid

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="AssetTrack API",
    description="IT Asset Management REST API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "assettrack.db"

# ─────────────────────────────────────────────
# Database initialisation
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                category    TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT 'active',
                department  TEXT,
                assigned_to TEXT,
                serial_num  TEXT,
                purchase_date TEXT,
                notes       TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
    print("✅ Database initialised.")

# ─────────────────────────────────────────────
# Pydantic schemas
# ─────────────────────────────────────────────
class AssetCreate(BaseModel):
    name: str
    category: str
    status: Optional[str] = "active"
    department: Optional[str] = None
    assigned_to: Optional[str] = None
    serial_num: Optional[str] = None
    purchase_date: Optional[str] = None
    notes: Optional[str] = None

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    department: Optional[str] = None
    assigned_to: Optional[str] = None
    serial_num: Optional[str] = None
    purchase_date: Optional[str] = None
    notes: Optional[str] = None

class Asset(AssetCreate):
    id: str
    created_at: str

# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────
VALID_STATUSES = {"active", "allocated", "maintenance", "decommissioned"}
VALID_CATEGORIES = {"Laptop", "Desktop", "Server", "Networking", "Peripheral", "Mobile"}

def row_to_dict(row) -> dict:
    return dict(row)

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "AssetTrack API", "version": "1.0.0"}


@app.get("/assets", response_model=List[dict], tags=["Assets"])
def list_assets(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name, dept, or serial"),
):
    """Retrieve all assets with optional filtering."""
    query = "SELECT * FROM assets WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if category:
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (name LIKE ? OR department LIKE ? OR serial_num LIKE ?)"
        params += [f"%{search}%"] * 3

    query += " ORDER BY created_at DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [row_to_dict(r) for r in rows]


@app.post("/assets", response_model=dict, status_code=201, tags=["Assets"])
def create_asset(asset: AssetCreate):
    """Register a new IT asset."""
    if asset.status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status. Must be one of: {VALID_STATUSES}")

    asset_id = "AST-" + str(uuid.uuid4())[:8].upper()

    with get_db() as conn:
        conn.execute("""
            INSERT INTO assets (id, name, category, status, department,
                                assigned_to, serial_num, purchase_date, notes)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            asset_id, asset.name, asset.category, asset.status,
            asset.department, asset.assigned_to, asset.serial_num,
            asset.purchase_date, asset.notes
        ))
        conn.commit()
        row = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()

    return row_to_dict(row)


@app.get("/assets/{asset_id}", response_model=dict, tags=["Assets"])
def get_asset(asset_id: str):
    """Get a single asset by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Asset '{asset_id}' not found.")
    return row_to_dict(row)


@app.patch("/assets/{asset_id}", response_model=dict, tags=["Assets"])
def update_asset(asset_id: str, updates: AssetUpdate):
    """Partially update an asset."""
    with get_db() as conn:
        existing = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
        if not existing:
            raise HTTPException(404, f"Asset '{asset_id}' not found.")

        fields = updates.dict(exclude_none=True)
        if not fields:
            raise HTTPException(400, "No update fields provided.")
        if "status" in fields and fields["status"] not in VALID_STATUSES:
            raise HTTPException(400, f"Invalid status. Must be one of: {VALID_STATUSES}")

        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [asset_id]
        conn.execute(f"UPDATE assets SET {set_clause} WHERE id=?", values)
        conn.commit()
        row = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()

    return row_to_dict(row)


@app.delete("/assets/{asset_id}", status_code=204, tags=["Assets"])
def delete_asset(asset_id: str):
    """Delete an asset by ID."""
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM assets WHERE id=?", (asset_id,)).fetchone()
        if not existing:
            raise HTTPException(404, f"Asset '{asset_id}' not found.")
        conn.execute("DELETE FROM assets WHERE id=?", (asset_id,))
        conn.commit()
    return


@app.get("/stats", tags=["Analytics"])
def get_stats():
    """Get asset statistics summary."""
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        by_status = conn.execute(
            "SELECT status, COUNT(*) as count FROM assets GROUP BY status"
        ).fetchall()
        by_category = conn.execute(
            "SELECT category, COUNT(*) as count FROM assets GROUP BY category"
        ).fetchall()

    return {
        "total": total,
        "by_status": {r["status"]: r["count"] for r in by_status},
        "by_category": {r["category"]: r["count"] for r in by_category},
    }


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
