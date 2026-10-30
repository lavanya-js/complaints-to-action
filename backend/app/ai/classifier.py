import math
from collections import Counter, defaultdict

from .text import tokens
from ..seed_data import REPORTS

# Keyword rules: used only when the trained model is not confident.
KEYWORDS = {
    "Road Damage": ["pothole", "road", "manhole", "footpath", "crack", "speed breaker", "gravel", "caved"],
    "Drainage & Waterlogging": ["drain", "sewage", "waterlog", "flood", "stagnant", "overflow", "underpass", "water logged"],
    "Garbage & Waste": ["garbage", "waste", "bin", "trash", "smell", "dead animal", "burning"],
    "Streetlight": ["streetlight", "street light", "light", "lamp"],
    "Water Supply": ["tap", "supply", "pipe", "borewell", "pressure", "tanker", "drinking", "leak"],
    "Electrical Hazard": ["wire", "electric", "transformer", "spark", "pole", "meter box", "power line"],
}


class NaiveBayes:
    def fit(self, samples):
        self.class_docs = Counter()
        self.word_counts = defaultdict(Counter)
        self.totals = Counter()
        self.vocab = set()
        for text, label in samples:
            self.class_docs[label] += 1
            for w in tokens(text):
                self.word_counts[label][w] += 1
                self.totals[label] += 1
                self.vocab.add(w)

    def predict(self, text):
        n = sum(self.class_docs.values())
        v = len(self.vocab)
        toks = [w for w in tokens(text) if w in self.vocab]  # ignore unseen words
        scores = {}
        for c in self.class_docs:
            s = math.log(self.class_docs[c] / n)
            for w in toks:
                s += math.log((self.word_counts[c][w] + 1) / (self.totals[c] + v))
            scores[c] = s
        m = max(scores.values())
        exp = {c: math.exp(s - m) for c, s in scores.items()}
        z = sum(exp.values())
        probs = {c: e / z for c, e in exp.items()}
        best = max(probs, key=probs.get)
        return best, probs[best]


SAMPLES = [(t, c) for (t, c, *_rest) in REPORTS]
_model = NaiveBayes()
_model.fit(SAMPLES)


def rule_category(text):
    low = text.lower()
    hits = {c: sum(1 for k in kws if k in low) for c, kws in KEYWORDS.items()}
    best = max(hits, key=hits.get)
    return best, hits[best]


def classify(text):
    """Returns (category, confidence 0-1, source)."""
    best, conf = _model.predict(text)
    if conf >= 0.55:
        return best, round(conf, 2), "classifier"
    rule_cat, n_hits = rule_category(text)
    if n_hits > 0:
        return rule_cat, 0.5, "rules"
    return "Unclassified", round(conf, 2), "rules"  # honest: we could not tell


def loo_accuracy():
    """Leave-one-out accuracy of the classifier alone on the synthetic data."""
    correct = 0
    for i, (text, label) in enumerate(SAMPLES):
        m = NaiveBayes()
        m.fit(SAMPLES[:i] + SAMPLES[i + 1:])
        if m.predict(text)[0] == label:
            correct += 1
    return correct / len(SAMPLES)