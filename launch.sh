#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Smart City Sousse 2030 Launcher ===${NC}"

# Check for cleanup argument
CLEANUP_ONLY=false
if [ "$1" == "clean" ]; then
    CLEANUP_ONLY=true
fi

# Cleanup function
cleanup() {
    echo -e "${RED}Stopping all services...${NC}"
    # Find and kill our specific processes
    pkill -f "manage.py runserver"
    pkill -f "simulate_realtime.py"
    pkill -f "streamlit run dashboard.py"
    echo -e "${BLUE}Cleanup complete.${NC}"
}

# Perform cleanup of previous instances
cleanup

if [ "$CLEANUP_ONLY" = true ]; then
    exit 0
fi

# Resolve virtual environment binaries explicitly instead of relying on PATH.
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

PYTHON_BIN="$(pwd)/venv/bin/python"
PIP_BIN="$(pwd)/venv/bin/pip"

if [ ! -x "$PYTHON_BIN" ]; then
    echo -e "${RED}Virtual environment Python not found at $PYTHON_BIN${NC}"
    exit 1
fi

if [ ! -x "$PIP_BIN" ]; then
    echo -e "${BLUE}Installing dependencies...${NC}"
    "$PIP_BIN" install -r requirements.txt
fi

# Run migrations to be sure
echo -e "${BLUE}Checking database...${NC}"
"$PYTHON_BIN" manage.py migrate

# Start Backend
echo -e "${GREEN}Starting Django Backend (Port 8000)...${NC}"
# Use nohup to separate output/process slightly, but we want to kill them later
"$PYTHON_BIN" manage.py runserver 0.0.0.0:8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo -n "Waiting for backend..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:8000/api/ > /dev/null; then
        echo " Ready!"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Start Simulation
echo -e "${GREEN}Starting Simulation...${NC}"
"$PYTHON_BIN" simulate_realtime.py > simulation.log 2>&1 &
SIM_PID=$!

# Start Dashboard
echo -e "${GREEN}Starting Dashboard (Port 8501)...${NC}"
"$PYTHON_BIN" -m streamlit run dashboard.py --server.headless true > dashboard.log 2>&1 &
DASH_PID=$!

echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${GREEN}SYSTEM LAUNCHED SUCCESSFULLY${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "Backend PID: $BACKEND_PID"
echo -e "Simulation PID: $SIM_PID"
echo -e "Dashboard PID: $DASH_PID"
echo -e ""
echo -e "Dashboard: ${GREEN}http://localhost:8501${NC}"
echo -e ""
echo -e "${RED}Do not close this terminal if you want the services to keep running.${NC}"
echo -e "Press Ctrl+C to stop all services."
echo -e "${BLUE}----------------------------------------${NC}"

# Logs tailing (optional, helps user see if something crashes)
# tail -f dashboard.log &

# Trap for cleanup
trap "kill $BACKEND_PID $SIM_PID $DASH_PID; exit" SIGINT SIGTERM

# Keep script running
wait
