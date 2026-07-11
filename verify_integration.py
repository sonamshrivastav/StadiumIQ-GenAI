import os
import sys
import time
import asyncio
from datetime import datetime

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weather_football_service import (
    get_weather_data, get_football_data,
    should_fetch_weather, should_fetch_football
)
from tools import get_stadium_weather, get_stadium_match_data
from unified_agent import run_chat_query

def test_classifiers():
    print("\n--- 1. Testing Intelligent Classifiers ---")
    test_queries = [
        ("Will it rain during today's match?", True, True),
        ("Who is playing today?", False, True),
        ("Which exit should I take if rain starts?", True, True),
        ("What's the current score?", False, True),
        ("How long until kickoff?", False, True),
        ("Where is the nearest food court?", False, True),
        ("Where is the nearest recycling station?", False, False),
        ("Calculate carbon footprint for 20km driving", False, False),
        ("Which teams remain in the tournament?", False, True),
        ("Who can still qualify from Group A?", False, True),
        ("Which teams will reach the final?", False, True)
    ]
    
    passed = True
    for query, expected_weather, expected_football in test_queries:
        w_res = should_fetch_weather(query)
        f_res = should_fetch_football(query)
        w_ok = (w_res == expected_weather)
        f_ok = (f_res == expected_football)
        print(f"Query: '{query}'")
        print(f"  Weather trigger: expected={expected_weather}, got={w_res} [{'PASS' if w_ok else 'FAIL'}]")
        print(f"  Football trigger: expected={expected_football}, got={f_res} [{'PASS' if f_ok else 'FAIL'}]")
        if not w_ok or not f_ok:
            passed = False
            
    return passed

def test_weather_retribution():
    print("\n--- 2. Testing Weather Data Retrieval (Open-Meteo) ---")
    stadiums_to_test = ["metlife", "sofi"]
    passed = True
    for sid in stadiums_to_test:
        print(f"Fetching weather for: {sid}")
        start_time = time.time()
        w_data = get_stadium_weather(sid)
        elapsed = time.time() - start_time
        
        if "error" in w_data:
            print(f"  FAILED to fetch weather: {w_data}")
            passed = False
            continue
            
        print(f"  Result: temp={w_data.get('temperature')}, cond={w_data.get('condition')}, rain={w_data.get('rain_probability')}")
        print(f"  Fetch took {elapsed:.2f}s")
        
        # Test Cache hit
        start_time = time.time()
        w_data_cached = get_stadium_weather(sid)
        elapsed_cached = time.time() - start_time
        print(f"  Cached fetch took {elapsed_cached:.4f}s (Cache Hit: {elapsed_cached < 0.01})")
            
    return passed

def test_football_retribution():
    print("\n--- 3. Testing Football Data Retrieval & Dynamic Standings ---")
    start_time = time.time()
    f_data = get_stadium_match_data("metlife")
    elapsed = time.time() - start_time
    
    print(f"Data source: {f_data.get('data_source')}")
    print(f"Tournament Name: {f_data.get('tournament_name')}")
    print(f"Tournament Stage: {f_data.get('current_tournament_stage')}")
    print(f"Remaining Teams count: {len(f_data.get('remaining_teams', []))}")
    print(f"Today Fixtures count: {len(f_data.get('today_fixtures', []))}")
    print(f"Live Matches count: {len(f_data.get('live_matches', []))}")
    
    # Check standings tables
    standings = f_data.get("group_standings", {})
    print(f"Group Standings keys: {list(standings.keys())}")
    for group_name, list_stats in list(standings.items())[:2]:
        print(f"  {group_name} leader: {list_stats[0]['team']} ({list_stats[0]['points']} pts, GD: {list_stats[0]['goal_difference']})")
        
    print(f"Fetch took {elapsed:.2f}s")
    
    # Verify structured fields
    required_fields = ["tournament_name", "current_tournament_stage", "remaining_teams", "group_standings", "today_fixtures"]
    fields_ok = all(field in f_data for field in required_fields)
    print(f"Structured fields check: {'PASS' if fields_ok else 'FAIL'}")
    
    return fields_ok

async def test_agent_pipeline():
    print("\n--- 4. Testing Unified Agent Integration & Reasoning ---")
    
    queries = [
        "Will it rain during today's match at MetLife Stadium?",
        "Which teams remain in the tournament?",
        "Who can still qualify?",
        "Which teams will reach the final?"
    ]
    
    session_id = f"test-session-{int(time.time())}"
    passed = True
    
    forbidden_phrases = [
        "live data shows",
        "according to the api",
        "i don't have standings",
        "do not have standings",
        "api shows",
        "the database says"
    ]
    
    for query in queries:
        print(f"\nSending Query: '{query}'")
        try:
            start_time = time.time()
            reply, agent = await run_chat_query(
                session_id=session_id,
                message=query,
                stadium_id="metlife",
                language="en"
            )
            elapsed = time.time() - start_time
            print(f"Agent used: [{agent}]")
            print(f"Response: {reply}")
            print(f"Query completed in {elapsed:.2f}s")
            
            # Check for forbidden phrases
            found_forbidden = False
            for phrase in forbidden_phrases:
                if phrase in reply.lower():
                    print(f"  🔴 WARNING: Response contains forbidden phrase: '{phrase}'")
                    found_forbidden = True
            
            if found_forbidden:
                passed = False
                print("  [FAIL] Response exposed implementation details or API wording.")
            else:
                print("  [PASS] Response is natural and does not leak backend details.")
                
        except Exception as e:
            print(f"FAILED Agent query: {e}")
            import traceback
            traceback.print_exc()
            passed = False
            
    return passed

async def main():
    print("====================================================")
    print(" Starting StadiumQ Football Reasoning Tests")
    print("====================================================")
    
    classifiers_ok = test_classifiers()
    weather_ok = test_weather_retribution()
    football_ok = test_football_retribution()
    agent_ok = await test_agent_pipeline()
    
    print("\n====================================================")
    print(" SUMMARY OF TEST RESULTS")
    print("====================================================")
    print(f"1. Classifiers: {'✅ PASSED' if classifiers_ok else '❌ FAILED'}")
    print(f"2. Weather Service: {'✅ PASSED' if weather_ok else '❌ FAILED'}")
    print(f"3. Football Service: {'✅ PASSED' if football_ok else '❌ FAILED'}")
    print(f"4. Unified Agent Pipeline: {'✅ PASSED' if agent_ok else '❌ FAILED'}")
    print("====================================================")
    
    if classifiers_ok and weather_ok and football_ok and agent_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
