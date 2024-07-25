from nltk.tokenize import word_tokenize
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
import os

def chunk_text(text, chunk_size=100):
    words = word_tokenize(text)
    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
    return [" ".join(chunk) for chunk in chunks]

# Define the schema for the Whoosh index
schema = Schema(title=ID(stored=True), content=TEXT(stored=True))

# Create the index directory
index_dir = "indexdir"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

# Create the Whoosh index
ix = index.create_in(index_dir, schema)

# Add documents to the index
writer = ix.writer()

# Sample text extraction (replace with actual text extraction from textbooks)
for i in range(1, 4):
    pdf_path = f"D:/youtube downloads/3textbook/textbook{i}.txt"
    with open(pdf_path, 'r', encoding='utf-8') as file:
        sample_text = file.read()
    
    # Chunk the sample text
    chunked_texts = chunk_text(sample_text)
    
    # Add each chunk to the index
    for j, chunk in enumerate(chunked_texts):
        writer.add_document(title=f"textbook_{i}_chunk_{j+1}", content=chunk)

writer.commit()
