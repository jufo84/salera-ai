import os
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class MemoryManager:
    def __init__(self, memory_folder="./memory", max_entries_per_user=1000):
        self.memory_folder = Path(memory_folder)
        self.memory_folder.mkdir(exist_ok=True)
        self.max_entries_per_user = max_entries_per_user
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def _get_user_file(self, username):
        return self.memory_folder / f"{username}.json"

    def add_entry(self, username, text):
        user_file = self._get_user_file(username)
        if user_file.exists():
            with open(user_file, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(text)
        if len(data) > self.max_entries_per_user:
            data = data[-self.max_entries_per_user:]

        with open(user_file, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def search(self, username, query, top_k=5):
        user_file = self._get_user_file(username)
        if not user_file.exists():
            return []

        with open(user_file, "r") as f:
            data = json.load(f)

        if not data:
            return []

        embeddings = self.model.encode(data, convert_to_numpy=True)
        query_emb = self.model.encode([query], convert_to_numpy=True)

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        distances, indices = index.search(query_emb, min(top_k, len(data)))

        results = [data[i] for i in indices[0]]
        return results
