#!/bin/bash
echo "Stopping all AlihanBot services..."

pkill -f "sheets_sync/sync_service.py" || true
pkill -f "sheets_sync/sync_service_v2.py" || true
pkill -f "api/main.py" || true
pkill -f "bot.main" || true
pkill -f "run_bot.py" || true

echo "All services stopped."
