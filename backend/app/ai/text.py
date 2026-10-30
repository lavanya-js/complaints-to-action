import math
import re
from collections import Counter

STOP = set("""a an the is are was were be been to of in on at for and or but with
near by from it its this that there here since very so as i we our my please pls""".split())

# Tiny synonym map so "streetlight" matches "street light", "Rd" matches "road", etc.
SYN = {"streetlight": "street light", "dustbin": "bin", "garbage": "waste",
       "trash": "waste", "rd": "road"}


def stem(w):
    """Very small stemmer: strip -ing, -ed, -s (not -ss)."""
    for suf in ("ing", "ed", "s"):
        if w.endswith(suf) and not w.endswith("ss") and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def tokens(text):
    out = []
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        for part in SYN.get(w, w).split():
            if part not in STOP:
                out.append(stem(part))
    return out


class Tfidf:
    """TF-IDF vectors built from a list of documents (written by hand, no libraries)."""

    def __init__(self, docs):
        self.n = len(docs)
        df = Counter()
        for d in docs:
            df.update(set(tokens(d)))
        self.idf = {w: math.log((1 + self.n) / (1 + c)) + 1 for w, c in df.items()}

    def vec(self, text):
        tf = Counter(tokens(text))
        default_idf = math.log(1 + self.n) + 1
        v = {w: c * self.idf.get(w, default_idf) for w, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {w: x / norm for w, x in v.items()}


def cosine(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(w, 0.0) for w, x in a.items())