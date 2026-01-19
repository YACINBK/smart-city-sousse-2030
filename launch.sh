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

# Activate environment or install
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run migrations to be sure
echo -e "${BLUE}Checking database...${NC}"
python manage.py makemigrations
python manage.py migrate

# Start Backend
echo -e "${GREEN}Starting Django Backend (Port 8000)...${NC}"
# Use nohup to separate output/process slightly, but we want to kill them later
python manage.py runserver 0.0.0.0:8000 > backend.log 2>&1 &
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
python simulate_realtime.py > simulation.log 2>&1 &
SIM_PID=$!

# Start Dashboard
echo -e "${GREEN}Starting Dashboard (Port 8501)...${NC}"
streamlit run dashboard.py --server.headless true > dashboard.log 2>&1 &
DASH_PID=$!

echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${GREEN}✅ SYSTEM LAUNCHED SUCCESSFULLY${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "Backend PID: $BACKEND_PID"
echo -e "Simulation PID: $SIM_PID"
echo -e "Dashboard PID: $DASH_PID"
echo -e ""
echo -e "📊 ACCESS DASHBOARD HERE: ${GREEN}http://localhost:8501${NC}"
echo -e ""
echo -e "${RED}⚠️  DO NOT CLOSE THIS TERMINAL!${NC}"
echo -e "Press Ctrl+C to stop all services."
echo -e "${BLUE}----------------------------------------${NC}"

# Logs tailing (optional, helps user see if something crashes)
# tail -f dashboard.log &

# Trap for cleanup
trap "kill $BACKEND_PID $SIM_PID $DASH_PID; exit" SIGINT SIGTERM

# Keep script running
wait
