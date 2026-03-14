#!/bin/bash

echo "🚀 Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "📦 Building macOS application..."
python3 -m PyInstaller --noconfirm --clean build.spec

echo "✅ Build complete! You can find the app in the 'dist' folder."
open dist
