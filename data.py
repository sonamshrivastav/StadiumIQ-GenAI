"""
StadiumIQ — FIFA World Cup 2026 Stadium Data
All 16 venues, match schedule, facilities, and simulated real-time data.
"""

import random
from datetime import datetime, timedelta

# ──────────────────────────────────────────────
# STADIUMS — All 16 FIFA World Cup 2026 Venues
# ──────────────────────────────────────────────

STADIUMS = {
    "metlife": {
        "id": "metlife",
        "name": "MetLife Stadium",
        "city": "New York / New Jersey",
        "country": "USA",
        "capacity": 82500,
        "lat": 40.8128,
        "lng": -74.0742,
        "image": "🏟️",
        "timezone": "America/New_York",
        "facilities": {
            "food_courts": [
                {"id": "f1", "name": "Main Concourse Food Hall", "section": "100-Level", "type": "food", "lat": 40.8130, "lng": -74.0745},
                {"id": "f2", "name": "Premium Dining Club", "section": "200-Level", "type": "food", "lat": 40.8132, "lng": -74.0740},
                {"id": "f3", "name": "East Side Vendors", "section": "300-Level East", "type": "food", "lat": 40.8126, "lng": -74.0735},
            ],
            "restrooms": [
                {"id": "r1", "name": "Section 104 Restroom", "section": "104", "type": "restroom", "lat": 40.8129, "lng": -74.0748},
                {"id": "r2", "name": "Section 204 Restroom", "section": "204", "type": "restroom", "lat": 40.8131, "lng": -74.0743},
                {"id": "r3", "name": "Section 312 Restroom", "section": "312", "type": "restroom", "lat": 40.8127, "lng": -74.0738},
                {"id": "r4", "name": "Section 128 Restroom", "section": "128", "type": "restroom", "lat": 40.8125, "lng": -74.0746},
            ],
            "medical": [
                {"id": "m1", "name": "First Aid Station A", "section": "Gate A", "type": "medical", "lat": 40.8133, "lng": -74.0744},
                {"id": "m2", "name": "First Aid Station C", "section": "Gate C", "type": "medical", "lat": 40.8124, "lng": -74.0740},
            ],
            "exits": [
                {"id": "e1", "name": "Gate A (Main)", "section": "North", "type": "exit", "lat": 40.8135, "lng": -74.0742},
                {"id": "e2", "name": "Gate B", "section": "East", "type": "exit", "lat": 40.8128, "lng": -74.0732},
                {"id": "e3", "name": "Gate C", "section": "South", "type": "exit", "lat": 40.8121, "lng": -74.0742},
                {"id": "e4", "name": "Gate D", "section": "West", "type": "exit", "lat": 40.8128, "lng": -74.0752},
            ],
            "accessibility": [
                {"id": "a1", "name": "Wheelchair Ramp A", "section": "Gate A", "type": "accessibility", "lat": 40.8134, "lng": -74.0743},
                {"id": "a2", "name": "Elevator 1 (All Levels)", "section": "Section 110", "type": "accessibility", "lat": 40.8130, "lng": -74.0747},
                {"id": "a3", "name": "Sensory Room", "section": "Section 200", "type": "accessibility", "lat": 40.8131, "lng": -74.0741},
            ],
            "recycling": [
                {"id": "s1", "name": "Recycling Station 1", "section": "Gate A Concourse", "type": "recycling", "lat": 40.8134, "lng": -74.0745},
                {"id": "s2", "name": "Compost Bin Area", "section": "Section 200", "type": "recycling", "lat": 40.8130, "lng": -74.0739},
            ],
        },
        "transit": {
            "train": "NJ Transit from Penn Station (Meadowlands Line) — 30 min",
            "bus": "NJ Transit Bus 160/161 from Port Authority — 40 min",
            "shuttle": "Free FIFA Shuttle from Times Square — 45 min",
            "rideshare": "Uber/Lyft drop-off at Lot K — surge pricing expected on match days",
            "parking": "Lots A-K available ($50-$75). Lot E closest to Gate A. Pre-book via ParkMobile.",
        },
    },
    "sofi": {
        "id": "sofi",
        "name": "SoFi Stadium",
        "city": "Los Angeles",
        "country": "USA",
        "capacity": 70240,
        "lat": 33.9535,
        "lng": -118.3392,
        "image": "🏟️",
        "timezone": "America/Los_Angeles",
        "facilities": {
            "food_courts": [
                {"id": "f1", "name": "Hollywood Park Food Court", "section": "100-Level", "type": "food", "lat": 33.9537, "lng": -118.3395},
                {"id": "f2", "name": "Champions Lounge Dining", "section": "200-Level", "type": "food", "lat": 33.9533, "lng": -118.3390},
            ],
            "restrooms": [
                {"id": "r1", "name": "Section 101 Restroom", "section": "101", "type": "restroom", "lat": 33.9536, "lng": -118.3397},
                {"id": "r2", "name": "Section 220 Restroom", "section": "220", "type": "restroom", "lat": 33.9534, "lng": -118.3388},
            ],
            "medical": [
                {"id": "m1", "name": "Medical Center East", "section": "Gate 1", "type": "medical", "lat": 33.9538, "lng": -118.3390},
            ],
            "exits": [
                {"id": "e1", "name": "Gate 1 (Main)", "section": "North", "type": "exit", "lat": 33.9540, "lng": -118.3392},
                {"id": "e2", "name": "Gate 5", "section": "South", "type": "exit", "lat": 33.9530, "lng": -118.3392},
            ],
            "accessibility": [
                {"id": "a1", "name": "ADA Entrance Gate 1", "section": "Gate 1", "type": "accessibility", "lat": 33.9539, "lng": -118.3393},
            ],
            "recycling": [
                {"id": "s1", "name": "Zero Waste Station", "section": "Gate 1 Plaza", "type": "recycling", "lat": 33.9539, "lng": -118.3394},
            ],
        },
        "transit": {
            "train": "LA Metro C Line to Downtown Inglewood Station — walk 15 min",
            "bus": "Metro Bus Line 212 — stops at Prairie Ave",
            "shuttle": "Free FIFA Shuttle from LA Union Station — 50 min",
            "rideshare": "Uber/Lyft at designated zone on Pincay Dr",
            "parking": "SoFi lots ($60-$100). Book via SpotHero.",
        },
    },
    "hardrock": {
        "id": "hardrock",
        "name": "Hard Rock Stadium",
        "city": "Miami",
        "country": "USA",
        "capacity": 65326,
        "lat": 25.9580,
        "lng": -80.2389,
        "image": "🏟️",
        "timezone": "America/New_York",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Tropical Concourse", "section": "100-Level", "type": "food", "lat": 25.9582, "lng": -80.2391}],
            "restrooms": [{"id": "r1", "name": "Section 110 Restroom", "section": "110", "type": "restroom", "lat": 25.9581, "lng": -80.2393}],
            "medical": [{"id": "m1", "name": "First Aid North", "section": "Gate 1", "type": "medical", "lat": 25.9584, "lng": -80.2389}],
            "exits": [{"id": "e1", "name": "Gate 1", "section": "NW", "type": "exit", "lat": 25.9585, "lng": -80.2392}],
            "accessibility": [{"id": "a1", "name": "ADA Gate 1", "section": "Gate 1", "type": "accessibility", "lat": 25.9584, "lng": -80.2390}],
            "recycling": [{"id": "s1", "name": "Eco Station NW", "section": "NW Plaza", "type": "recycling", "lat": 25.9583, "lng": -80.2391}],
        },
        "transit": {"train": "Tri-Rail to Opa-Locka + shuttle", "bus": "Miami-Dade Route 297", "shuttle": "FIFA Shuttle from Brickell", "rideshare": "Drop-off at NW 27th Ave", "parking": "Lots $40-$60"},
    },
    "att": {
        "id": "att",
        "name": "AT&T Stadium",
        "city": "Dallas",
        "country": "USA",
        "capacity": 80000,
        "lat": 32.7473,
        "lng": -97.0945,
        "image": "🏟️",
        "timezone": "America/Chicago",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Lone Star Grill", "section": "Main Concourse", "type": "food", "lat": 32.7475, "lng": -97.0947}],
            "restrooms": [{"id": "r1", "name": "Section 200 Restroom", "section": "200", "type": "restroom", "lat": 32.7474, "lng": -97.0949}],
            "medical": [{"id": "m1", "name": "Medical Suite", "section": "Gate A", "type": "medical", "lat": 32.7477, "lng": -97.0945}],
            "exits": [{"id": "e1", "name": "Gate A", "section": "East", "type": "exit", "lat": 32.7478, "lng": -97.0940}],
            "accessibility": [{"id": "a1", "name": "ADA Entrance East", "section": "Gate A", "type": "accessibility", "lat": 32.7477, "lng": -97.0941}],
            "recycling": [{"id": "s1", "name": "Recycling Hub East", "section": "East Plaza", "type": "recycling", "lat": 32.7476, "lng": -97.0942}],
        },
        "transit": {"train": "TRE to CentrePort + shuttle", "bus": "Arlington Trolley", "shuttle": "FIFA Shuttle from Dallas Downtown", "rideshare": "Lot 15 drop-off", "parking": "Lots $50-$75"},
    },
    "nrg": {
        "id": "nrg",
        "name": "NRG Stadium",
        "city": "Houston",
        "country": "USA",
        "capacity": 72220,
        "lat": 29.6847,
        "lng": -95.4107,
        "image": "🏟️",
        "timezone": "America/Chicago",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Texan BBQ Court", "section": "100-Level", "type": "food", "lat": 29.6849, "lng": -95.4109}],
            "restrooms": [{"id": "r1", "name": "Section 120 Restroom", "section": "120", "type": "restroom", "lat": 29.6848, "lng": -95.4111}],
            "medical": [{"id": "m1", "name": "First Aid South", "section": "Gate 1", "type": "medical", "lat": 29.6851, "lng": -95.4107}],
            "exits": [{"id": "e1", "name": "Gate 1", "section": "North", "type": "exit", "lat": 29.6852, "lng": -95.4107}],
            "accessibility": [{"id": "a1", "name": "ADA Gate 1", "section": "Gate 1", "type": "accessibility", "lat": 29.6851, "lng": -95.4108}],
            "recycling": [{"id": "s1", "name": "Eco Bin North", "section": "Gate 1 Plaza", "type": "recycling", "lat": 29.6850, "lng": -95.4108}],
        },
        "transit": {"train": "METRORail to NRG Park/Fannin South", "bus": "Metro Route 8", "shuttle": "FIFA Shuttle from GRB Convention Center", "rideshare": "Yellow Lot drop-off", "parking": "Lots $40-$60"},
    },
    "mercedes": {
        "id": "mercedes",
        "name": "Mercedes-Benz Stadium",
        "city": "Atlanta",
        "country": "USA",
        "capacity": 71000,
        "lat": 33.7553,
        "lng": -84.4006,
        "image": "🏟️",
        "timezone": "America/New_York",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Peachtree Eats", "section": "100-Level", "type": "food", "lat": 33.7555, "lng": -84.4008}],
            "restrooms": [{"id": "r1", "name": "Section 108 Restroom", "section": "108", "type": "restroom", "lat": 33.7554, "lng": -84.4010}],
            "medical": [{"id": "m1", "name": "First Aid West", "section": "Gate 1", "type": "medical", "lat": 33.7557, "lng": -84.4006}],
            "exits": [{"id": "e1", "name": "Gate 1", "section": "NW", "type": "exit", "lat": 33.7558, "lng": -84.4006}],
            "accessibility": [{"id": "a1", "name": "ADA Gate 1", "section": "Gate 1", "type": "accessibility", "lat": 33.7557, "lng": -84.4007}],
            "recycling": [{"id": "s1", "name": "Zero Waste Station NW", "section": "NW Plaza", "type": "recycling", "lat": 33.7556, "lng": -84.4007}],
        },
        "transit": {"train": "MARTA to Vine City or GWCC stations", "bus": "MARTA Route 1", "shuttle": "FIFA Shuttle from Centennial Park", "rideshare": "Northside Dr drop-off", "parking": "Lots $40-$60"},
    },
    "gillette": {
        "id": "gillette",
        "name": "Gillette Stadium",
        "city": "Boston",
        "country": "USA",
        "capacity": 65878,
        "lat": 42.0909,
        "lng": -71.2643,
        "image": "🏟️",
        "timezone": "America/New_York",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Patriots Place Eats", "section": "100-Level", "type": "food", "lat": 42.0911, "lng": -71.2645}],
            "restrooms": [{"id": "r1", "name": "Section 106 Restroom", "section": "106", "type": "restroom", "lat": 42.0910, "lng": -71.2647}],
            "medical": [{"id": "m1", "name": "First Aid East", "section": "Gate B", "type": "medical", "lat": 42.0912, "lng": -71.2641}],
            "exits": [{"id": "e1", "name": "Gate B", "section": "East", "type": "exit", "lat": 42.0913, "lng": -71.2640}],
            "accessibility": [{"id": "a1", "name": "ADA Gate B", "section": "Gate B", "type": "accessibility", "lat": 42.0912, "lng": -71.2642}],
            "recycling": [{"id": "s1", "name": "Eco Station East", "section": "East Plaza", "type": "recycling", "lat": 42.0911, "lng": -71.2641}],
        },
        "transit": {"train": "MBTA Commuter Rail to Foxborough (match-day service)", "bus": "Bloom Bus from Boston South Station", "shuttle": "FIFA Shuttle from Boston Common", "rideshare": "Route 1 drop-off zone", "parking": "Lots $40-$50"},
    },
    "arrowhead": {
        "id": "arrowhead",
        "name": "Arrowhead Stadium",
        "city": "Kansas City",
        "country": "USA",
        "capacity": 76416,
        "lat": 39.0489,
        "lng": -94.4839,
        "image": "🏟️",
        "timezone": "America/Chicago",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "KC BBQ Pit", "section": "100-Level", "type": "food", "lat": 39.0491, "lng": -94.4841}],
            "restrooms": [{"id": "r1", "name": "Section 115 Restroom", "section": "115", "type": "restroom", "lat": 39.0490, "lng": -94.4843}],
            "medical": [{"id": "m1", "name": "First Aid Gate A", "section": "Gate A", "type": "medical", "lat": 39.0493, "lng": -94.4839}],
            "exits": [{"id": "e1", "name": "Gate A", "section": "West", "type": "exit", "lat": 39.0494, "lng": -94.4842}],
            "accessibility": [{"id": "a1", "name": "ADA Gate A", "section": "Gate A", "type": "accessibility", "lat": 39.0493, "lng": -94.4840}],
            "recycling": [{"id": "s1", "name": "Recycling Center West", "section": "West Lot", "type": "recycling", "lat": 39.0492, "lng": -94.4841}],
        },
        "transit": {"train": "No direct rail — shuttle recommended", "bus": "KCATA Route 47", "shuttle": "FIFA Shuttle from Union Station", "rideshare": "Lot G drop-off", "parking": "Lots $35-$50"},
    },
    "lincoln": {
        "id": "lincoln",
        "name": "Lincoln Financial Field",
        "city": "Philadelphia",
        "country": "USA",
        "capacity": 69796,
        "lat": 39.9008,
        "lng": -75.1675,
        "image": "🏟️",
        "timezone": "America/New_York",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Philly Cheesesteak Court", "section": "100-Level", "type": "food", "lat": 39.9010, "lng": -75.1677}],
            "restrooms": [{"id": "r1", "name": "Section 122 Restroom", "section": "122", "type": "restroom", "lat": 39.9009, "lng": -75.1679}],
            "medical": [{"id": "m1", "name": "First Aid SW", "section": "Gate A", "type": "medical", "lat": 39.9012, "lng": -75.1675}],
            "exits": [{"id": "e1", "name": "Gate A", "section": "SW", "type": "exit", "lat": 39.9013, "lng": -75.1675}],
            "accessibility": [{"id": "a1", "name": "ADA Gate A", "section": "Gate A", "type": "accessibility", "lat": 39.9012, "lng": -75.1676}],
            "recycling": [{"id": "s1", "name": "Eco Hub SW", "section": "SW Plaza", "type": "recycling", "lat": 39.9011, "lng": -75.1676}],
        },
        "transit": {"train": "SEPTA Broad Street Line to NRG station", "bus": "SEPTA Route 17", "shuttle": "FIFA Shuttle from City Hall", "rideshare": "Pattison Ave drop-off", "parking": "Lots $40-$60"},
    },
    "levis": {
        "id": "levis",
        "name": "Levi's Stadium",
        "city": "San Francisco Bay Area",
        "country": "USA",
        "capacity": 68500,
        "lat": 37.4033,
        "lng": -121.9694,
        "image": "🏟️",
        "timezone": "America/Los_Angeles",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Silicon Valley Bites", "section": "100-Level", "type": "food", "lat": 37.4035, "lng": -121.9696}],
            "restrooms": [{"id": "r1", "name": "Section 110 Restroom", "section": "110", "type": "restroom", "lat": 37.4034, "lng": -121.9698}],
            "medical": [{"id": "m1", "name": "First Aid Gate A", "section": "Gate A", "type": "medical", "lat": 37.4037, "lng": -121.9694}],
            "exits": [{"id": "e1", "name": "Gate A", "section": "NE", "type": "exit", "lat": 37.4038, "lng": -121.9694}],
            "accessibility": [{"id": "a1", "name": "ADA Gate A", "section": "Gate A", "type": "accessibility", "lat": 37.4037, "lng": -121.9695}],
            "recycling": [{"id": "s1", "name": "Green Station NE", "section": "NE Plaza", "type": "recycling", "lat": 37.4036, "lng": -121.9695}],
        },
        "transit": {"train": "VTA Light Rail + Caltrain to Great America", "bus": "VTA Route 10", "shuttle": "FIFA Shuttle from San Jose Diridon", "rideshare": "Tasman Dr drop-off", "parking": "Lots $50-$70"},
    },
    "lumen": {
        "id": "lumen",
        "name": "Lumen Field",
        "city": "Seattle",
        "country": "USA",
        "capacity": 69000,
        "lat": 47.5952,
        "lng": -122.3316,
        "image": "🏟️",
        "timezone": "America/Los_Angeles",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Pacific NW Eats", "section": "100-Level", "type": "food", "lat": 47.5954, "lng": -122.3318}],
            "restrooms": [{"id": "r1", "name": "Section 130 Restroom", "section": "130", "type": "restroom", "lat": 47.5953, "lng": -122.3320}],
            "medical": [{"id": "m1", "name": "First Aid Gate N", "section": "Gate N", "type": "medical", "lat": 47.5956, "lng": -122.3316}],
            "exits": [{"id": "e1", "name": "Gate N", "section": "North", "type": "exit", "lat": 47.5957, "lng": -122.3316}],
            "accessibility": [{"id": "a1", "name": "ADA Gate N", "section": "Gate N", "type": "accessibility", "lat": 47.5956, "lng": -122.3317}],
            "recycling": [{"id": "s1", "name": "Eco Station N", "section": "North Concourse", "type": "recycling", "lat": 47.5955, "lng": -122.3317}],
        },
        "transit": {"train": "Link Light Rail to Stadium station", "bus": "Metro Route 21/124", "shuttle": "FIFA Shuttle from Westlake Center", "rideshare": "Occidental Ave drop-off", "parking": "Lots $40-$60"},
    },
    "azteca": {
        "id": "azteca",
        "name": "Estadio Azteca",
        "city": "Mexico City",
        "country": "Mexico",
        "capacity": 87523,
        "lat": 19.3029,
        "lng": -99.1505,
        "image": "🏟️",
        "timezone": "America/Mexico_City",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Tacos & Antojitos Plaza", "section": "Planta Baja", "type": "food", "lat": 19.3031, "lng": -99.1507}],
            "restrooms": [{"id": "r1", "name": "Zona Norte Baños", "section": "Norte", "type": "restroom", "lat": 19.3032, "lng": -99.1509}],
            "medical": [{"id": "m1", "name": "Cruz Roja Station", "section": "Puerta 1", "type": "medical", "lat": 19.3033, "lng": -99.1505}],
            "exits": [{"id": "e1", "name": "Puerta 1", "section": "Norte", "type": "exit", "lat": 19.3034, "lng": -99.1505}],
            "accessibility": [{"id": "a1", "name": "Acceso Universal P1", "section": "Puerta 1", "type": "accessibility", "lat": 19.3033, "lng": -99.1506}],
            "recycling": [{"id": "s1", "name": "Estación Verde Norte", "section": "Norte", "type": "recycling", "lat": 19.3032, "lng": -99.1506}],
        },
        "transit": {"train": "Metro Línea 2 to Tasqueña + Tren Ligero", "bus": "Metrobús Línea 1 to Estadio Azteca", "shuttle": "FIFA Shuttle from Zócalo", "rideshare": "Calzada de Tlalpan drop-off", "parking": "Estacionamiento $300-500 MXN"},
    },
    "akron": {
        "id": "akron",
        "name": "Estadio Akron",
        "city": "Guadalajara",
        "country": "Mexico",
        "capacity": 49850,
        "lat": 20.6827,
        "lng": -103.4625,
        "image": "🏟️",
        "timezone": "America/Mexico_City",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Birria & Tortas", "section": "Planta Baja", "type": "food", "lat": 20.6829, "lng": -103.4627}],
            "restrooms": [{"id": "r1", "name": "Zona Sur Baños", "section": "Sur", "type": "restroom", "lat": 20.6828, "lng": -103.4629}],
            "medical": [{"id": "m1", "name": "Primeros Auxilios", "section": "Puerta A", "type": "medical", "lat": 20.6831, "lng": -103.4625}],
            "exits": [{"id": "e1", "name": "Puerta A", "section": "Oriente", "type": "exit", "lat": 20.6832, "lng": -103.4623}],
            "accessibility": [{"id": "a1", "name": "Acceso Universal PA", "section": "Puerta A", "type": "accessibility", "lat": 20.6831, "lng": -103.4624}],
            "recycling": [{"id": "s1", "name": "Estación Reciclaje", "section": "Oriente", "type": "recycling", "lat": 20.6830, "lng": -103.4624}],
        },
        "transit": {"train": "Mi Macro Calzada to Zapopan", "bus": "Ruta 631 from Centro", "shuttle": "FIFA Shuttle from Plaza Tapatía", "rideshare": "Av. de las Rosas drop-off", "parking": "Lots $200-400 MXN"},
    },
    "bbva": {
        "id": "bbva",
        "name": "Estadio BBVA",
        "city": "Monterrey",
        "country": "Mexico",
        "capacity": 53500,
        "lat": 25.6652,
        "lng": -100.2446,
        "image": "🏟️",
        "timezone": "America/Monterrey",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Carne Asada Court", "section": "Planta Baja", "type": "food", "lat": 25.6654, "lng": -100.2448}],
            "restrooms": [{"id": "r1", "name": "Zona Poniente Baños", "section": "Poniente", "type": "restroom", "lat": 25.6653, "lng": -100.2450}],
            "medical": [{"id": "m1", "name": "Primeros Auxilios P1", "section": "Puerta 1", "type": "medical", "lat": 25.6656, "lng": -100.2446}],
            "exits": [{"id": "e1", "name": "Puerta 1", "section": "Norte", "type": "exit", "lat": 25.6657, "lng": -100.2446}],
            "accessibility": [{"id": "a1", "name": "Acceso Universal", "section": "Puerta 1", "type": "accessibility", "lat": 25.6656, "lng": -100.2447}],
            "recycling": [{"id": "s1", "name": "Punto Verde", "section": "Norte", "type": "recycling", "lat": 25.6655, "lng": -100.2447}],
        },
        "transit": {"train": "Metrorrey Línea 1 to Exposición + bus", "bus": "Ruta 42 from Macroplaza", "shuttle": "FIFA Shuttle from Fundidora Park", "rideshare": "Av. Pablo Livas drop-off", "parking": "Lots $200-400 MXN"},
    },
    "bmo": {
        "id": "bmo",
        "name": "BMO Field",
        "city": "Toronto",
        "country": "Canada",
        "capacity": 45736,
        "lat": 43.6332,
        "lng": -79.4186,
        "image": "🏟️",
        "timezone": "America/Toronto",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "Lakeshore Eats", "section": "100-Level", "type": "food", "lat": 43.6334, "lng": -79.4188}],
            "restrooms": [{"id": "r1", "name": "Section 105 Washroom", "section": "105", "type": "restroom", "lat": 43.6333, "lng": -79.4190}],
            "medical": [{"id": "m1", "name": "First Aid Gate 1", "section": "Gate 1", "type": "medical", "lat": 43.6336, "lng": -79.4186}],
            "exits": [{"id": "e1", "name": "Gate 1", "section": "East", "type": "exit", "lat": 43.6337, "lng": -79.4184}],
            "accessibility": [{"id": "a1", "name": "Accessible Gate 1", "section": "Gate 1", "type": "accessibility", "lat": 43.6336, "lng": -79.4185}],
            "recycling": [{"id": "s1", "name": "Green Bin Station", "section": "East Concourse", "type": "recycling", "lat": 43.6335, "lng": -79.4185}],
        },
        "transit": {"train": "TTC Streetcar 509/511 to Exhibition", "bus": "TTC Bus 29 Dufferin", "shuttle": "FIFA Shuttle from Union Station", "rideshare": "Princes' Blvd drop-off", "parking": "Exhibition Place lots $30-50 CAD"},
    },
    "bcplace": {
        "id": "bcplace",
        "name": "BC Place",
        "city": "Vancouver",
        "country": "Canada",
        "capacity": 54500,
        "lat": 49.2768,
        "lng": -123.1118,
        "image": "🏟️",
        "timezone": "America/Vancouver",
        "facilities": {
            "food_courts": [{"id": "f1", "name": "West Coast Kitchen", "section": "100-Level", "type": "food", "lat": 49.2770, "lng": -123.1120}],
            "restrooms": [{"id": "r1", "name": "Section 215 Washroom", "section": "215", "type": "restroom", "lat": 49.2769, "lng": -123.1122}],
            "medical": [{"id": "m1", "name": "First Aid Gate A", "section": "Gate A", "type": "medical", "lat": 49.2772, "lng": -123.1118}],
            "exits": [{"id": "e1", "name": "Gate A", "section": "North", "type": "exit", "lat": 49.2773, "lng": -123.1118}],
            "accessibility": [{"id": "a1", "name": "Accessible Gate A", "section": "Gate A", "type": "accessibility", "lat": 49.2772, "lng": -123.1119}],
            "recycling": [{"id": "s1", "name": "Zero Waste Hub", "section": "North Concourse", "type": "recycling", "lat": 49.2771, "lng": -123.1119}],
        },
        "transit": {"train": "SkyTrain Expo/Canada Line to Stadium-Chinatown", "bus": "TransLink Route 17/19", "shuttle": "FIFA Shuttle from Waterfront Station", "rideshare": "Beatty St drop-off", "parking": "BC Place parkade $25-40 CAD"},
    },
}

