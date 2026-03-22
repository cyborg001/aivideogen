import PyPDF2
import os

def extract_text(pdf_path):
    if not os.path.exists(pdf_path):
        return None
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
            return text
    except Exception as e:
        return None

if __name__ == "__main__":
    pdf_file = r"C:\Users\hp\aivideogen\tesis carlos\tesis_mw.pdf"
    content = extract_text(pdf_file)
    if content:
        with open("tesis_content.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print("Extraction complete.")
    else:
        print("Extraction failed.")
