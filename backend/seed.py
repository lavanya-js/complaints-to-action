import random
import string
from datetime import datetime, timedelta

from app.db import engine, SessionLocal, Base
from app import models
from app.seed_data import REPORTS

rng = random.Random(42)  # fixed seed so data is reproducible


def make_code():
    return "CTA-" + "".join(rng.choices(string.ascii_uppercase + string.digits, k=6))


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

db = SessionLocal()
now = datetime.utcnow()

for i, (text, cat, lat, lng, days) in enumerate(REPORTS):
    # a few reports already in progress so the workflow has something to show
    status = "Submitted"
    if i % 11 == 5:
        status = "Under Review"
    elif i % 13 == 7:
        status = "In Progress"

    created = now - timedelta(days=days, hours=rng.randint(0, 12))
    r = models.Report(
        tracking_code=make_code(), text=text, category=cat,
        lat=lat, lng=lng, status=status, created_at=created,
    )
    db.add(r)
    db.flush()
    db.add(models.StatusHistory(report_id=r.id, status="Submitted",
                                note="Report received", created_at=created))
    if status != "Submitted":
        db.add(models.StatusHistory(report_id=r.id, status=status,
                                    note="Updated by staff (seed data)",
                                    created_at=created + timedelta(hours=6)))

db.commit()
print(f"Seeded {db.query(models.Report).count()} reports (synthetic data)")
db.close()