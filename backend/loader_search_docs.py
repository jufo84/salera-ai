from pathlib import Path
import json
from sentence_transformers import SentenceTransformer
import faiss

# Pfad zur Index-Datei aus config.yaml
CONFIG_PATH = "config.yaml"
import yaml
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

docs_folder = Path(config['docs']['folder'])
index_file = Path(config['docs']['index_file'])
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Lade oder erstelle Index
if index_file.exists():
    with open(index_file, "r") as f:
        docs_data = json.load(f)
else:
    docs_data = []

embeddings = None
faiss_index = None

def process_document(file_path):
    global docs_data, embeddings, faiss_index
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    docs_data.append({"filename": file_path.name, "text": text})
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(docs_data, f, ensure_ascii=False, indent=2)

    # Embeddings und FAISS neu aufbauen
    texts = [d["text"] for d in docs_data]
    embeddings = model.encode(texts, convert_to_numpy=True)
    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(embeddings)

def search_docs(query, top_k=5):
    global docs_data, embeddings, faiss_index
    if not docs_data:
        return []

    if faiss_index is None or embeddings is None:
        texts = [d["text"] for d in docs_data]
        embeddings = model.encode(texts, convert_to_numpy=True)
        faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
        faiss_index.add(embeddings)

    query_emb = model.encode([query], convert_to_numpy=True)
    distances, indices = faiss_index.search(query_emb, min(top_k, len(docs_data)))
    results = [{"filename": docs_data[i]["filename"], "text": docs_data[i]["text"]} for i in indices[0]]
    return results
