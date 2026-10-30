# (text, true_category, lat, lng, days_ago)
# SYNTHETIC data. Coordinates are fictional points around 12.93, 77.62.
# Includes: a cluster (Lake View Road), duplicate groups, urgent hazards,
# and deliberately messy/vague reports.
REPORTS = [
    # --- Cluster: Lake View Road (drain + waterlogging + road damage)
    ("Drain near Lake View Road is blocked, dirty water overflowing onto the street", "Drainage & Waterlogging", 12.9352, 77.6245, 6),
    ("Water logged knee deep on Lake View Road after last night's rain, vehicles stuck", "Drainage & Waterlogging", 12.9354, 77.6247, 5),
    ("Stagnant water on lake view road for 3 days, mosquitoes breeding", "Drainage & Waterlogging", 12.9351, 77.6243, 4),
    ("Big potholes on Lake View Road near the bus stop, bikes skidding", "Road Damage", 12.9355, 77.6249, 7),
    ("Road caved in beside blocked drain at Lake View Road", "Road Damage", 12.9353, 77.6246, 3),
    ("Garbage dumped next to the drain at Lake View Road, blocking water flow", "Garbage & Waste", 12.9350, 77.6244, 2),
    # --- Duplicate group A: streetlight 5th Main
    ("Streetlight not working on 5th Main, whole stretch is dark at night", "Streetlight", 12.9330, 77.6190, 8),
    ("5th Main road street light is off since a week, women feel unsafe walking", "Streetlight", 12.9331, 77.6192, 6),
    ("lights out on 5th main near the park gate", "Streetlight", 12.9329, 77.6191, 5),
    # --- Duplicate group B: Market Circle garbage
    ("Garbage bin overflowing at Market Circle, waste spilling onto the road", "Garbage & Waste", 12.9400, 77.6300, 4),
    ("Market circle dustbin full for days, foul smell and stray dogs", "Garbage & Waste", 12.9402, 77.6301, 3),
    # --- Duplicate group C: Station Road pothole
    ("Deep pothole on Station Road opposite the pharmacy", "Road Damage", 12.9280, 77.6150, 9),
    ("Huge pothole station road near medical shop, two wheelers falling", "Road Damage", 12.9281, 77.6152, 7),
    ("Station Rd pothole getting bigger, someone nearly crashed", "Road Damage", 12.9279, 77.6149, 2),
    # --- Duplicate group D: water supply Block C
    ("No water supply in Block C apartments since yesterday morning", "Water Supply", 12.9450, 77.6100, 2),
    ("Block C no tap water for 30 hours, tanker needed", "Water Supply", 12.9451, 77.6102, 1),
    # --- Duplicate group E (URGENT): flooded underpass
    ("Railway underpass completely flooded, cars submerged and water rising near school bus route", "Drainage & Waterlogging", 12.9500, 77.6350, 1),
    ("Underpass near the railway gate is flooded, people wading through chest-deep water", "Drainage & Waterlogging", 12.9501, 77.6352, 1),
    # --- Duplicate group F (URGENT): live wire near school
    ("Electric wire hanging low and sparking near Govt School gate, children pass here", "Electrical Hazard", 12.9380, 77.6050, 0),
    ("Live wire fallen on footpath near government school, sparks seen", "Electrical Hazard", 12.9381, 77.6051, 0),
    # --- Urgent standalone
    ("Open manhole without cover on Temple Street, very dangerous for children and cyclists", "Road Damage", 12.9300, 77.6220, 1),
    ("Transformer box door open with exposed wires near bus stop", "Electrical Hazard", 12.9420, 77.6250, 2),
    ("Electric pole leaning dangerously after storm near the bakery", "Electrical Hazard", 12.9390, 77.6330, 1),
    ("Tree branch fell on power line, wires touching ground", "Electrical Hazard", 12.9440, 77.6130, 0),
    # --- Standalone routine
    ("Streetlight flickering near the community hall", "Streetlight", 12.9360, 77.6120, 10),
    ("Garbage not collected in Sector 4 for 5 days", "Garbage & Waste", 12.9250, 77.6320, 5),
    ("Burning of plastic waste on empty plot near Ring Road", "Garbage & Waste", 12.9220, 77.6400, 3),
    ("Low water pressure in morning hours in Lakshmi Layout", "Water Supply", 12.9150, 77.6280, 6),
    ("Water pipe leaking on the road near the temple, water wasted all day", "Water Supply", 12.9310, 77.6230, 4),
    ("Drain cover broken on Park Street, someone's foot got stuck", "Drainage & Waterlogging", 12.9270, 77.6090, 3),
    ("Sewage overflowing at corner of 2nd Cross", "Drainage & Waterlogging", 12.9190, 77.6210, 5),
    ("Cracked footpath tiles near the metro station, elderly people tripping", "Road Damage", 12.9410, 77.6180, 12),
    ("Road resurfacing left half done on Ring Road service lane, loose gravel everywhere", "Road Damage", 12.9240, 77.6420, 8),
    ("Speed breaker paint faded, no visibility at night", "Road Damage", 12.9340, 77.6280, 11),
    ("Two streetlights broken in the playground lane", "Streetlight", 12.9470, 77.6200, 9),
    ("Meter box sparking at night in our lane", "Electrical Hazard", 12.9205, 77.6160, 2),
    ("Muddy brown water coming from taps, unsafe to drink", "Water Supply", 12.9480, 77.6260, 3),
    ("Garbage truck skipped our street again", "Garbage & Waste", 12.9455, 77.6215, 2),
    ("Waterlogging near bus depot every time it rains, drains too small", "Drainage & Waterlogging", 12.9430, 77.6070, 14),
    ("Street light pole rusted and tilting near the school", "Streetlight", 12.9382, 77.6048, 5),
    ("Dead animal on the road near Market Circle, needs removal", "Garbage & Waste", 12.9398, 77.6298, 1),
    ("Borewell pump not working, no water in public tap", "Water Supply", 12.9160, 77.6290, 7),
    ("Manhole lid sunk below road level, cars bumping", "Road Damage", 12.9295, 77.6210, 6),
    # --- Messy / vague on purpose (AI can be wrong here)
    ("road brokn near temple pls do somthing", "Road Damage", 12.9305, 77.6225, 4),
    ("light not working", "Streetlight", 12.9370, 77.6140, 6),
    ("smell very bad here since many days", "Garbage & Waste", 12.9235, 77.6335, 3),
    ("water water everywhere cant walk", "Drainage & Waterlogging", 12.9260, 77.6110, 2),
    ("pls fix asap", "Road Damage", 12.9345, 77.6295, 7),
]