# ──────────────────────────────────────────────
# MATCH SCHEDULE — Active Group Stage (July 2026)
# ──────────────────────────────────────────────

MATCHES = [
    {"id": "m1", "team1": "🇧🇷 Brazil", "team2": "🇳🇬 Nigeria", "stadium_id": "metlife", "date": "2026-07-10", "time": "18:00", "group": "A", "status": "upcoming"},
    {"id": "m2", "team1": "🇩🇪 Germany", "team2": "🇯🇵 Japan", "stadium_id": "sofi", "date": "2026-07-10", "time": "15:00", "group": "B", "status": "upcoming"},
    {"id": "m3", "team1": "🇦🇷 Argentina", "team2": "🇦🇺 Australia", "stadium_id": "hardrock", "date": "2026-07-11", "time": "19:00", "group": "C", "status": "upcoming"},
    {"id": "m4", "team1": "🇫🇷 France", "team2": "🇰🇷 South Korea", "stadium_id": "att", "date": "2026-07-11", "time": "16:00", "group": "D", "status": "upcoming"},
    {"id": "m5", "team1": "🇪🇸 Spain", "team2": "🇨🇦 Canada", "stadium_id": "bmo", "date": "2026-07-12", "time": "14:00", "group": "E", "status": "upcoming"},
    {"id": "m6", "team1": "🇬🇧 England", "team2": "🇸🇳 Senegal", "stadium_id": "mercedes", "date": "2026-07-12", "time": "20:00", "group": "F", "status": "upcoming"},
    {"id": "m7", "team1": "🇺🇸 USA", "team2": "🇲🇽 Mexico", "stadium_id": "azteca", "date": "2026-07-13", "time": "17:00", "group": "G", "status": "upcoming"},
    {"id": "m8", "team1": "🇵🇹 Portugal", "team2": "🇳🇱 Netherlands", "stadium_id": "gillette", "date": "2026-07-13", "time": "19:00", "group": "H", "status": "upcoming"},
    {"id": "m9", "team1": "🇮🇹 Italy", "team2": "🇨🇴 Colombia", "stadium_id": "nrg", "date": "2026-07-14", "time": "18:00", "group": "A", "status": "upcoming"},
    {"id": "m10", "team1": "🇧🇪 Belgium", "team2": "🇲🇦 Morocco", "stadium_id": "lumen", "date": "2026-07-14", "time": "15:00", "group": "B", "status": "upcoming"},
    {"id": "m11", "team1": "🇭🇷 Croatia", "team2": "🇪🇨 Ecuador", "stadium_id": "levis", "date": "2026-07-15", "time": "16:00", "group": "C", "status": "upcoming"},
    {"id": "m12", "team1": "🇺🇾 Uruguay", "team2": "🇬🇭 Ghana", "stadium_id": "arrowhead", "date": "2026-07-15", "time": "19:00", "group": "D", "status": "upcoming"},
]


