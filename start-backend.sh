#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Starting Silver Substrate API..."
echo ""
PYTHONPATH=src python3 -m silver_substrate.api
