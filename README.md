# From Complaints to Action

An AI-assisted platform that turns scattered citizen reports (waterlogging,
potholes, garbage, broken streetlights, electrical hazards) into prioritized,
explainable, trackable action. Built solo for PromptWars x ASTRA.

## What it does (the four stages)

1. **Capture** - mobile-friendly form: text, optional photo, category (or "not sure"),
   map pin / coordinates / device location.
2. **Understand** - category, summary, duplicate check and priority score, each with a reason.
3. **Reveal** - dashboard with a priority-coloured map, hotspot circles, ranked list
   with a "Why this priority?" breakdown, and an action brief.
4. **Act** - staff assign reports and change status; citizens follow progress with a
   tracking code (no login).

## Run it locally (Windows)

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python process_all.py
uvicorn app.main:app
```

Then open:
- http://127.0.0.1:8000/ - report a problem
- http://127.0.0.1:8000/dashboard.html - decision dashboard
- http://127.0.0.1:8000/track.html - citizen tracking

`seed.py` wipes the database and loads 48 synthetic reports. `process_all.py` runs the
AI pipeline over them. Leaflet is bundled in `frontend/vendor`; street-map tiles
need internet access (the app still works without them, with a plain background).

## Architecture

- **Backend:** Python, FastAPI, SQLite (SQLAlchemy).
- **Frontend:** plain HTML/JS served by FastAPI, Leaflet for maps.
- **AI:** pure Python, no LLM and no external API (see below).

```
backend/app/main.py        API + static file serving
backend/app/models.py      tables: reports, status_history, assignments, clusters
backend/app/ai/            text.py (TF-IDF), classifier.py, duplicates.py,
                           priority.py, clusters.py, pipeline.py
backend/seed.py            synthetic data loader
backend/process_all.py     runs the AI over the seeded data
frontend/                  index.html, dashboard.html, track.html
```

## The AI approach

All components are classical methods written by hand, so every decision can be explained.

- **Categorisation:** Naive Bayes over word counts, trained on the synthetic reports.
  If confidence is below 55% it falls back to keyword rules; if those find nothing,
  the report is marked "Unclassified" instead of guessing. Citizen-chosen categories
  are kept as chosen.
- **Summary:** extractive (first sentence, trimmed) plus detected safety words.
- **Duplicate detection:** candidates must share the category and be within 200 m.
  Score = 50% TF-IDF cosine similarity of the text + 50% closeness. Linked reports
  show the score and reason. Duplicates are merged in counts and share status updates.
- **Priority (0-100):** a transparent weighted formula, not a black box: safety
  wording (30), repeat reports (20), sensitive place nearby (15, mocked site table),
  category severity (15), days unresolved (10), hotspot density (10). The
  explanation lists the biggest factors in plain language.
- **Hotspots:** DBSCAN density clustering (150 m, at least 3 reports), described as
  recurring (one category) or mixed (several categories in one spot).
- **Action brief:** a template filled from the top-priority reports (not an LLM).

## Honesty

See [LIMITATIONS.md](LIMITATIONS.md) for what is real, what is mocked, and where the AI can be wrong.