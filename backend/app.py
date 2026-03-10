from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.pdf_utils import extract_text_per_page
from utils.embedding_utils import create_vector_store
from utils.query_utils import query_vector_db
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Check if API key is loaded
api_key = os.getenv("GROQ_API_KEY")
print("Loaded API KEY:", api_key)

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Please check your .env file.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Groq client
client = Groq(api_key=api_key)

# Function to query Grok
def ask_ai(question, context=None):

    if context:
        user_prompt = f"""
You are a helpful study assistant.

Use the following context to answer the question.

Context:
{context}

Question:
{question}
"""
    else:
        user_prompt = question

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content


# Home route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "StudyBuddy backend is running successfully"})


# Upload PDF endpoint
@app.route("/upload", methods=["POST"])
def upload_pdf():
    try:
        if "pdf" not in request.files:
            return jsonify({"error": "No PDF file uploaded"}), 400

        file = request.files["pdf"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        pages = extract_text_per_page(file_path)
        create_vector_store(pages)

        return jsonify({
            "message": f"Document '{file.filename}' uploaded successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ask question endpoint
@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        query = data.get("query")

        if not query:
            return jsonify({"error": "Query is required"}), 400

        passages = query_vector_db(query)

        context = "\n\n".join(
            [f"Page {p['page']}:\n{p['text']}" for p in passages]
        )

        answer = ask_ai(query, context=context)

        pages = sorted({
            p.get("page") for p in passages if p.get("page") is not None
        })

        if pages:
            answer = f"{answer.strip()} (refer page {', '.join(map(str, pages))})"

        return jsonify({"answer": answer})

    except Exception as e:
        print("ASK ROUTE ERROR:", e)
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

