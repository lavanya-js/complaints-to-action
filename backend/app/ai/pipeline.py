import json
from collections import Counter

from .. import models
from .classifier import classify
from .duplicates import find_duplicate
from .priority import compute_priority, hazard_hits
from .clusters import rebuild_clusters
from .geo import distance_m
import re


def summarize(text):
    """Extractive summary: the first sentence, trimmed."""
    t = " ".join(text.split())
    first = re.split(r"(?<=[.!?])\s+", t)[0]
    if len(first) > 140:
        first = first[:137].rsplit(" ", 1)[0] + "..."
    return first[:1].upper() + first[1:]


def recompute_all(db):
    """Clusters and priorities depend on ALL reports, so recompute everything."""
    reports = db.query(models.Report).all()
    rebuild_clusters(db, reports)
    groups = Counter((r.duplicate_of or r.id) for r in reports)
    for r in reports:
        neighbors = sum(1 for o in reports
                        if o.id != r.id and distance_m(r.lat, r.lng, o.lat, o.lng) <= 150)
        dup_count = groups[r.duplicate_of or r.id] - 1
        score, factors, expl = compute_priority(
            r.text, r.category, r.lat, r.lng, r.created_at, dup_count, neighbors)
        r.priority_score = score
        r.priority_factors = json.dumps(factors)
        r.priority_explanation = expl
    db.commit()


def process_report(db, r, use_ai_category, recompute=True):
    # 1. Categorise (only if the citizen did not pick a category)
    if use_ai_category:
        r.category, r.category_confidence, r.ai_source = classify(r.text)
    else:
        r.category_confidence, r.ai_source = 1.0, "user"

    # 2. Summarise + safety words
    strong, _mild = hazard_hits(r.text)
    r.summary = summarize(r.text) + (f" [Safety words: {', '.join(strong[:3])}]" if strong else "")

    # 3. Duplicate check against earlier, unresolved reports
    others = (db.query(models.Report)
              .filter(models.Report.id != r.id,
                      models.Report.created_at <= r.created_at,
                      models.Report.status != "Resolved").all())
    r.duplicate_of, r.duplicate_confidence, r.duplicate_reason = None, None, ""
    dup = find_duplicate(r, others)
    if dup:
        r.duplicate_of, r.duplicate_confidence, r.duplicate_reason = dup

    db.flush()
    # 4. Priority + clusters
    if recompute:
        recompute_all(db)