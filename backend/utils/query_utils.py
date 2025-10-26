import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

# Load OpenAI API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def query_vector_db(query, store_dir="vector_store", top_k=3):
    """
    Given a user query, searches FAISS index and returns top similar pages.
    """
    query_vec = model.encode([query])
    index = faiss.read_index(os.path.join(store_dir, "faiss.index"))

    D, I = index.search(np.array(query_vec).astype('float32'), k=top_k)

    with open(os.path.join(store_dir, "metadata.pkl"), "rb") as f:
        pages = pickle.load(f)

    top_pages = [pages[i] for i in I[0]]
    return top_pages


def summarize_with_llm(query, passages):
    """
    Uses GPT to generate an answer using top-matched passages.
    """
    context = "\n\n".join([f"Page {p['page']}:\n{p['text']}" for p in passages])

    prompt = f"""You are a helpful study assistant.
Use the context below to answer the question briefly and accurately.
Include the page numbers in your answer.

Context:
{context}

Question: {query}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a smart, concise study assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
