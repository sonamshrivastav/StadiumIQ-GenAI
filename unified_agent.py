import os
import re
import time
import random
import asyncio
import sqlite3
import threading
import sys
from collections import OrderedDict
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from data import STADIUMS
from tools import (
    get_stadium_info, find_nearest_facility, get_match_schedule,
    check_crowd_density, suggest_best_exit, predict_congestion,
    get_accessible_route, find_sensory_room, request_companion_assistance,
    get_transit_options, estimate_travel_time, find_parking,
    calculate_carbon_footprint, find_recycling_station, get_sustainability_score,
    report_incident, get_active_incidents, assign_staff_task, get_staff_overview,
    get_stadium_weather, get_stadium_match_data,
)
from weather_football_service import should_fetch_weather, should_fetch_football, format_weather_context, format_football_context

# ──────────────────────────────────────────────
# GEMINI CLIENT INITIALIZATION
# ──────────────────────────────────────────────

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# ──────────────────────────────────────────────
# SYSTEM INSTRUCTIONS & PERSONAS
# ──────────────────────────────────────────────

SYSTEM_INSTRUCTION = """You are StadiumIQ, the unified AI-powered command center and operations concierge for the FIFA World Cup 2026. You act as a seamless interface coordinating six operational personas: Fan Services, Crowd Intelligence, Accessibility Concierge, Transit & Transport, Sustainability Hub, and Operations Management.

Based on the user's message, you must adopt the most relevant persona, call appropriate tools, and respond in the appropriate tone.

PERSONAS & INSTRUCTIONS:
1. [fan_assistant] (Fan Services):
   - Helps fans with stadium navigation, finding facilities (food, restrooms, medical, exits), match schedules.
   - Tone: Enthusiastic, welcoming.
   - If the user writes in a non-English language, respond in their language.
   - Use tools to get real facility locations. List the name, section, distance, walk time, and status.
   
2. [crowd_agent] (Crowd Intelligence):
   - Monitors crowd density, recommends best exits, predicts congestion.
   - Tone: Direct, analytical, actionable.
   - Use indicators: 🟢 Low (<40%), 🟡 Moderate (40-65%), 🟠 High (65-85%), 🔴 Critical (>85%).
   - Proactively suggest less crowded exits/gates to optimize fan flow.

3. [accessibility_agent] (Accessibility Concierge):
   - Wheelchair routes, sensory rooms, volunteer companion requests.
   - Tone: Warm, patient, highly respectful.
   - Provide clear, numbered step-by-step directions with elevator/ramp details.

4. [transit_agent] (Transit & Transport):
   - Driving, transit options, shuttle routes, parking lots, travel times.
   - Tone: Informative, practical.
   - Recommend free shuttles and public transit first to avoid congestion.

5. [sustainability_agent] (Sustainability Hub):
   - Carbon calculations, recycling guides, eco initiatives.
   - Tone: Positive, eco-conscious, encouraging.
   - Provide carbon ratings and helpful tips to reduce waste.

6. [ops_agent] (Operations Management):
   - Incident reporting, staff tasks, maintenance, security logs.
   - Tone: Professional, crisp, efficient.
   - Always confirm incident logging with an incident ID, location, and assigned responder.

CRITICAL INSTRUCTIONS:
- You MUST begin your final answer with the active agent tag in square brackets, e.g., '[fan_assistant]', '[crowd_agent]', '[accessibility_agent]', '[transit_agent]', '[sustainability_agent]', or '[ops_agent]'. Followed by a single space, then your response. For example: `[transit_agent] The transit options for MetLife Stadium include...`
- NEVER make up data. If a tool call is needed, call it.
- Keep responses relatively concise and focused on action.
"""

# ──────────────────────────────────────────────
# TOOL DEFINITIONS & MAPPINGS
# ──────────────────────────────────────────────

TOOL_MAP = {
    "get_stadium_info": get_stadium_info,
    "find_nearest_facility": find_nearest_facility,
    "get_match_schedule": get_match_schedule,
    "check_crowd_density": check_crowd_density,
    "suggest_best_exit": suggest_best_exit,
    "predict_congestion": predict_congestion,
    "get_accessible_route": get_accessible_route,
    "find_sensory_room": find_sensory_room,
    "request_companion_assistance": request_companion_assistance,
    "get_transit_options": get_transit_options,
    "estimate_travel_time": estimate_travel_time,
    "find_parking": find_parking,
    "calculate_carbon_footprint": calculate_carbon_footprint,
    "find_recycling_station": find_recycling_station,
    "get_sustainability_score": get_sustainability_score,
    "report_incident": report_incident,
    "get_active_incidents": get_active_incidents,
    "assign_staff_task": assign_staff_task,
    "get_staff_overview": get_staff_overview,
    "get_stadium_weather": get_stadium_weather,
    "get_stadium_match_data": get_stadium_match_data,
}

