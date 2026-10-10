#!/usr/bin/env bash
set -e

echo "========================================================"
echo "      YouTube MP3 Downloader - Linux/macOS Setup"
echo "========================================================"

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.9+."
    exit 1
fi

echo "[1/2] Creating virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

echo "[2/2] Installing requirements..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup completed successfully! Run './run.sh' to launch."
