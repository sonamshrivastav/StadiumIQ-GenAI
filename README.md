# StadiumQ — FIFA World Cup 2026 AI Command Center

StadiumQ is an AI-powered operational command center and guest concierge designed for the FIFA World Cup 2026. Built for fans, operations staff, and transit planners, the application merges live simulated stadium telemetry (crowd flows, gate queue wait times, parking availability, restroom wait times, incidents) with real-world weather conditions (Open-Meteo) and live football matches, scores, group standings, cards, and goals (API-Football). 

The platform leverages a robust, multi-tier GenAI pipeline that coordinates six specialized AI personas to deliver context-aware stadium navigation, crowd mitigation, and operational safety recommendations.

---

## 📌 Problem Statement
Managing a major tournament like the FIFA World Cup 2026 across 16 different venues presents immense logistics and safety challenges. Operations staff are often siloed from real-time crowd dynamics, and fans struggle with navigating long restroom/concession lines, parking surge rates, transit delays, and weather changes. Isolated weather forecasts or raw sports schedules do not help unless they are combined into **actionable stadium operational intelligence** (e.g. warning fans about an exit gate because a match is ending and heavy rain is starting).

## 💡 Solution
StadiumQ solves this by building an AI-powered console that aggregates:
1. **Simulated Stadium Telemetry**: Live zone occupancy, exit gate wait times, security alerts, queue times.
2. **Real-time Weather Data (Open-Meteo)**: Current temp, rain probability, wind speed, relative humidity, and 3-day forecasts.
3. **Live Football Data (API-Football)**: Real-time match fixtures, live scores, stage progress, goals, cards, and dynamic group standings.
4. **Conversation History**: Short-term persistent session memory.

It feeds this unified context into a specialized AI pipeline that adopts the voice of the most relevant operational persona (Fan Services, Crowd Intelligence, Accessibility Concierge, Transit & Transport, Sustainability Hub, or Operations Management) to generate intelligent recommendations.

---

## 🏗 Architecture Diagram

```mermaid
graph TD
    User([User]) <--> Frontend[React Frontend]
    Frontend <--> Backend[FastAPI Backend]
    
    subgraph Context Gathering
        Telemetry[Simulated Stadium Telemetry] --> Context[AI Prompt Context]
        Weather[Open-Meteo Weather API] --> Context
        Football[API-Football Live Scores API] --> Context
    end

    Backend --> Context
    Context --> AI_Pipeline{AI Router}
    
    subgraph AI Providers
        AI_Pipeline -->|1. Primary| Gemini[Google Gemini 2.5 Flash]
        AI_Pipeline -.->|2. Fallback| Groq[Groq Llama-3.3-70b-versatile]
        AI_Pipeline -.->|3. Cascade Fallback| OpenRouter[OpenRouter Llama-3.3-70b-instruct]
    end

    Gemini --> AgentResponse[Agent Tagged Response]
    Groq --> AgentResponse
    OpenRouter --> AgentResponse
    AgentResponse --> Backend
```

---

## 🔄 AI Workflow (Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    actor User as Fan / Operator
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant Context as Context Injection
    participant Gemini as Google Gemini
    participant Groq as Groq (Fallback 1)
    participant OR as OpenRouter (Fallback 2)

    User->>FE: Type message (e.g. "Will it rain during today's match?")
    FE->>BE: POST /api/chat (message, session_id, stadium_id)
    Note over BE: Classifiers verify intent: weather=True, football=True
    BE->>Context: Load Weather (Open-Meteo) & Matches (API-Football)
    Context-->>BE: Weather + Matches + Telemetry + History
    Note over BE: Construct Context Injected Prompt
    
    alt Gemini Active (No Rate Limits)
        BE->>Gemini: generate_content()
        Gemini-->>BE: Tagged Response (e.g. "[fan_assistant] ...")
    else Gemini Rate Limited (429) / Quota Exhausted
        BE->>Gemini: generate_content() -> Fails
        Note over BE: Initiates Backoff + Cascades to Groq
        alt Groq Active
            BE->>Groq: chat.completions()
            Groq-->>BE: Tagged Response
        else Groq Fails (403/Other)
            BE->>Groq: chat.completions() -> Fails
            Note over BE: Cascades to OpenRouter
            BE->>OR: chat.completions()
            OR-->>BE: Tagged Response
        end
    end
    
    Note over BE: Parse Agent Tag (e.g., [transit_agent])
    BE->>FE: Return clean response & agent info
    FE->>User: Display response with Agent Avatar (e.g. Transit Agent)