TOOL_AGENT_MAP = {
    "get_stadium_info": "fan_assistant",
    "find_nearest_facility": "fan_assistant",
    "get_match_schedule": "fan_assistant",
    "check_crowd_density": "crowd_agent",
    "suggest_best_exit": "crowd_agent",
    "predict_congestion": "crowd_agent",
    "get_accessible_route": "accessibility_agent",
    "find_sensory_room": "accessibility_agent",
    "request_companion_assistance": "accessibility_agent",
    "get_transit_options": "transit_agent",
    "estimate_travel_time": "transit_agent",
    "find_parking": "transit_agent",
    "calculate_carbon_footprint": "sustainability_agent",
    "find_recycling_station": "sustainability_agent",
    "get_sustainability_score": "sustainability_agent",
    "report_incident": "ops_agent",
    "get_active_incidents": "ops_agent",
    "assign_staff_task": "ops_agent",
    "get_staff_overview": "ops_agent",
    "get_stadium_weather": "fan_assistant",
    "get_stadium_match_data": "fan_assistant"
}

# ──────────────────────────────────────────────
# PERSISTENT SQLITE CHAT HISTORY MANAGER
# ──────────────────────────────────────────────

DB_PATH = os.path.join(BASE_DIR, "sqlite_chat_history.db")

class SQLiteChatHistoryManager:
    """Thread-safe SQLite persistent store for conversational context."""
    def __init__(self, db_path: str = DB_PATH, max_turns: int = 4):
        self.db_path = db_path
        self.max_turns = max_turns
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    session_id TEXT,
                    role TEXT,
                    text_content TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()
            conn.close()

    def get_history(self, session_id: str) -> list[types.Content]:
        """Loads and formats the last 8 messages (4 turns) as types.Content objects."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            max_messages = self.max_turns * 2
            cursor.execute("""
                SELECT role, text_content FROM (
                    SELECT role, text_content, timestamp 
                    FROM chat_history 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ) ORDER BY timestamp ASC
            """, (session_id, max_messages))
            rows = cursor.fetchall()
            conn.close()

        contents = []
        for role, text in rows:
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=text)]
                )
            )
        return contents

    def add_message(self, session_id: str, role: str, text: str):
        """Adds a message to the persistent store."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (session_id, role, text_content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, role, text, time.time()))
            conn.commit()
            conn.close()


history_manager = SQLiteChatHistoryManager()

# ──────────────────────────────────────────────
# IN-MEMORY CACHE (EXACT MATCH & NORMALIZATION)
# ──────────────────────────────────────────────

class SimpleNormalizedCache:
    """Key-normalized query cache to prevent repeat API calls."""
    def __init__(self, ttl: int = 120, max_size: int = 100):
        self.ttl = ttl
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def _normalize_key(self, stadium_id: str, language: str, message: str) -> str:
        msg = message.lower().strip()
        msg = re.sub(r'\s+', ' ', msg)
        msg = re.sub(r'[?.!]+$', '', msg)
        return f"{stadium_id}:{language}:{msg}"

    def get(self, stadium_id: str, language: str, message: str) -> tuple:
        key = self._normalize_key(stadium_id, language, message)
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    self.cache.move_to_end(key)
                    return value
                else:
                    del self.cache[key]
            return None

    def set(self, stadium_id: str, language: str, message: str, value: tuple):
        key = self._normalize_key(stadium_id, language, message)
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            self.cache[key] = (value, time.time())


cache_manager = SimpleNormalizedCache()

# ──────────────────────────────────────────────
# MULTI-PROVIDER LLM FALLBACK HANDLERS
# ──────────────────────────────────────────────


def map_history_to_openai_messages(history: list, new_user_message: str, system_instruction: str = None) -> list:
    """Converts a list of types.Content history and a new user message into OpenAI format."""
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
        
    for content in history:
        role = "user" if content.role == "user" else "assistant"
        text = ""
        for part in content.parts:
            if hasattr(part, "text") and part.text:
                text += part.text
        messages.append({"role": role, "content": text})
        
    messages.append({"role": "user", "content": new_user_message})
    return messages