# ──────────────────────────────────────────────
# SIMULATED CROWD DATA
# ──────────────────────────────────────────────

def get_crowd_data(stadium_id: str) -> dict:
    """Generate simulated real-time crowd density data for a stadium."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}

    zones = ["North Gate", "South Gate", "East Gate", "West Gate",
             "Main Concourse", "Upper Deck", "Lower Bowl", "VIP Section"]

    total_in = 0
    zone_data = []
    for zone in zones:
        density = random.randint(20, 95)
        capacity_pct = density
        people_count = int((density / 100) * (stadium["capacity"] // len(zones)))
        total_in += people_count
        zone_data.append({
            "zone": zone,
            "density_pct": capacity_pct,
            "people_count": people_count,
            "status": "critical" if density > 85 else "high" if density > 65 else "moderate" if density > 40 else "low",
            "wait_time_min": max(0, int((density - 30) * 0.3)),
        })

    return {
        "stadium_id": stadium_id,
        "stadium_name": stadium["name"],
        "total_capacity": stadium["capacity"],
        "total_inside": total_in,
        "occupancy_pct": round((total_in / stadium["capacity"]) * 100, 1),
        "zones": zone_data,
        "timestamp": datetime.utcnow().isoformat(),
        "alerts": _generate_alerts(zone_data),
    }


def _generate_alerts(zone_data: list) -> list:
    """Generate crowd alerts based on zone density."""
    alerts = []
    for zone in zone_data:
        if zone["density_pct"] > 85:
            alerts.append({
                "level": "critical",
                "zone": zone["zone"],
                "message": f"⚠️ {zone['zone']} at {zone['density_pct']}% capacity — consider diverting flow",
            })
        elif zone["density_pct"] > 75:
            alerts.append({
                "level": "warning",
                "zone": zone["zone"],
                "message": f"🟡 {zone['zone']} approaching capacity ({zone['density_pct']}%)",
            })
    return alerts


# ──────────────────────────────────────────────
# INCIDENT TRACKER (In-Memory)
# ──────────────────────────────────────────────

import os
import json

_incidents = []
_incident_counter = 2800


def _seed_incidents():
    global _incident_counter
    report_path = "C:/Users/sonam/Downloads/FIFA_Nexus_Ops_Report_2026-07-09.json"
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                events = json.load(f)
            for event in events:
                if event.get("is_anomaly"):
                    _incident_counter += 1
                    predictions = event.get("predictions", [])
                    pred = predictions[0] if predictions else {}
                    desc = event.get("anomaly_reason") or pred.get("explanation") or "Unusual crowd density pattern"
                    loc = pred.get("affected_location") or "Concourse Area"
                    
                    # Clean up descriptions
                    if desc.startswith("Predicted Anomaly: "):
                        desc = desc[len("Predicted Anomaly: "):]
                    
                    status = "active"
                    if event.get("status") == "PROCESSED_NOMINAL":
                        status = "resolved"
                    elif "READY" in str(event.get("status")):
                        status = "dispatched"
                    
                    # Get assigned unit if actions taken
                    assigned = "Response Unit " + str(random.randint(1, 4))
                    actions = event.get("actions_taken", [])
                    if actions:
                        res = actions[0].get("result", "")
                        if "Dispatched" in res:
                            assigned = res.replace("Dispatched ", "").split(" to ")[0]
                    
                    incident = {
                        "id": f"INC-{_incident_counter}",
                        "stadium_id": "metlife",  # Seeding MetLife as primary test stadium
                        "description": desc,
                        "location": loc,
                        "status": status,
                        "reported_at": event.get("telemetry_snapshot", {}).get("timestamp") or datetime.utcnow().isoformat(),
                        "eta_minutes": event.get("wait_time_estimate", 5),
                        "assigned_to": assigned,
                    }
                    _incidents.append(incident)
        except Exception as e:
            pass

# Seed initially
_seed_incidents()


def report_new_incident(stadium_id: str, description: str, location: str) -> dict:
    """Report a new incident at a stadium."""
    global _incident_counter
    _incident_counter += 1
    incident = {
        "id": f"INC-{_incident_counter}",
        "stadium_id": stadium_id,
        "description": description,
        "location": location,
        "status": "reported",
        "reported_at": datetime.utcnow().isoformat(),
        "eta_minutes": random.randint(2, 8),
        "assigned_to": random.choice(["Team Alpha", "Team Bravo", "Team Charlie", "Maintenance Unit 4"]),
    }
    _incidents.append(incident)
    return incident


def get_incidents(stadium_id: str) -> list:
    """Get all incidents for a stadium."""
    # Ensure we return both seeded and newly reported incidents for the stadium
    return [i for i in _incidents if i["stadium_id"] == stadium_id]

