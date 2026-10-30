from .text import Tfidf, cosine
from .geo import distance_m

RADIUS_M = 200  # only look at reports this close


def find_duplicate(new, others):
    """Return (root_report_id, confidence, reason) or None.

    Score = 50% text similarity (TF-IDF cosine) + 50% closeness in metres.
    Candidates must share the category and be within RADIUS_M.
    """
    cands = [o for o in others
             if o.category == new.category
             and distance_m(new.lat, new.lng, o.lat, o.lng) <= RADIUS_M]
    if not cands:
        return None
    tf = Tfidf([o.text for o in others] + [new.text])
    nv = tf.vec(new.text)
    best = None
    for o in cands:
        sim = cosine(nv, tf.vec(o.text))
        d = distance_m(new.lat, new.lng, o.lat, o.lng)
        score = 0.5 * sim + 0.5 * (1 - d / RADIUS_M)
        if sim >= 0.15 and score >= 0.5 and (best is None or score > best[0]):
            best = (score, o, sim, d)
    if not best:
        return None
    score, o, sim, d = best
    root = o.duplicate_of or o.id  # link to the first report of the group
    return root, round(score, 2), f"same category, {d:.0f} m apart, wording {sim:.0%} similar"