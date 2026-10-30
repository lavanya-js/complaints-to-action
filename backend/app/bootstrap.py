import random
import string
from datetime import datetime, timedelta

from .db import SessionLocal
from . import models
from .seed_data import REPORTS
from .ai.pipeline import process_report, recompute_all


def seed_if_empty():
    """Load the synthetic demo data and run the AI over it if the DB has no reports."""
    db = SessionLocal()
    try:
        if db.query(models.Report).count() > 0:
            return
        rng = random.Random(42)
        now = datetime.utcnow()
        used = set()

        def make_code():
            while True:
                c = "CTA-" + "".join(rng.choices(string.ascii_uppercase + string.digits, k=6))
                if c not in used:
                    used.add(c)
                    return c

        for i, (text, cat, lat, lng, days) in enumerate(REPORTS):
            status = "Submitted"
            if i % 11 == 5:
                status = "Under Review"
            elif i % 13 == 7:
                status = "In Progress"
            created = now - timedelta(days=days, hours=rng.randint(0, 12))
            r = models.Report(tracking_code=make_code(), text=text, category=cat,
                              lat=lat, lng=lng, status=status, created_at=created)
            db.add(r)
            db.flush()
            db.add(models.StatusHistory(report_id=r.id, status="Submitted",
                                        note="Report received", created_at=created))
            if status != "Submitted":
                db.add(models.StatusHistory(report_id=r.id, status=status,
                                            note="Updated by staff (seed data)",
                                            created_at=created + timedelta(hours=6)))
        db.commit()

        reports = db.query(models.Report).order_by(models.Report.created_at).all()
        for r in reports:
            process_report(db, r, use_ai_category=False, recompute=False)
        recompute_all(db)
    finally:
        db.close()