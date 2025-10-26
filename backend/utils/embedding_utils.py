import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load embedding model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_vector_store(pages, store_dir="vector_store"):
    """
    Generates embeddings for each page and stores them in a FAISS index.
    Also saves metadata (page numbers + text) as pickle file.
    """
    os.makedirs(store_dir, exist_ok=True)

    texts = [p["text"] for p in pages]
    embeddings = model.encode(texts, show_progress_bar=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype('float32'))

    faiss.write_index(index, os.path.join(store_dir, "faiss.index"))
    with open(os.path.join(store_dir, "metadata.pkl"), "wb") as f:
        pickle.dump(pages, f)

    print(f"✅ Vector store created with {len(pages)} pages.")
