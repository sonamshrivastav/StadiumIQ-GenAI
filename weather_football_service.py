import os
import json
import ssl
import time
import urllib.request
import threading
from datetime import datetime, timedelta
from data import STADIUMS, MATCHES

# ──────────────────────────────────────────────
# CONFIG & STATE
# ──────────────────────────────────────────────
FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY", "bf4edbdc9c03e58de50fb413df362def")

# Caches and Locks
_weather_cache = {}
_football_cache = {}
_weather_cache_lock = threading.Lock()
_football_cache_lock = threading.Lock()

# Weather Code Mapping (WMO Codes)
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def get_weather_desc(code):
    return WMO_WEATHER_CODES.get(code, "Cloudy")

# ──────────────────────────────────────────────
# INTELLIGENT CONTEXT LOADING CLASSIFIERS
# ──────────────────────────────────────────────

def should_fetch_weather(message: str) -> bool:
    """Determine if the user request depends on weather or if weather affects the scenario."""
    msg = message.lower()
    weather_terms = [
        "weather", "rain", "temp", "forecast", "wind", "humidity", "precip", 
        "sunny", "cloud", "storm", "heat", "cold", "wet", "dry", "umbrella", 
        "snow", "shower", "hot", "degree", "celsius", "fahrenheit", "sky"
    ]
    operational_terms = [
        "exit", "gate", "crowd", "congest", "transit", "bus", "train", "shuttle", 
        "parking", "route", "wheelchair", "accessible", "incident", "safety", "spill",
        "outdoor", "walk", "shelter"
    ]
    return any(term in msg for term in weather_terms + operational_terms)

def should_fetch_football(message: str) -> bool:
    """Determine if the user request depends on football matches/scores/schedule."""
    msg = message.lower()
    football_terms = [
        "match", "score", "kickoff", "play", "versus", "vs", "game", "team", 
        "goal", "card", "win", "lose", "schedule", "group", "tournament", 
        "standing", "fixture", "result", "cup", "half", "referee", "final", 
        "qualify", "eliminate", "knockout", "bracket", "winner", "stage"
    ]
    operational_terms = [
        "exit", "gate", "crowd", "congest", "leave", "leaving", "end", "concession",
        "food", "queue", "restroom", "wait"
    ]
    return any(term in msg for term in football_terms + operational_terms)

# ──────────────────────────────────────────────
# WEATHER SERVICE (OPEN-METEO)
# ──────────────────────────────────────────────

