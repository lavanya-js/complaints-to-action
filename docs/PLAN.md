# Plan

## Stack
- Backend: Python + FastAPI + SQLite (SQLAlchemy)
- Frontend: plain HTML/JS (mobile-first) + Leaflet map, served by FastAPI
-AI (classical ML + rules, no LLM):
  - Category: TF-IDF + logistic regression (scikit-learn), keyword fallback
  - Summary: extractive (key sentence + hazard keywords)
  - Duplicates: TF-IDF cosine similarity + distance + same category
  - Priority: transparent weighted formula
  - Hotspots: DBSCAN on coordinates, grouped by category mix
  - Action brief: template built from top-priority reports

## Tables
- reports: id, tracking_code, text, category, summary, lat, lng, image_path,
  status, priority_score, priority_factors (JSON), priority_explanation,
  duplicate_of, duplicate_confidence, cluster_id, ai_source (llm|rules),
  created_at
- status_history: id, report_id, status, note, created_at
- assignments: id, report_id, team, assigned_at
- clusters: id, label, summary, center_lat, center_lng, report_count

## Status flow
Submitted -> Under Review -> Assigned -> In Progress -> Resolved

## Endpoints
- POST /api/reports             create + run AI pipeline
- GET  /api/reports             list (filters: status, category)
- GET  /api/track/{code}        citizen view + timeline
- POST /api/reports/{id}/assign
- POST /api/reports/{id}/status
- GET  /api/clusters
- GET  /api/brief               action brief for top priorities

## Priority formula (total 100)
- Safety hazard flag ........... 30
- Linked duplicate count ....... 20  (min(count,5)/5 x 20)
- Near school/hospital (mocked)  15
- Category severity ............ 15
- Days unresolved .............. 10  (min(days,14)/14 x 10)
- Area cluster density ......... 10
Explanation = factors sorted by points, written in plain language.

## Mocked (label in UI + README)
Notifications, login/auth, sensitive-site lookup, image analysis
(images stored only, not analyzed).

## Fallback
If the classifier is unsure (low confidence), keyword rules decide and the
UI shows "low confidence".