```

---

## 🌟 Key Features

* **Multi-Provider AI Fallback Routing**: Guarantees high availability by cascading from Google Gemini to Groq and OpenRouter when rate limits or quotas are hit, maintaining zero chat downtime.
* **Intelligent Query Classifiers**: Only queries weather or football endpoints when the query depends on them, preventing API overhead and reducing token sizes.
* **Live Dynamic Standings**: Computes tournament group stage standings (points, wins, goal differences) in real-time, mapping match updates instantly.
* **Specialized Operational Personas**: Coordinates 6 distinct agent tags (e.g. `[fan_assistant]`, `[crowd_agent]`, `[accessibility_agent]`) depending on the context.
* **Dark Stadium Map visualizer**: Renders facilities, restrooms, entrances, and recycling bins dynamically over real-world coordinates via Leaflet.js.
* **Multilingual Support**: Supports English (`en`), Spanish (`es`), French (`fr`), Arabic (`ar`), and Hindi (`hi`).

---

## 🛠 Technology Stack

* **Frontend**: React (Vite), Leaflet.js Maps, Vanilla CSS.
* **Backend**: FastAPI (Python), Uvicorn server, SQLite3 (persistent chat history).
* **AI Engine**: Google GenAI SDK, REST integrations for Groq and OpenRouter.
* **APIs**: Open-Meteo API (weather), API-Football (v3 fixtures and events).
* **CORS Middleware**: Configured to run on standard localhost development ports (`5173` and `8000`).

---

## 📁 Folder Structure

```
FIFA/
├── weather_football_service.py # Weather/Match fetchers, caches, and standings
├── unified_agent.py           # GenAI cascade routing, system prompts, history
├── tools.py                   # Python tools exposed to primary Gemini model
├── data.py                    # Static stadium coordinate assets & match seeds
├── main.py                    # FastAPI routes, WebSocket telemetry, CORS configs
├── schema.py                  # Pydantic schema validation structures
├── verify_integration.py      # Automated integration verification test suite
├── start.bat                  # Multi-process launch script for local running
└── frontend/                  # React Vite client code
    ├── src/
    │   ├── App.jsx            # Core layout routing
    │   ├── components/        # Sidebar, Header, ChatPanel, StadiumMap, Dashboards
    │   └── utils/api.js       # Client HTTP fetch utilities
    └── package.json
```

---

## 🚀 Installation & Running Locally

### Prerequisites
* Python 3.10+
* Node.js 18+

### 1. Clone the repository and install Backend
From the root directory:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct
FOOTBALL_API_KEY=bf4edbdc9c03e58de50fb413df362def
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Launch the Application
Run the startup script in the root directory:
```cmd
start.bat
```
* **Frontend**: [http://localhost:5173/](http://localhost:5173/)
* **Backend API**: [http://localhost:8000/](http://localhost:8000/)
* **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔮 Future Enhancements
* **3D Indoor Navigation**: Integrate WebGL/Three.js maps for multi-level indoor seat navigation.
* **Live CCTV Anomaly Detection**: Connect local cameras with vision models (e.g. Gemini 2.5 Flash) to report safety incidents or long food court queues automatically.
* **NFC Ticketing and Wallet integration**: Combine digital gates with fan wallet IDs to recommend entrance lanes dynamically.

---

## 📄 License
This project is licensed under the MIT License.
