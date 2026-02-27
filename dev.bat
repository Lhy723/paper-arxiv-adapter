@echo off
echo Starting ArXiv Paper Adapter Dev Servers...
echo.

echo Starting Backend (port 8000)...
start "Backend" cmd /k "cd /d %~dp0web\backend && uv run uvicorn main:app --reload --port 8000"

echo Starting Frontend (port 5173)...
start "Frontend" cmd /k "cd /d %~dp0web\frontend && npm run dev"

echo.
echo Dev servers started!
echo Frontend: http://localhost:5173
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close this window will NOT stop servers.
echo Close the Backend/Frontend windows to stop them.
pause
