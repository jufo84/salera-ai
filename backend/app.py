from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
import json
import yaml
import os
from pathlib import Path
from typing import Optional
from loader_search_docs import process_document, search_docs
from memory import MemoryManager
from duckduckgo_search import ddg

# Lade Config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Lade Nutzer
with open(config['users_file'], "r") as f:
    users_data = json.load(f)

# Memory Manager initialisieren
memory_manager = MemoryManager(config['memory']['folder'], config['memory']['max_entries_per_user'])

app = FastAPI()
security = HTTPBasic()

# CORS (für Web-UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hilfsfunktionen
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    for user in users_data['users']:
        if user['username'] == credentials.username:
            if bcrypt.checkpw(credentials.password.encode(), user['password'].encode()):
                return user
    raise HTTPException(status_code=401, detail="Ungültige Zugangsdaten")

# Routen

@app.get("/api/me")
def read_me(user=Depends(get_current_user)):
    return {"username": user['username'], "role": user['role']}

@app.post("/api/memory/add")
def add_memory(entry: str = Form(...), user=Depends(get_current_user)):
    memory_manager.add_entry(user['username'], entry)
    return {"status": "ok", "entry": entry}

@app.get("/api/memory/search")
def search_memory(query: str, user=Depends(get_current_user)):
    results = memory_manager.search(user['username'], query)
    return {"results": results}

@app.post("/api/docs/upload")
def upload_document(file: UploadFile = File(...), user=Depends(get_current_user)):
    docs_path = Path(config['docs']['folder'])
    docs_path.mkdir(exist_ok=True)
    file_path = docs_path / file.filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    process_document(file_path)
    return {"status": "uploaded", "filename": file.filename}

@app.get("/api/docs/search")
def search_documents(query: str, user=Depends(get_current_user)):
    results = search_docs(query)
    return {"results": results}

@app.get("/api/websearch")
def web_search(query: str, user=Depends(get_current_user)):
    if not config['web_search']['enabled']:
        return {"results": [], "error": "Websuche deaktiviert"}
    results = ddg(query, max_results=config['web_search']['max_results'])
    return {"results": results}

@app.get("/api/ping")
def ping():
    return {"status": "ok"}
