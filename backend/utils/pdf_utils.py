import fitz  # PyMuPDF

def extract_text_per_page(pdf_path):
    """
    Extracts text from each page of the uploaded PDF.
    Returns a list of dicts: [{"page": 1, "text": "..."}]
    """
    pages = []
    with fitz.open(pdf_path) as pdf:
        for i, page in enumerate(pdf):
            text = page.get_text("text")
            pages.append({"page": i + 1, "text": text})
    return pages
