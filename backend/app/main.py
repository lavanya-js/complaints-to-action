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
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise HTTPException(400, "Invalid location.")

    code = new_tracking_code(db)

    image_path = None
    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise HTTPException(400, "Image must be jpg, png or webp.")
        fname = f"{code}{ext}"
        with open(UPLOADS / fname, "wb") as f:
            shutil.copyfileobj(image.file, f)
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


# Serve uploaded images and the frontend (must come after the API routes)
app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")
app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")