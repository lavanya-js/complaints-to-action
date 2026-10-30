from datetime import datetime

from .geo import distance_m

# Words that signal immediate danger / milder risk
STRONG = ["spark", "live wire", "exposed", "open manhole", "without cover", "submerged",
          "chest-deep", "fallen", "touching ground", "dangerously", "caved", "wading",
          "rising", "nearly crash", "dangerous"]
MILD = ["unsafe", "tripping", "skidding", "accident", "stuck", "mosquito",
        "falling", "unsafe to drink", "bumping"]
PEOPLE_WORDS = ["school", "hospital", "clinic", "children", "elderly"]

SEVERITY = {"Electrical Hazard": 15, "Drainage & Waterlogging": 11, "Road Damage": 9,
            "Water Supply": 8, "Garbage & Waste": 6, "Streetlight": 6, "Unclassified": 5}

# MOCKED lookup table of sensitive sites (not real map data)
SITES = [("Govt School", 12.9380, 77.6050), ("City Hospital", 12.9282, 77.6153),
         ("Primary School", 12.9500, 77.6352)]


def hazard_hits(text):
    low = text.lower()
    return [k for k in STRONG if k in low], [k for k in MILD if k in low]


def _f(name, points, mx, detail):
    return {"name": name, "points": round(points, 1), "max": mx, "detail": detail}


def compute_priority(text, category, lat, lng, created_at, dup_count, neighbor_count):
    strong, mild = hazard_hits(text)
    factors = []

    if strong:
        factors.append(_f("Safety hazard", 30, 30, "danger words: " + ", ".join(strong[:3])))
    elif mild:
        factors.append(_f("Safety hazard", 12, 30, "risk words: " + ", ".join(mild[:3])))
    else:
        factors.append(_f("Safety hazard", 0, 30, "no safety wording found"))

    factors.append(_f("Repeat reports", min(dup_count, 4) / 4 * 20, 20,
                      f"{dup_count} other report(s) about the same issue"))

    near = None
    for name, slat, slng in SITES:
        d = distance_m(lat, lng, slat, slng)
        if d <= 200 and (near is None or d < near[1]):
            near = (name, d)
    people = [w for w in PEOPLE_WORDS if w in text.lower()]
    if near:
        factors.append(_f("Sensitive place nearby", 15, 15,
                          f"{near[0]} about {near[1]:.0f} m away (mocked site data)"))
    elif people:
        factors.append(_f("Sensitive place nearby", 10, 15, "text mentions " + ", ".join(people[:2])))
    else:
        factors.append(_f("Sensitive place nearby", 0, 15, "none found"))

    sev = SEVERITY.get(category, 5)
    factors.append(_f("Category severity", sev, 15, category))

    days = max((datetime.utcnow() - created_at).total_seconds() / 86400, 0)
    factors.append(_f("Days unresolved", min(days, 14) / 14 * 10, 10, f"{days:.0f} day(s) old"))

    factors.append(_f("Area hotspot density", min(neighbor_count, 5) / 5 * 10, 10,
                      f"{neighbor_count} other report(s) within 150 m"))

    total = round(sum(f["points"] for f in factors))
    level = "Critical" if total >= 60 else "High" if total >= 45 else "Medium" if total >= 25 else "Low"
    top = sorted([f for f in factors if f["points"] > 0], key=lambda f: -f["points"])[:4]
    explanation = (f"{level} priority ({total}/100). " +
                   "; ".join(f"{f['name']} +{f['points']:g} ({f['detail']})" for f in top) + ".")
    return total, factors, explanation