def execute_groq_generation(messages: list, timeout: float = 10.0) -> str:
    """Executes a synchronous call to the Groq API over REST."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not defined in the environment.")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.2
    }
    
    import urllib.request
    import json
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=timeout) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        return res_data["choices"][0]["message"]["content"]


def execute_openrouter_generation(messages: list, timeout: float = 10.0) -> str:
    """Executes a synchronous call to the OpenRouter API over REST."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not defined in the environment.")
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "StadiumIQ"
    }
    model = os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2
    }
    
    import urllib.request
    import json
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=timeout) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        return res_data["choices"][0]["message"]["content"]
# ──────────────────────────────────────────────
# NATIVE ASYNC CLIENT INTERACTION & RETRIES
# ──────────────────────────────────────────────

async def execute_content_generation_async(contents, config, retries: int = 3, base_delay: float = 2.0):
    """Executes a non-blocking asynchronous call to Gemini with backoff retries."""
    for attempt in range(retries):
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config
            )
            return response
        except Exception as e:
            err_msg = str(e)
            is_rate_limit = "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower()
            if is_rate_limit and attempt < retries - 1:
                delay = (base_delay ** attempt) + random.uniform(0.5, 1.5)
                print(f"[AsyncUnifiedAgent] Rate limited. Retrying in {delay:.2f}s... (Attempt {attempt+1}/{retries})")
                await asyncio.sleep(delay)
            else:
                raise e

def parse_agent_response(reply_text: str, default_agent: str = "fan_assistant") -> tuple[str, str]:
    """Extract agent_name from square brackets prefix and return clean message."""
    if not reply_text:
        return default_agent, ""
        
    reply_text = reply_text.strip()
    match = re.match(r'^(?:\*\*|)?\[([a-zA-Z0-9_]+)\](?:\*\*|)?\s*(.*)$', reply_text, re.DOTALL)
    if match:
        agent_name = match.group(1).strip()
        clean_reply = match.group(2).strip()
        
        valid_agents = {"fan_assistant", "crowd_agent", "accessibility_agent", "transit_agent", "sustainability_agent", "ops_agent"}
        if agent_name in valid_agents:
            return agent_name, clean_reply
            
    return default_agent, reply_text


def get_agent_for_tool(tool_name: str) -> str:
    """Map tool name to its respective specialized agent category."""
    return TOOL_AGENT_MAP.get(tool_name, "fan_assistant")


# ──────────────────────────────────────────────
# TOOL OUTPUT TRUNCATION LAYER
# ──────────────────────────────────────────────

def truncate_tool_response(tool_name: str, raw_output: dict) -> dict:
    """Filters massive tool payloads to save token limits under model context."""
    if not isinstance(raw_output, dict):
        return raw_output
        
    if tool_name == "get_stadium_info":
        return {
            "name": raw_output.get("name"),
            "city": raw_output.get("city"),
            "capacity": raw_output.get("capacity"),
            "facility_types": raw_output.get("facility_types")
        }
    return raw_output

# ──────────────────────────────────────────────
# MAIN EXPOSURE ENTRY POINT
# ──────────────────────────────────────────────

def sanitize_user_input(message: str) -> str:
    """Sanitizes user input to protect against HTML elements and prompt injection."""
    if not message:
        return ""
        
    # Strip HTML tags
    clean = re.sub(r'<[^>]*>', '', message)
    
    # Redact common prompt injection keywords case-insensitively
    injection_patterns = [
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"system\s+override",
        r"you\s+must\s+now\s+act\s+as",
        r"bypass\s+restrictions",
        r"new\s+system\s+prompt"
    ]
    
    for pattern in injection_patterns:
        clean = re.sub(pattern, "[REDACTED INJECTION ATTEMPT]", clean, flags=re.IGNORECASE)
        
    return clean


