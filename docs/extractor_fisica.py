import sys
from pdfminer.high_level import extract_text

def extract_pages(pdf_path, start_page, end_page, exclude_range=None):
    # pdfminer uses 0-based indexing for pages in some contexts, 
    # but high_level extract_text uses page_numbers (0-indexed)
    pages = []
    for p in range(start_page - 1, end_page):
        if exclude_range and exclude_range[0] <= p + 1 <= exclude_range[1]:
            continue
        pages.append(p)
    
    try:
        text = extract_text(pdf_path, page_numbers=pages)
        print(text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    pdf = r"C:\Users\hp\aivideogen\docs\Libro_Fisica_Basica.pdf"
    # El usuario quiere: Tema 2 hasta p77, excluyendo 45-48.
    # Necesitamos identificar primero dónde empieza el Tema 2.
    # Por ahora extraeremos un rango amplio para buscar el índice.
    extract_pages(pdf, 1, 80, exclude_range=(45, 48))
