from collections import Counter, defaultdict

from .geo import distance_m
from .. import models

EPS_M = 150     # reports closer than this are neighbours
MIN_PTS = 3     # at least this many reports make a hotspot


def dbscan(points, eps_m=EPS_M, min_pts=MIN_PTS):
    """DBSCAN density clustering written by hand. Returns a label per point (-1 = noise)."""
    n = len(points)
    labels = [None] * n

    def nbrs(i):
        return [j for j in range(n) if distance_m(*points[i], *points[j]) <= eps_m]

    cid = 0
    for i in range(n):
        if labels[i] is not None:
            continue
        nb = nbrs(i)
        if len(nb) < min_pts:
            labels[i] = -1
            continue
        labels[i] = cid
        queue = [j for j in nb if j != i]
        while queue:
            j = queue.pop()
            if labels[j] == -1:
                labels[j] = cid
            if labels[j] is not None:
                continue
            labels[j] = cid
            nb2 = nbrs(j)
            if len(nb2) >= min_pts:
                queue.extend(nb2)
        cid += 1
    return labels


def rebuild_clusters(db, reports):
    db.query(models.Cluster).delete()
    for r in reports:
        r.cluster_id = None
    labels = dbscan([(r.lat, r.lng) for r in reports])
    groups = defaultdict(list)
    for r, lab in zip(reports, labels):
        if lab >= 0:
            groups[lab].append(r)
    for members in groups.values():
        cats = Counter(m.category for m in members)
        mixed = len(cats) > 1
        parts = ", ".join(f"{n} {c}" for c, n in cats.most_common())
        summary = f"{len(members)} reports within about {EPS_M} m: {parts}."
        if mixed:
            summary += (" Different problem types in one spot may share a root cause "
                        "(for example a blocked drain causing waterlogging and road damage).")
        label = ("Mixed hotspot: " if mixed else "Recurring problem: ") + ", ".join(cats)
        c = models.Cluster(
            label=label, summary=summary, report_count=len(members),
            center_lat=sum(m.lat for m in members) / len(members),
            center_lng=sum(m.lng for m in members) / len(members))
        db.add(c)
        db.flush()
        for m in members:
            m.cluster_id = c.id