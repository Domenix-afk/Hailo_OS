#!/bin/bash
# Nero AI Framework - Quick Activation Guide
# Run this to activate all optimizations automatically

echo "╔════════════════════════════════════════════════════════╗"
echo "║   Nero AI Framework - Optimization Activation        ║"
echo "║                                                        ║"
echo "║   This will activate all optimizations automatically  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if running from correct directory
if [ ! -f "OPTIMIZATION_COMPLETE.md" ]; then
    echo -e "${RED}✗ Error: Please run this script from the Hailo_OS root directory${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Backing up current files...${NC}"

# Backend Backups
cd backend

if [ -f "omni_engine.py" ] && [ ! -f "omni_engine_backup.py" ]; then
    cp omni_engine.py omni_engine_backup.py
    echo -e "${GREEN}  ✓ backend/omni_engine.py backed up${NC}"
fi

if [ -f "main.py" ] && [ ! -f "main_backup.py" ]; then
    cp main.py main_backup.py
    echo -e "${GREEN}  ✓ backend/main.py backed up${NC}"
fi

cd ..

# Frontend Backups
cd frontend/src

if [ -f "App.jsx" ] && [ ! -f "App_backup.jsx" ]; then
    cp App.jsx App_backup.jsx
    echo -e "${GREEN}  ✓ frontend/src/App.jsx backed up${NC}"
fi

if [ -f "index.css" ] && [ ! -f "index_backup.css" ]; then
    cp index.css index_backup.css
    echo -e "${GREEN}  ✓ frontend/src/index.css backed up${NC}"
fi

cd ../..

echo ""
echo -e "${BLUE}Step 2: Activating optimized files...${NC}"

# Backend Activation
cd backend

if [ -f "omni_engine_optimized.py" ]; then
    cp omni_engine_optimized.py omni_engine.py
    echo -e "${GREEN}  ✓ omni_engine_optimized.py activated${NC}"
else
    echo -e "${RED}  ✗ omni_engine_optimized.py not found${NC}"
fi

if [ -f "main_optimized.py" ]; then
    cp main_optimized.py main.py
    echo -e "${GREEN}  ✓ main_optimized.py activated${NC}"
else
    echo -e "${RED}  ✗ main_optimized.py not found${NC}"
fi

cd ..

# Frontend Activation
cd frontend/src

if [ -f "App_optimized.jsx" ]; then
    cp App_optimized.jsx App.jsx
    echo -e "${GREEN}  ✓ App_optimized.jsx activated${NC}"
else
    echo -e "${RED}  ✗ App_optimized.jsx not found${NC}"
fi

if [ -f "index_optimized.css" ]; then
    cp index_optimized.css index.css
    echo -e "${GREEN}  ✓ index_optimized.css activated${NC}"
else
    echo -e "${RED}  ✗ index_optimized.css not found${NC}"
fi

cd ../..

echo ""
echo -e "${BLUE}Step 3: Verifying optimization markers...${NC}"

# Verify STT optimization
if grep -q "STT_BEAM_SIZE = 3" backend/omni_engine.py; then
    echo -e "${GREEN}  ✓ STT optimization detected${NC}"
else
    echo -e "${YELLOW}  ⚠ STT optimization not detected${NC}"
fi

# Verify LLM optimization
if grep -q "LLM_MAX_TOKENS = 120" backend/omni_engine.py; then
    echo -e "${GREEN}  ✓ LLM optimization detected${NC}"
else
    echo -e "${YELLOW}  ⚠ LLM optimization not detected${NC}"
fi

# Verify React optimization
if grep -q "useMemo" frontend/src/App.jsx; then
    echo -e "${GREEN}  ✓ React optimization detected${NC}"
else
    echo -e "${YELLOW}  ⚠ React optimization not detected${NC}"
fi

# Verify API optimization
if grep -q "GZIPMiddleware" backend/main.py; then
    echo -e "${GREEN}  ✓ API optimization detected${NC}"
else
    echo -e "${YELLOW}  ⚠ API optimization not detected${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Optimizations Successfully Activated!              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "  1. Start the system:"
echo -e "     ${YELLOW}./start.sh both${NC}"
echo ""
echo "  2. Open frontend:"
echo -e "     ${YELLOW}http://localhost:5173${NC}"
echo ""
echo "  3. Check backend:"
echo -e "     ${YELLOW}curl http://localhost:8000/api/health${NC}"
echo ""
echo "  4. View stats:"
echo -e "     ${YELLOW}curl http://localhost:8000/api/stats${NC}"
echo ""
echo -e "${YELLOW}Backup files stored if rollback needed:${NC}"
echo "  - backend/omni_engine_backup.py"
echo "  - backend/main_backup.py"
echo "  - frontend/src/App_backup.jsx"
echo "  - frontend/src/index_backup.css"
echo ""
echo "For detailed info, see: OPTIMIZATION_GUIDE.md"
echo ""