def get_weather_data(stadium_id: str) -> dict:
    """Fetch real-time weather from Open-Meteo with caching (15-min TTL) and graceful mock fallback."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": f"Stadium '{stadium_id}' not found."}

    # Check cache
    now = time.time()
    with _weather_cache_lock:
        if stadium_id in _weather_cache:
            cached_data, expiry = _weather_cache[stadium_id]
            if now < expiry:
                return cached_data

    # Fetch from Open-Meteo
    lat, lng = stadium["lat"], stadium["lng"]
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lng}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability,weather_code"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone=auto"
    )

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=8) as response:
            raw_res = json.loads(response.read().decode("utf-8"))
            
            # Parse Current weather
            current = raw_res.get("current", {})
            curr_temp = current.get("temperature_2m", 20.0)
            curr_humidity = current.get("relative_humidity_2m", 60)
            curr_wind = current.get("wind_speed_10m", 10.0)
            curr_precip = current.get("precipitation", 0.0)
            curr_code = current.get("weather_code", 0)
            
            # Forecast hourly
            hourly = raw_res.get("hourly", {})
            hourly_precip_probs = hourly.get("precipitation_probability", [])
            rain_prob = 0
            if hourly_precip_probs and len(hourly_precip_probs) > 0:
                # Average probability of next 3 hours
                rain_prob = int(sum(hourly_precip_probs[:3]) / min(3, len(hourly_precip_probs)))

            # Forecast daily (Today and Tomorrow)
            daily = raw_res.get("daily", {})
            daily_dates = daily.get("time", [])
            daily_codes = daily.get("weather_code", [])
            daily_max_temps = daily.get("temperature_2m_max", [])
            daily_min_temps = daily.get("temperature_2m_min", [])
            daily_precip_max = daily.get("precipitation_probability_max", [])
            
            forecast = []
            for i in range(min(3, len(daily_dates))):
                forecast.append({
                    "date": daily_dates[i],
                    "condition": get_weather_desc(daily_codes[i] if i < len(daily_codes) else 0),
                    "temp_max": daily_max_temps[i] if i < len(daily_max_temps) else 22.0,
                    "temp_min": daily_min_temps[i] if i < len(daily_min_temps) else 15.0,
                    "rain_probability_max": daily_precip_max[i] if i < len(daily_precip_max) else 0
                })

            weather_info = {
                "stadium_name": stadium["name"],
                "temperature": f"{curr_temp}°C",
                "condition": get_weather_desc(curr_code),
                "humidity": f"{curr_humidity}%",
                "wind_speed": f"{curr_wind} km/h",
                "precipitation_mm": f"{curr_precip} mm",
                "rain_probability": f"{rain_prob}%",
                "forecast": forecast,
                "is_simulated": False
            }
            
            # Cache it
            with _weather_cache_lock:
                _weather_cache[stadium_id] = (weather_info, now + 900)  # 15 minutes TTL
            return weather_info

    except Exception as e:
        print(f"[WeatherService] API call failed for {stadium_id}: {e}. Falling back to simulated weather.")
        # Fallback to simulated weather
        simulated_weather = {
            "stadium_name": stadium["name"],
            "temperature": "22°C",
            "condition": "Partly cloudy",
            "humidity": "55%",
            "wind_speed": "12 km/h",
            "precipitation_mm": "0.0 mm",
            "rain_probability": "10%",
            "forecast": [
                {"date": "Today", "condition": "Partly cloudy", "temp_max": 24, "temp_min": 17, "rain_probability_max": 15},
                {"date": "Tomorrow", "condition": "Clear sky", "temp_max": 26, "temp_min": 18, "rain_probability_max": 5},
                {"date": "Day After", "condition": "Overcast", "temp_max": 22, "temp_min": 16, "rain_probability_max": 40}
            ],
            "is_simulated": True
        }
        return simulated_weather

# ──────────────────────────────────────────────
# FOOTBALL SERVICE (API-FOOTBALL & STANDINGS)
# ──────────────────────────────────────────────

def _get_api_headers():
    return {
        "x-apisports-key": FOOTBALL_API_KEY
    }

def get_football_data(stadium_id: str = None) -> dict:
    """Delegator function to retrieve the full structured football context."""
    return get_structured_football_context(stadium_id)

def get_structured_football_context(stadium_id: str = None) -> dict:
    """Builds a structured tournament context by merging API-Football today's fixtures and calculating standings."""
    cache_key = stadium_id or "all_stadiums"
    now = time.time()

    # Check cache
    with _football_cache_lock:
        if cache_key in _football_cache:
            cached_data, expiry = _football_cache[cache_key]
            if now < expiry:
                return cached_data

    # 1. Fetch Today's fixtures from API-Football
    today_str = datetime.now().strftime("%Y-%m-%d")
    api_fixtures = []
    api_success = False
    
    url = f"https://v3.football.api-sports.io/fixtures?date={today_str}"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(url, headers=_get_api_headers())
        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            api_fixtures = res_data.get("response", [])
            if len(api_fixtures) > 0 and not res_data.get("errors"):
                api_success = True
    except Exception as e:
        print(f"[FootballService] Failed to load today's API-Football matches: {e}")

    # 2. Extract participating teams from simulated MATCHES
    all_groups = {}
    remaining_teams = set()
    for m in MATCHES:
        g = f"Group {m['group']}"
        if g not in all_groups:
            all_groups[g] = set()
        all_groups[g].add(m["team1"])
        all_groups[g].add(m["team2"])
        remaining_teams.add(m["team1"])
        remaining_teams.add(m["team2"])

    # Convert sets to sorted lists
    all_groups = {g: sorted(list(teams)) for g, teams in all_groups.items()}
    remaining_teams = sorted(list(remaining_teams))

    # 3. Compile and merge all tournament matches
    all_matches = []
    
    # We process each simulated match in MATCHES to determine its state
    for m in MATCHES:
        std = STADIUMS.get(m["stadium_id"], {})
        
        # Determine default status dynamically based on current time
        status_short = m["status"]
        elapsed = 0
        score_home = 0
        score_away = 0
        goals_details = []
        cards_details = []
        status_long = "Not Started"
        
        try:
            kickoff_dt = datetime.strptime(f"{m['date']} {m['time']}", "%Y-%m-%d %H:%M")
            now_dt = datetime.now()
            
            if now_dt >= kickoff_dt + timedelta(minutes=110):
                status_short = "FT"
                elapsed = 90
                score_home = 2
                score_away = 1
                status_long = "Match Finished"
                goals_details = [
                    {"elapsed": 15, "team": m["team1"], "player": "Forward A", "detail": "Normal Goal"},
                    {"elapsed": 50, "team": m["team2"], "player": "Midfielder B", "detail": "Normal Goal"},
                    {"elapsed": 82, "team": m["team1"], "player": "Captain C", "detail": "Normal Goal"}
                ]
                cards_details = [
                    {"elapsed": 40, "team": m["team2"], "player": "Defender D", "detail": "Yellow Card"}
                ]
            elif now_dt >= kickoff_dt:
                status_short = "live"
                diff_min = int((now_dt - kickoff_dt).total_seconds() / 60)
                elapsed = min(90, diff_min)
                score_home = 1
                score_away = 0
                status_long = "In Progress"
                goals_details = [
                    {"elapsed": min(elapsed, 30), "team": m["team1"], "player": "Forward A", "detail": "Normal Goal"}
                ]
            else:
                status_short = "NS"
                elapsed = 0
                status_long = "Not Started"
        except Exception:
            status_short = "NS"
            elapsed = 0

        # Construct the match record
        match_record = {
            "match_id": m["id"],
            "competition": "FIFA World Cup",
            "group": f"Group {m['group']}",
            "teams": {
                "home": m["team1"],
                "away": m["team2"]
            },
            "venue": {
                "stadium_id": m["stadium_id"],
                "name": std.get("name", "Unknown Stadium"),
                "city": std.get("city", "Unknown City")
            },
            "date": m["date"],
            "time": m["time"],
            "kickoff_time": f"{m['date']}T{m['time']}:00",
            "status": status_long,
            "status_short": status_short,
            "elapsed_minutes": elapsed,
            "score": {
                "home": score_home,
                "away": score_away
            },
            "goals_details": goals_details,
            "cards_details": cards_details
        }

        # Override simulated today's matches with real API-Football matches at the same venue
        if m["date"] == today_str:
            # Check if there is an API match that fits this venue
            for api_f in api_fixtures:
                v_name = api_f.get("fixture", {}).get("venue", {}).get("name") or ""
                v_city = api_f.get("fixture", {}).get("venue", {}).get("city") or ""
                
                s_name = std.get("name", "").lower()
                s_cities = [c.strip().lower() for c in std.get("city", "").split("/")]
                
                if s_name in v_name.lower() or any(c in v_city.lower() for c in s_cities):
                    # Found a matching real match! Override!
                    api_status_short = api_f["fixture"]["status"]["short"]
                    api_elapsed = api_f["fixture"]["status"]["elapsed"]
                    api_teams = api_f["teams"]
                    api_goals = api_f["goals"]
                    
                    match_record["status"] = api_f["fixture"]["status"]["long"]
                    match_record["status_short"] = api_status_short
                    match_record["elapsed_minutes"] = api_elapsed
                    match_record["score"] = {
                        "home": api_goals.get("home", 0) if api_goals.get("home") is not None else 0,
                        "away": api_goals.get("away", 0) if api_goals.get("away") is not None else 0
                    }
                    
                    # Fetch detailed events if match is live/finished
                    api_goals_details = []
                    api_cards_details = []
                    if api_status_short not in ["NS", "TBD"]:
                        events = _fetch_match_events(api_f["fixture"]["id"], ctx)
                        for ev in events:
                            ev_type = ev.get("type", "").lower()
                            el_min = ev.get("time", {}).get("elapsed", 0)
                            t_name = ev.get("team", {}).get("name", "")
                            p_name = ev.get("player", {}).get("name", "")
                            detail = ev.get("detail", "")
                            
                            if ev_type == "goal":
                                api_goals_details.append({
                                    "elapsed": el_min,
                                    "team": t_name,
                                    "player": p_name,
                                    "detail": detail
                                })
                            elif ev_type == "card":
                                api_cards_details.append({
                                    "elapsed": el_min,
                                    "team": t_name,
                                    "player": p_name,
                                    "detail": detail
                                })
                    
                    match_record["goals_details"] = api_goals_details
                    match_record["cards_details"] = api_cards_details
                    break

        all_matches.append(match_record)

    # 4. Categorize matches
    completed_matches = []
    live_matches = []
    upcoming_matches = []
    today_fixtures = []

    for m in all_matches:
        if m["date"] == today_str:
            today_fixtures.append(m)
            
        if m["status_short"] == "FT":
            completed_matches.append(m)
        elif m["status_short"] in ["live", "1H", "2H", "HT", "ET", "P"]:
            live_matches.append(m)
        else:
            upcoming_matches.append(m)

    # If filtering by stadium_id, keep a flag or subset of today's fixtures for that stadium
    stadium_today_fixtures = []
    if stadium_id:
        stadium_today_fixtures = [m for m in today_fixtures if m["venue"]["stadium_id"] == stadium_id]

    # 5. Calculate group standings dynamically based on completed and live matches
    group_tables = {}
    for g, teams in all_groups.items():
        # Initialize standings for this group
        group_tables[g] = {}
        for t in teams:
            group_tables[g][t] = {
                "team": t,
                "played": 0,
                "won": 0,
                "drawn": 0,
                "lost": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
                "points": 0
            }

    # Process match results to update standings
    for m in completed_matches + live_matches:
        g = m["group"]
        if g not in group_tables:
            continue
            
        home = m["teams"]["home"]
        away = m["teams"]["away"]
        
        # Verify the teams belong to the group (in case of mock mismatch)
        if home not in group_tables[g] or away not in group_tables[g]:
            continue
            
        h_score = m["score"]["home"]
        a_score = m["score"]["away"]
        
        # Update home team
        h_stats = group_tables[g][home]
        h_stats["played"] += 1
        h_stats["goals_for"] += h_score
        h_stats["goals_against"] += a_score
        h_stats["goal_difference"] = h_stats["goals_for"] - h_stats["goals_against"]
        
        # Update away team
        a_stats = group_tables[g][away]
        a_stats["played"] += 1
        a_stats["goals_for"] += a_score
        a_stats["goals_against"] += h_score
        a_stats["goal_difference"] = a_stats["goals_for"] - a_stats["goals_against"]
        
        if h_score > a_score:
            h_stats["won"] += 1
            h_stats["points"] += 3
            a_stats["lost"] += 1
        elif h_score < a_score:
            a_stats["won"] += 1
            a_stats["points"] += 3
            h_stats["lost"] += 1
        else:
            h_stats["drawn"] += 1
            h_stats["points"] += 1
            a_stats["drawn"] += 1
            a_stats["points"] += 1

    # Sort each group standings by points, GD, GF
    sorted_standings = {}
    for g, teams_stats in group_tables.items():
        sorted_list = list(teams_stats.values())
        # Sort key: points (desc), goal_difference (desc), goals_for (desc), team_name (asc)
        sorted_list.sort(key=lambda x: (-x["points"], -x["goal_difference"], -x["goals_for"], x["team"]))
        sorted_standings[g] = sorted_list

    # 6. Format final context response
    result_context = {
        "tournament_name": "FIFA World Cup 2026",
        "competition": "FIFA World Cup 2026 Tournament",
        "current_tournament_stage": "Group Stage",
        "remaining_teams": remaining_teams,
        "all_groups": all_groups,
        "today_fixtures": today_fixtures,
        "live_matches": live_matches,
        "completed_matches": completed_matches,
        "upcoming_matches": upcoming_matches,
        "group_standings": sorted_standings,
        "stadium_today_fixtures": stadium_today_fixtures,
        "data_source": "Merged API-Football & Simulation Structure",
        "is_live_api": api_success
    }

    # Cache the result
    with _football_cache_lock:
        _football_cache[cache_key] = (result_context, now + 120)  # 2 minutes TTL
        
    return result_context


