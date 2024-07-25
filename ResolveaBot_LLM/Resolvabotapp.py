import streamlit as st
import fitz  # pymupdf
import pytesseract
from PIL import Image
import io
import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh import scoring
import nltk
from nltk.corpus import wordnet
import openai
import wikipediaapi
import requests

# Initialize OpenAI API key (Replace with your actual API key)
openai.api_key = "your_openai_api_key"

# Set the path for Tesseract OCR executable (Uncomment and update this path if needed)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

# Download necessary NLTK data
nltk.download('wordnet')

# Define the schema for the Whoosh index
schema = Schema(title=ID(stored=True), content=TEXT(stored=True))

# Create the index directory
index_dir = "indexdir"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

# Function to read PDF content using pymupdf and OCR
def read_pdf(uploaded_file):
    content = ""
    try:
        # Convert UploadedFile to a byte stream
        pdf_stream = io.BytesIO(uploaded_file.read())
        
        # Open the PDF file using pymupdf
        pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)  # Load each page
            
            # Extract text using pymupdf
            text = page.get_text()
            if text.strip():  # Check if text is extracted
                content += text
            else:
                # If text extraction fails, use OCR on images
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    text += pytesseract.image_to_string(image)
                content += text
                
        pdf_document.close()  # Close the document
    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}")
    return content

# Function to chunk text
def chunk_text(text, chunk_size=1000):
    """Splits the given text into chunks of specified size."""
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# Function to expand query
def expand_query(query_str):
    synonyms = set()
    for syn in wordnet.synsets(query_str):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return ' '.join(synonyms)

# Function to get answer from LLM
def get_answer_from_llm(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"An error occurred while generating an answer from the LLM: {e}")
        return ""

# Function to get an answer from Wikipedia
def get_answer_from_wikipedia(query):
    # Create a custom HTTP session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Resolvabotapp/1.0 (your.email@example.com)'  # Replace with your app name and contact
    })

    # Initialize Wikipedia with the custom session
    wiki_wiki = wikipediaapi.Wikipedia('en', session=session)

    try:
        page = wiki_wiki.page(query)
        if page.exists():
            return page.summary[:1000]  # Limit the summary to 1000 characters
        else:
            return "Page not found."
    except Exception as e:
        return f"An error occurred while fetching from Wikipedia: {e}"

# Streamlit UI
st.title("ResolvaBot LLM")
st.subheader("A sophisticated platform leveraging advanced large language models (LLMs) for the dynamic resolution of user queries, utilizing state-of-the-art natural language processing (NLP) and machine learning algorithms to facilitate context-aware and precise information retrieval and problem-solving.")

# File upload
uploaded_file = st.file_uploader("Upload a textbook (PDF)", type="pdf")

if uploaded_file is not None:
    # Extract and chunk content
    text_content = read_pdf(uploaded_file)
    chunks = chunk_text(text_content)
    
    # Create or open the Whoosh index
    if not index.exists_in(index_dir):
        ix = index.create_in(index_dir, schema)
    else:
        ix = index.open_dir(index_dir)

    # Add documents to the index
    writer = ix.writer()
    for i, chunk in enumerate(chunks):
        writer.add_document(title=f"textbook_chunk_{i+1}", content=chunk)
    writer.commit()
    
    st.write("Textbook content indexed successfully!")

    # Query input
    query_str = st.text_input("Enter your query:")
    if query_str:
        # Expand query
        expanded_query = expand_query(query_str)
        st.write(f"Expanded Query: {expanded_query}")  # Debugging output
        
        # Define the query parser
        qp = QueryParser("content", schema=ix.schema)
        
        # Parse the query
        query = qp.parse(expanded_query)
        
        # Use BM25 scoring
        searcher = ix.searcher(weighting=scoring.BM25F())
        
        # Perform the search
        results = searcher.search(query, limit=10)
        
        if results:
            st.write("Top 10 relevant chunks:")
            context = " ".join(result['content'] for result in results)
            for result in results:
                st.write(result['title'], result['content'])
        else:
            st.write("No relevant chunks found.")
            context = ""  # Ensure context is defined even if no results

        # Generate answer from LLM or fallback to Wikipedia
        question = st.text_input("Ask a question based on the retrieved content:")
        if question:
            if context:  # Check if context is available
                prompt = f"Based on the following text, answer the question:\n\n{context}\n\nQuestion: {question}"
                answer = get_answer_from_llm(prompt)
                st.write("Answer:", answer)
            else:
                st.write("No context available. Fetching information from Wikipedia...")
                wikipedia_answer = get_answer_from_wikipedia(question)
                st.write("Wikipedia Answer:", wikipedia_answer)
