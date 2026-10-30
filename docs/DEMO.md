# 5-minute demo script

Before starting: server running, `python seed.py` then `python process_all.py` done.

1. **Intro (30s):** Problem: duplicate, unprioritised complaints and no visibility for citizens.
2. **Capture (60s):** Open `/`. Enter `12.9381` / `77.6051`, write "Live wire sparking
   near school gate", category "Not sure", submit. Copy the tracking code.
3. **AI result (60s):** Read the green box: category and confidence, summary, duplicate
   note (linked to earlier wire reports), priority and the plain-language reason.
   Then submit "pls fix asap" to show the honest "Unclassified" case.
4. **Insight (60s):** Open `/dashboard.html`. Show the stat cards, the Lake View Road
   mixed hotspot (drain + road damage + garbage), and the action brief.
   Click "Why this priority?" to show the factor bars.
5. **Act (60s):** Untick "Merge duplicates", find the new report, assign it to
   Electrical Dept, set status In Progress with a note.
6. **Citizen view (30s):** Open `/track.html`, paste the code: progress bar and history.
7. **Honesty (30s):** Mention LIMITATIONS: synthetic data, mocked notifications and
   login, photos not analysed, classifier about 75% on its own training data.