async def run_chat_query(session_id: str, message: str, stadium_id: str, language: str) -> tuple[str, str]:
    """Main executor pipeline incorporating cache, persistent SQL memory, and LLM providers cascade."""
    # Step 0: Sanitize user input against HTML and injections
    message = sanitize_user_input(message)
    
    # Safe message string for console logging on Windows
    safe_log_msg = message[:30].encode('ascii', errors='replace').decode('ascii')
    
    # Step 1: Check cache
    cached = cache_manager.get(stadium_id, language, message)
    if cached:
        print(f"[AsyncUnifiedAgent] Cache hit for query: '{safe_log_msg}...'")
        return cached

    # API Keys configurations check
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")

    if not gemini_key and not groq_key and not openrouter_key:
        err_msg = (
            "[fan_assistant] ⚠️ Configuration Error: No AI API keys are configured. "
            "Please configure GEMINI_API_KEY, GROQ_API_KEY, and OPENROUTER_API_KEY in your .env file."
        )
        return err_msg, "fan_assistant"

    # Step 2: Load persistent session histories
    history = history_manager.get_history(session_id)
    
    # Fetch real live data from database/tools for Context Injection fallback
    stadium_name = STADIUMS.get(stadium_id, {}).get("name", "MetLife Stadium")
    
    live_weather = None
    live_football = None
    
    # Conditional loading of Open-Meteo and API-Football data sources
    if should_fetch_weather(message):
        try:
            live_weather = get_stadium_weather(stadium_id)
        except Exception as weather_err:
            print(f"[AsyncUnifiedAgent] Weather gathering failed: {weather_err}")
            
    if should_fetch_football(message):
        try:
            live_football = get_stadium_match_data(stadium_id)
        except Exception as football_err:
            print(f"[AsyncUnifiedAgent] Football gathering failed: {football_err}")

    try:
        live_crowd = check_crowd_density(stadium_id)
        live_matches = get_match_schedule(stadium_id)
        live_incidents = get_active_incidents(stadium_id)
        nearest_restroom = find_nearest_facility(stadium_id, "restroom")
        nearest_food = find_nearest_facility(stadium_id, "food")
        nearest_medical = find_nearest_facility(stadium_id, "medical")
        stadium_info = get_stadium_info(stadium_id)
    except Exception as ctx_err:
        print(f"[AsyncUnifiedAgent] Context gathering failed: {ctx_err}")
        live_crowd = live_matches = live_incidents = nearest_restroom = nearest_food = nearest_medical = stadium_info = {}

    weather_str = format_weather_context(live_weather) if live_weather else ""
    football_str = format_football_context(live_football, stadium_id) if live_football else ""

    context_prompt = (
        f"--- LIVE STADIUM DATA FOR {stadium_name.upper()} ---\n"
        f"Stadium Info: {stadium_info}\n"
        f"Live Crowd Densities: {live_crowd}\n"
        f"Upcoming Matches: {live_matches}\n"
        f"Active Incidents: {live_incidents}\n"
        f"Nearest Restrooms: {nearest_restroom}\n"
        f"Nearest Food Concessions: {nearest_food}\n"
        f"Nearest Medical Aid Stations: {nearest_medical}\n"
        f"\n{weather_str}\n"
        f"\n{football_str}\n"
        f"-----------------------------------------------\n"
        f"INSTRUCTION FOR OPERATIONAL INTELLIGENCE & PERSONA:\n"
        f"- You are StadiumIQ, a helpful and natural stadium AI assistant. Respond naturally and professionally, maintaining your persona.\n"
        f"- Never expose backend details or implementation phrasing. Never say 'The live data shows...', 'According to the API...', or 'I don't have access to standings.'\n"
        f"- If asked about standings, who is remaining in the tournament, or qualification scenarios, reason mathematically and logically over the standing tables and fixture details provided in the context above. For example, if a team has won all matches, describe their strong position. If multiple games are left and points are close, explain what points are needed to qualify.\n"
        f"- If a question cannot be answered deterministically from the provided standings/context (e.g., 'Which teams will reach the final?'), explain why logically (e.g. explain that we are currently in the Group Stage with many matches remaining, so final matchups are not yet determined, but highlight current group leaders) instead of giving irrelevant guess work or generic data warnings.\n"
        f"- Intelligently combine all available contexts (telemetry, weather, match state). For example, if a match is ending and rain is occurring or forecast, direct fans to specific, covered, and less congested exits, recommending public transport first to save time and reduce carbon footprint.\n"
        f"Adopt the correct operational persona from your system instructions. "
        f"Answer the user's query in their language using the live data above. "
        f"Be precise, professional, and friendly. User Language: {language}.\n\n"
        f"User message: {message}"
    )

    # Incorporate context prefix for primary provider (Gemini)
    context_prefix = f"[Current stadium context: {stadium_name} (stadium_id: {stadium_id}). User language: {language}] "
    full_message = context_prefix + message
    
    user_content = types.Content(
        role="user",
        parts=[types.Part(text=full_message)]
    )
    
    temp_contents = list(history) + [user_content]
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=list(TOOL_MAP.values()),
        temperature=0.2,
    )
    
    force_failure = os.environ.get("FORCE_PROVIDER_FAILURE", "").lower()
    gemini_failed = "gemini" in force_failure
    groq_failed = "groq" in force_failure

    reply_text = None
    agent_used = "fan_assistant"

    # --- Try Primary Provider: Google Gemini ---
    if not gemini_failed:
        if not gemini_key:
            print("[AsyncUnifiedAgent] Gemini key is missing, cascading to Groq...")
            gemini_failed = True
        else:
            try:
                print("[AsyncUnifiedAgent] Attempting Primary Provider: Google Gemini...")
                response = await execute_content_generation_async(
                    contents=temp_contents,
                    config=config
                )
                
                # Multi-Turn Function Calling Loop
                if response.function_calls:
                    tool_results_parts = []
                    for function_call in response.function_calls:
                        name = function_call.name
                        args = function_call.args
                        
                        print(f"[AsyncUnifiedAgent] Tool call requested: {name}({args})")
                        agent_used = get_agent_for_tool(name)
                        
                        if name in TOOL_MAP:
                            try:
                                result = TOOL_MAP[name](**args)
                                result = truncate_tool_response(name, result)
                            except Exception as ex:
                                result = {"error": f"Failed to execute tool {name}: {str(ex)}"}
                        else:
                            result = {"error": f"Tool {name} not found"}
                        
                        tool_results_parts.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=name,
                                    response={"result": result}
                                )
                            )
                        )
                    
                    # Pack model call details & function response payload
                    model_request_content = types.Content(
                        role="model",
                        parts=response.candidates[0].content.parts
                    )
                    tool_response_content = types.Content(
                        role="tool",
                        parts=tool_results_parts
                    )
                    
                    temp_contents.append(model_request_content)
                    temp_contents.append(tool_response_content)
                    
                    # Second async call to obtain formatted response
                    final_response_obj = await execute_content_generation_async(
                        contents=temp_contents,
                        config=config
                    )
                    reply_text = final_response_obj.text
                else:
                    # Direct response text
                    reply_text = response.text
                    
            except Exception as e:
                print(f"[AsyncUnifiedAgent] Primary Provider Gemini failed: {e}")
                gemini_failed = True

    # --- Try Secondary Fallback Provider: Groq ---
    if gemini_failed and not groq_failed:
        if not groq_key:
            print("[AsyncUnifiedAgent] Groq key is missing, cascading to OpenRouter...")
            groq_failed = True
        else:
            try:
                print("[AsyncUnifiedAgent] Attempting Fallback Provider 1: Groq API...")
                openai_messages = map_history_to_openai_messages(history, context_prompt, SYSTEM_INSTRUCTION)
                reply_text = await asyncio.to_thread(execute_groq_generation, openai_messages)
                print(f"[AsyncUnifiedAgent] Fallback Provider 1 Groq succeeded.")
                
            except Exception as e:
                print(f"[AsyncUnifiedAgent] Fallback Provider 1 Groq failed: {e}")
                groq_failed = True

    # --- Try Tertiary Fallback Provider: OpenRouter ---
    if gemini_failed and groq_failed:
        if not openrouter_key:
            print("[AsyncUnifiedAgent] OpenRouter key is missing. All providers exhausted.")
            reply_text = (
                "[fan_assistant] ⚠️ Configuration Error: All configured AI providers failed, "
                "and OpenRouter API key is missing. Please check your API keys."
            )
        else:
            try:
                print("[AsyncUnifiedAgent] Attempting Fallback Provider 2: OpenRouter API...")
                openai_messages = map_history_to_openai_messages(history, context_prompt, SYSTEM_INSTRUCTION)
                reply_text = await asyncio.to_thread(execute_openrouter_generation, openai_messages)
                print(f"[AsyncUnifiedAgent] Fallback Provider 2 OpenRouter succeeded.")
                
            except Exception as e:
                print(f"[AsyncUnifiedAgent] Fallback Provider 2 OpenRouter failed: {e}")
                reply_text = (
                    "[fan_assistant] ⚠️ The AI service is temporarily unavailable. All providers failed to connect. "
                    "Please check your network and configuration keys."
                )

    history_manager.add_message(session_id, "user", message)
    history_manager.add_message(session_id, "model", reply_text)

    # Step 6: Parse bracket agent tag and return
    parsed_agent, clean_reply = parse_agent_response(reply_text, agent_used)
    
    # Store in normalized cache
    cache_manager.set(stadium_id, language, message, (clean_reply, parsed_agent))
    
    return clean_reply, parsed_agent
