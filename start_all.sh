#!/bin/bash
set -e

# Define project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Create logs directory
mkdir -p logs

echo "======================================================================"
echo "🚀 STARTING ALIHANBOT SYSTEM"
echo "======================================================================"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ ERROR: venv not found!"
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_DIR"

# Check credentials
if [ ! -f "credentials/google-sheets-credentials.json" ]; then
    echo "⚠️  WARNING: Google Sheets credentials not found!"
fi

# Stop old processes
echo "1. Stopping old processes..."
pkill -f "sheets_sync/sync_service.py" || true
pkill -f "sheets_sync/sync_service_v2.py" || true
pkill -f "api/main.py" || true
pkill -f "bot.main" || true
pkill -f "run_bot.py" || true
sleep 2
echo "   ✅ Old processes stopped"

# Start Sync Service (The Correct One: sync_service.py)
echo ""
echo "2. Starting Sync Service..."
nohup python sheets_sync/sync_service.py > logs/sync.log 2>&1 &
SYNC_PID=$!
echo "   ✅ Sync Service started (PID: $SYNC_PID)"

# Start API
echo ""
echo "3. Starting API Server..."
nohup python api/main.py > logs/api.log 2>&1 &
API_PID=$!
echo "   ✅ API Server started (PID: $API_PID)"

# Start Bot
echo ""
echo "4. Starting Telegram Bot..."
nohup python -m bot.main > logs/bot.log 2>&1 &
BOT_PID=$!
echo "   ✅ Telegram Bot started (PID: $BOT_PID)"

# Wait and Check
sleep 3

echo ""
echo "5. Status Check..."

if ps -p $SYNC_PID > /dev/null; then
    echo "   ✅ Sync Service: RUNNING"
else
    echo "   ❌ Sync Service: FAILED (Check logs/sync.log)"
fi

if ps -p $API_PID > /dev/null; then
    echo "   ✅ API Server: RUNNING"
else
    echo "   ❌ API Server: FAILED (Check logs/api.log)"
fi

if ps -p $BOT_PID > /dev/null; then
    echo "   ✅ Telegram Bot: RUNNING"
else
    echo "   ❌ Telegram Bot: FAILED (Check logs/bot.log)"
fi

echo ""
echo "======================================================================"
echo "✅ SYSTEM STARTUP COMPLETE"
echo "======================================================================"
echo "📝 Logs available in logs/ directory"
echo "   - sync.log"
echo "   - api.log"
echo "   - bot.log"
echo "======================================================================"
