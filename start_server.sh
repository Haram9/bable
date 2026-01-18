#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Babel FastAPI Server..."
echo "Server will be available at: http://localhost:8000"
echo "Dashboard will be available at: http://localhost:8000/"
echo ""
python3 server.py > ../logs/server.log 2>&1
