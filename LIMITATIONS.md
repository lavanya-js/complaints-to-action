# Limitations and Honesty Note

## What is real
- Report capture, SQLite storage, tracking codes, status history, assignment, and the
  citizen tracking page all work end to end.
- The AI pipeline really runs on every new report: Naive Bayes categorisation,
  TF-IDF duplicate detection, a weighted priority formula, and DBSCAN hotspots.
- Hotspots and priorities are recomputed across all reports whenever a report is added.

## What is mocked or simplified
- **Data:** all 48 seeded reports are synthetic, around fictional coordinates. No real personal data.
- **Sensitive places** (schools, hospital) are a small hard-coded lookup table, not real map data.
- **Login / roles:** none. Anyone who opens the dashboard can act as staff.
- **Notifications:** no SMS or email is sent. Citizens must check the tracking page.
- **Photos:** stored and shown, but **not analysed** by any AI.
- **Not deployed:** runs locally; no live integrations of any kind.

## Where the AI can be wrong
- The classifier was trained on the same small synthetic set it was tested on
  (leave-one-out accuracy about 75%). Real-world accuracy would likely be lower,
  especially for vague, misspelled or non-English reports. Vague reports such as
  "pls fix asap" are marked Unclassified on purpose.
- Duplicate thresholds (200 m, score of 0.5) were tuned by hand on the synthetic data.
  They can merge distinct problems on the same street or miss paraphrased duplicates.
  Precision and recall were not measured.
- Safety detection is keyword based. A hazard written without those words scores low,
  and an innocent use of a word can score high.
- The "Why this priority?" explanation shows the formula's inputs; it is not
  evidence that the weights are right. The weights are my own judgement.
- Mixed hotspots suggest a possible shared cause but do not prove one.

## What I would do next
- Collect real labelled reports to measure accuracy, precision and recall.
- Use multilingual embeddings or an LLM for classification and summaries, keeping the
  transparent priority formula.
- Analyse photos, add real authentication, SMS/email notifications and
  multilingual support.
- Use real map data for sensitive places and street names for hotspot labels.