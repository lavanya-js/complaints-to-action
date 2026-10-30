from app.db import SessionLocal
from app import models
from app.ai.pipeline import process_report, recompute_all
from app.ai.classifier import loo_accuracy

db = SessionLocal()
reports = db.query(models.Report).order_by(models.Report.created_at).all()
for r in reports:
    process_report(db, r, use_ai_category=False, recompute=False)
recompute_all(db)

reports = db.query(models.Report).all()
print("Reports processed:", len(reports))
print("Linked as duplicates:", sum(1 for r in reports if r.duplicate_of))
print("Hotspots found:", db.query(models.Cluster).count())
for c in db.query(models.Cluster).all():
    print("  -", c.label, "|", c.report_count, "reports")
print("\nTop 5 by priority:")
for r in sorted(reports, key=lambda r: -r.priority_score)[:5]:
    print(f"  #{r.id} [{r.priority_score:.0f}] {r.text[:60]}")
    print("     ", r.priority_explanation)
print(f"\nClassifier leave-one-out accuracy on synthetic data: {loo_accuracy():.0%}")
db.close()