#!/bin/bash
set -e

# 1️⃣ Python-Venv anlegen, falls noch nicht vorhanden
if [ ! -d "venv" ]; then
    echo "Erstelle Python Virtual Environment..."
    python3 -m venv venv
fi

# 2️⃣ Venv aktivieren und Dependencies installieren
echo "Aktiviere Virtual Environment..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3️⃣ Frontend bauen (falls Node.js vorhanden)
if [ -f "frontend/package.json" ]; then
    echo "Baue Frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# 4️⃣ Avatar-Datei prüfen
if [ ! -f "frontend/avatar.glb" ]; then
    echo "Warnung: avatar.glb nicht gefunden. Avatar wird nicht angezeigt."
fi

# 5️⃣ Backend starten
echo "Starte AI-Backend..."
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8000
