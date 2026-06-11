#!/bin/bash
# Nero AI Framework - Start Script (Linux/Mac)
# Usage: ./start.sh [backend|frontend|both|docker]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 nicht gefunden. Bitte installieren Sie Python3."
        exit 1
    fi
    print_success "Python3 gefunden: $(python3 --version)"
}

# Check Node
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js nicht gefunden. Bitte installieren Sie Node.js."
        exit 1
    fi
    print_success "Node.js gefunden: $(node --version)"
}

# Start Backend
start_backend() {
    print_header "Starte Backend Service"
    
    check_python
    
    cd backend
    
    # Create temp directory
    mkdir -p temp logs
    
    print_info "Aktiviere optimierte Backend-Dateien..."
    if [ -f "omni_engine_optimized.py" ]; then
        cp omni_engine_optimized.py omni_engine.py
        cp main_optimized.py main.py
        print_success "Optimierte Dateien aktiviert"
    fi
    
    # Check if requirements installed
    if ! python3 -c "import fastapi" 2>/dev/null; then
        print_info "Installiere Python-Abhängigkeiten..."
        pip install -r requirements.txt
    fi
    
    print_info "Starte Uvicorn Server..."
    python3 -m uvicorn main:app \
        --host 127.0.0.1 \
        --port 8000 \
        --reload \
        --log-level info
}

# Start Frontend
start_frontend() {
    print_header "Starte Frontend Service"
    
    check_node
    
    cd frontend
    
    print_info "Aktiviere optimierte Frontend-Dateien..."
    if [ -f "src/App_optimized.jsx" ]; then
        cp src/App_optimized.jsx src/App.jsx
        cp src/index_optimized.css src/index.css
        print_success "Optimierte Dateien aktiviert"
    fi
    
    # Check if dependencies installed
    if [ ! -d "node_modules" ]; then
        print_info "Installiere Node-Abhängigkeiten..."
        npm install
    fi
    
    print_info "Starte Vite Dev Server..."
    npm run dev
}

# Start Both (in background)
start_both() {
    print_header "Starte Nero AI Framework"
    
    # Create output directory
    mkdir -p logs
    
    # Start Backend
    print_info "Starte Backend im Hintergrund..."
    cd backend
    python3 -m uvicorn main:app \
        --host 127.0.0.1 \
        --port 8000 \
        --log-level info > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    print_success "Backend gestartet (PID: $BACKEND_PID)"
    
    cd ..
    
    # Wait for backend to be ready
    print_info "Warte auf Backend-Ready..."
    sleep 5
    
    # Check backend health
    if curl -s http://localhost:8000/api/health > /dev/null; then
        print_success "Backend ist bereit"
    else
        print_error "Backend konnte nicht gestartet werden"
        kill $BACKEND_PID
        exit 1
    fi
    
    # Start Frontend
    print_info "Starte Frontend im Hintergrund..."
    cd frontend
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    print_success "Frontend gestartet (PID: $FRONTEND_PID)"
    
    cd ..
    
    print_header "✓ Nero AI läuft!"
    print_success "Backend: http://127.0.0.1:8000"
    print_success "Frontend: http://localhost:5173"
    print_success "Backend Log: ./logs/backend.log"
    print_success "Frontend Log: ./logs/frontend.log"
    print_info "Zum Beenden: ./stop.sh"
    
    # Keep script running
    wait
}

# Start Docker
start_docker() {
    print_header "Starte Docker Container"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker nicht gefunden. Bitte installieren Sie Docker."
        exit 1
    fi
    
    print_info "Baue Docker Image..."
    docker build -t nero-ai:latest .
    print_success "Docker Image gebaut"
    
    print_info "Starte Docker Container..."
    docker-compose up -d
    print_success "Docker Container gestartet"
    
    print_info "Warte auf Container-Ready..."
    sleep 10
    
    if docker ps | grep nero-backend > /dev/null; then
        print_success "Backend Container läuft"
        print_success "Backend: http://localhost:8000"
        print_success "Logs: docker-compose logs -f"
    else
        print_error "Backend Container konnte nicht gestartet werden"
        exit 1
    fi
}

# Main
main() {
    MODE=${1:-both}
    
    case $MODE in
        backend)
            start_backend
            ;;
        frontend)
            start_frontend
            ;;
        both)
            start_both
            ;;
        docker)
            start_docker
            ;;
        *)
            print_error "Unbekannter Modus: $MODE"
            echo "Verwendung: $0 [backend|frontend|both|docker]"
            exit 1
            ;;
    esac
}

# Run
main "$@"
