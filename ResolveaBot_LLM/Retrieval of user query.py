from nltk.tokenize import word_tokenize
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
import os

def chunk_text(text, chunk_size=100):
    words = word_tokenize(text)
    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
    return [" ".join(chunk) for chunk in chunks]

# Sample text extraction (replace with actual text extraction from textbooks)
for i in range(1, 4):
        pdf_path = f"E:/TEXT_EXTRACTION_LLM/data/textbook{i}.txt"
sample_text = pdf_path

# Chunk the sample text
chunked_texts = chunk_text(sample_text)

# Define the schema for the Whoosh index
schema = Schema(title=ID(stored=True), content=TEXT(stored=True))

# Create the index directory
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

# Create the Whoosh index
ix = index.create_in("indexdir", schema)

# Add documents to the index
writer = ix.writer()

for i, chunk in enumerate(chunked_texts):
    writer.add_document(title=f"chunk_{i+1}", content=chunk)
writer.commit()
