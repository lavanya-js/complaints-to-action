import random
import string
import shutil
from pathlib import Path

from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import engine, SessionLocal, Base
from . import models
from .ai.pipeline import process_report

ROOT = Path(__file__).resolve().parents[2]
UPLOADS = ROOT / "data" / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)

CATEGORIES = [
    "Road Damage", "Drainage & Waterlogging", "Garbage & Waste",
    "Streetlight", "Water Supply", "Electrical Hazard",
]

Base.metadata.create_all(engine)

from .bootstrap import seed_if_empty
seed_if_empty()
app = FastAPI(title="From Complaints to Action")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def new_tracking_code(db: Session) -> str:
    while True:
        code = "CTA-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not db.query(models.Report).filter_by(tracking_code=code).first():
            return code


def dup_note(r):
    if r.duplicate_of:
        return (f"Likely duplicate of report #{r.duplicate_of} "
                f"(confidence {r.duplicate_confidence:.0%}): {r.duplicate_reason}")
    return "No likely duplicate found nearby."


@app.get("/api/categories")
def categories():
    return CATEGORIES


@app.post("/api/reports")
def create_report(
    text: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    category: str = Form("auto"),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    text = text.strip()
    if len(text) < 5:
        raise HTTPException(400, "Please describe the problem (at least 5 characters).")
        if len(text) > 2000:
            raise HTTPException(400, "Description is too long (max 2000 characters).")
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise HTTPException(400, "Invalid location.")

    code = new_tracking_code(db)

    image_path = None
    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise HTTPException(400, "Image must be jpg, png or webp.")
        fname = f"{code}{ext}"
        data = image.file.read()
        if len(data) > 5_000_000:
            raise HTTPException(400, "Image is too large (max 5 MB).")
        with open(UPLOADS / fname, "wb") as f:
            f.write(data)
        image_path = f"/uploads/{fname}"  # stored only, NOT analysed by the AI

    use_ai = category not in CATEGORIES
    report = models.Report(
        tracking_code=code, text=text, lat=lat, lng=lng, image_path=image_path,
        category="Unclassified" if use_ai else category,
    )
    db.add(report)
    db.flush()
    db.add(models.StatusHistory(report_id=report.id, status="Submitted", note="Report received"))
    process_report(db, report, use_ai_category=use_ai)
    db.refresh(report)

    return {
        "id": report.id, "tracking_code": code, "category": report.category,
        "category_confidence": report.category_confidence, "ai_source": report.ai_source,
        "summary": report.summary, "duplicate_note": dup_note(report),
        "priority_score": report.priority_score,
        "priority_explanation": report.priority_explanation,
    }


@app.get("/api/reports")
def list_reports(db: Session = Depends(get_db)):
    rows = db.query(models.Report).order_by(models.Report.priority_score.desc()).all()
    return [
        {
            "id": r.id, "tracking_code": r.tracking_code, "text": r.text,
            "summary": r.summary, "category": r.category, "ai_source": r.ai_source,
            "category_confidence": r.category_confidence,
            "lat": r.lat, "lng": r.lng, "status": r.status,
            "priority_score": r.priority_score,
            "priority_explanation": r.priority_explanation,
            "duplicate_of": r.duplicate_of, "duplicate_note": dup_note(r),
            "cluster_id": r.cluster_id, "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


import json
from collections import Counter

ACTIONS = {
    "Electrical Hazard": "Send an electrical crew now; keep people away until it is made safe.",
    "Drainage & Waterlogging": "Dispatch a drain-clearing or pumping team.",
    "Road Damage": "Put up barricades, then schedule the repair.",
    "Water Supply": "Check the line and arrange tanker supply if needed.",
    "Garbage & Waste": "Schedule an extra collection run.",
    "Streetlight": "Add to the next lighting repair round.",
}


@app.get("/api/clusters")
def list_clusters(db: Session = Depends(get_db)):
    return [{"id": c.id, "label": c.label, "summary": c.summary,
             "report_count": c.report_count, "lat": c.center_lat, "lng": c.center_lng}
            for c in db.query(models.Cluster).all()]


@app.get("/api/reports/{rid}")
def report_detail(rid: int, db: Session = Depends(get_db)):
    r = db.get(models.Report, rid)
    if not r:
        raise HTTPException(404, "Report not found")
    return {"id": r.id, "factors": json.loads(r.priority_factors or "[]"),
            "explanation": r.priority_explanation, "duplicate_note": dup_note(r),
            "image_path": r.image_path}


@app.get("/api/brief")
def action_brief(db: Session = Depends(get_db)):
    reports = db.query(models.Report).all()
    open_r = [r for r in reports if r.status != "Resolved"]
    unique = [r for r in open_r if not r.duplicate_of]
    dups = Counter(r.duplicate_of for r in open_r if r.duplicate_of)
    critical = [r for r in unique if r.priority_score >= 60]
    top = sorted(unique, key=lambda r: -r.priority_score)[:5]
    clusters = (db.query(models.Cluster)
                .order_by(models.Cluster.report_count.desc()).limit(3).all())
    return {
        "headline": (f"{len(open_r)} open reports are {len(unique)} separate issues after "
                     f"merging duplicates. {len(critical)} need urgent action."),
        "method": "Template-based brief built from the priority scores (no LLM).",
        "items": [{"id": r.id, "summary": r.summary, "why": r.priority_explanation,
                   "action": ACTIONS.get(r.category, "Review and assign."),
                   "duplicates": dups.get(r.id, 0), "score": r.priority_score}
                  for r in top],
        "hotspots": [{"label": c.label, "summary": c.summary} for c in clusters],
    }


# Serve uploaded images and the frontend (must come after the API routes)

from pydantic import BaseModel

STATUSES = ["Submitted", "Under Review", "Assigned", "In Progress", "Resolved"]
TEAMS = ["Electrical Dept", "Roads & Potholes Team", "Drainage & Sewerage Team",
         "Water Board", "Sanitation Team", "Street Lighting Team"]


class AssignIn(BaseModel):
    team: str
    note: str = ""


class StatusIn(BaseModel):
    status: str
    note: str = ""


def _apply(db: Session, r, status: str, note: str):
    """Update a report and every report merged into it, so all citizens see progress."""
    targets = [r]
    if not r.duplicate_of:
        targets += db.query(models.Report).filter(models.Report.duplicate_of == r.id).all()
    for t in targets:
        t.status = status
        extra = "" if t.id == r.id else " (updated together with the main report for this issue)"
        db.add(models.StatusHistory(report_id=t.id, status=status, note=(note + extra).strip()))


@app.get("/api/teams")
def list_teams():
    return TEAMS


@app.post("/api/reports/{rid}/assign")
def assign_report(rid: int, body: AssignIn, db: Session = Depends(get_db)):
    r = db.get(models.Report, rid)
    if not r:
        raise HTTPException(404, "Report not found")
    if body.team not in TEAMS:
        raise HTTPException(400, "Unknown team")
    db.add(models.Assignment(report_id=rid, team=body.team))
    _apply(db, r, "Assigned", f"Assigned to {body.team}. {body.note}")
    db.commit()
    return {"ok": True, "status": r.status}


@app.post("/api/reports/{rid}/status")
def change_status(rid: int, body: StatusIn, db: Session = Depends(get_db)):
    r = db.get(models.Report, rid)
    if not r:
        raise HTTPException(404, "Report not found")
    if body.status not in STATUSES:
        raise HTTPException(400, "Unknown status")
    _apply(db, r, body.status, body.note or f"Status changed to {body.status}")
    db.commit()
    return {"ok": True, "status": r.status}


@app.get("/api/track/{code}")
def track(code: str, db: Session = Depends(get_db)):
    r = db.query(models.Report).filter_by(tracking_code=code.strip().upper()).first()
    if not r:
        raise HTTPException(404, "No report found with that code.")
    hist = (db.query(models.StatusHistory).filter_by(report_id=r.id)
            .order_by(models.StatusHistory.created_at, models.StatusHistory.id).all())
    asg = (db.query(models.Assignment).filter_by(report_id=r.id)
           .order_by(models.Assignment.id.desc()).first())
    return {
        "tracking_code": r.tracking_code, "status": r.status, "category": r.category,
        "summary": r.summary, "submitted": r.created_at.isoformat(),
        "team": asg.team if asg else None, "statuses": STATUSES,
        "timeline": [{"status": h.status, "note": h.note, "at": h.created_at.isoformat()} for h in hist],
    }

app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")
app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")