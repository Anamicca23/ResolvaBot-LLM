import fitz  # pymupdf
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        pdf_document = fitz.open(pdf_path)  # Open the PDF file using pymupdf
        number_of_pages = len(pdf_document)  # Get the number of pages
        for page_num in range(number_of_pages):
            page = pdf_document.load_page(page_num)  # Load each page
            text += page.get_text()  # Extract text from the page
        pdf_document.close()  # Close the PDF document
    except Exception as e:
        print(f"An error occurred while processing {pdf_path}: {e}")
    return text

if __name__ == "__main__":
    # Define the base path
    base_path = "D:/youtube downloads/steps_AI_LLM_project-main/3textbook/"
    
    # Extract text from PDF files and save to .txt files
    for i in range(1, 4):
        pdf_path = os.path.join(base_path, f"textbook{i}.pdf")
        txt_path = os.path.join(base_path, f"textbook{i}.txt")
        
        if os.path.exists(pdf_path):
            text = extract_text_from_pdf(pdf_path)
            with open(txt_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text)
        else:
            print(f"PDF file not found: {pdf_path}")
    
    # Read and print the contents of .txt files
    for i in range(1, 4):
        txt_path = os.path.join(base_path, f"textbook{i}.txt")
        
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as text_file:
                text = text_file.read()
                print(f"Contents of textbook{i}.txt:\n{text[:500]}\n{'-'*40}\n")
        else:
            print(f"Text file not found: {txt_path}")