def format_weather_context(ctx: dict) -> str:
    """Formats weather JSON context into a clean, token-efficient text summary."""
    if not ctx or not isinstance(ctx, dict) or "error" in ctx:
        return ""
    
    source_status = "[SIMULATED / DEMO DATA - Live API weather unavailable]" if ctx.get("is_simulated") else "[VERIFIED LIVE DATA - Open-Meteo]"
    
    lines = [
        f"Weather Context {source_status}:",
        f"  Stadium: {ctx['stadium_name']}",
        f"  Current Condition: {ctx['condition']}",
        f"  Temperature: {ctx['temperature']}",
        f"  Humidity: {ctx['humidity']}",
        f"  Wind Speed: {ctx['wind_speed']}",
        f"  Precipitation: {ctx['precipitation_mm']}",
        f"  Precipitation/Rain Probability (next 3 hours): {ctx['rain_probability']}",
        "  Forecast:"
    ]
    for day in ctx.get("forecast", []):
        lines.append(f"    - {day['date']}: {day['condition']} | High: {day['temp_max']}°C, Low: {day['temp_min']}°C | Rain Prob: {day['rain_probability_max']}%")
    return "\n".join(lines)


def format_football_context(ctx: dict, stadium_id: str = None) -> str:
    """Formats football JSON context (stages, groups, standings, fixtures, results) into a highly structured text summary."""
    if not ctx or not isinstance(ctx, dict):
        return ""
        
    source_status = "[VERIFIED LIVE DATA - API-Football]" if ctx.get("is_live_api") else "[SIMULATED / DEMO DATA - Live API match info unavailable or showing local seed fixtures]"
    
    lines = []
    lines.append(f"Tournament Context {source_status}:")
    lines.append(f"Tournament Name: {ctx.get('tournament_name', 'FIFA World Cup 2026')}")
    lines.append(f"Competition: {ctx.get('competition', 'FIFA World Cup 2026')}")
    lines.append(f"Current Tournament Stage: {ctx.get('current_tournament_stage', 'Group Stage')}")
    
    # Remaining teams
    teams = ctx.get("remaining_teams", [])
    lines.append(f"Remaining Teams in Tournament: {', '.join(teams)}")
    
    # Standings for Groups
    lines.append("\nCURRENT GROUP STANDINGS:")
    standings = ctx.get("group_standings", {})
    for grp, table in standings.items():
        lines.append(f"  {grp}:")
        lines.append("    Rank | Team | Played | Won | Drawn | Lost | GD | Points")
        for rank, t_stats in enumerate(table, 1):
            gd_str = f"{t_stats['goal_difference']:+d}" if t_stats['goal_difference'] != 0 else "0"
            lines.append(
                f"    {rank}. {t_stats['team']:<18} | "
                f"{t_stats['played']} | {t_stats['won']} | {t_stats['drawn']} | {t_stats['lost']} | "
                f"{gd_str:<2} | {t_stats['points']} pts"
            )
            
    # Today's Fixtures
    today_fix = ctx.get("today_fixtures", [])
    if today_fix:
        lines.append("\nTODAY'S FIXTURES:")
        for f in today_fix:
            lines.append(
                f"  - {f['teams']['home']} vs {f['teams']['away']} at {f['venue']['name']}, {f['venue']['city']} | "
                f"Status: {f['status']} | Score: {f['score']['home']}-{f['score']['away']} "
                f"({f['elapsed_minutes']} mins)"
            )
            if f.get("goals_details"):
                g_details = ", ".join([f"{g['player']} {g['elapsed']}' ({g['team']})" for g in f["goals_details"]])
                lines.append(f"    Goals scored: {g_details}")
            if f.get("cards_details"):
                c_details = ", ".join([f"{c['player']} {c['elapsed']}' ({c['team']}: {c['detail']})" for c in f["cards_details"]])
                lines.append(f"    Cards shown: {c_details}")

    # Stadium specific fixture (if applicable)
    stadium_today = ctx.get("stadium_today_fixtures", [])
    if stadium_today:
        lines.append("\nTODAY'S FIXTURE AT CURRENT STADIUM:")
        for f in stadium_today:
            lines.append(
                f"  - {f['teams']['home']} vs {f['teams']['away']} | "
                f"Kickoff: {f['time']} | Status: {f['status']} | Score: {f['score']['home']}-{f['score']['away']}"
            )
            
    # Live matches
    live = ctx.get("live_matches", [])
    if live:
        lines.append("\nLIVE MATCHES:")
        for f in live:
            lines.append(f"  - {f['teams']['home']} vs {f['teams']['away']} ({f['elapsed_minutes']} mins elapsed) | Score: {f['score']['home']}-{f['score']['away']}")

    # Completed Matches (past results)
    completed = ctx.get("completed_matches", [])
    if completed:
        lines.append("\nCOMPLETED MATCH RESULTS:")
        for f in completed:
            lines.append(f"  - {f['teams']['home']} vs {f['teams']['away']} | Final Score: {f['score']['home']}-{f['score']['away']}")

    # Upcoming Matches
    upcoming = ctx.get("upcoming_matches", [])
    if upcoming:
        lines.append("\nUPCOMING SCHEDULE:")
        for f in upcoming[:8]:
            lines.append(f"  - {f['date']} {f['time']} | {f['teams']['home']} vs {f['teams']['away']} at {f['venue']['name']}")
            
    return "\n".join(lines)

