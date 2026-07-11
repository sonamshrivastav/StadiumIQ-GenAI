@echo off
echo ================================================
echo  StadiumIQ - FIFA World Cup 2026 Command Center
echo ================================================
echo.

echo [1/2] Starting Backend (FastAPI + GenAI SDK)...
start "StadiumIQ Backend" cmd /k "cd /d %~dp0 && python -m uvicorn main:app --reload --port 8000"

echo [2/2] Starting Frontend (Vite + React)...
timeout /t 3 >nul
start "StadiumIQ Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ================================================
echo  Backend: http://localhost:8000
echo  Frontend: http://localhost:5173
echo  API Docs: http://localhost:8000/docs
echo ================================================
echo.
echo Press any key to close this window...
pause >nul
