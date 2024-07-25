from whoosh import index, scoring
from whoosh.qparser import QueryParser
from transformers import DPRContextEncoder, DPRQuestionEncoder, DPRTokenizer
import torch
import numpy as np
import faiss

# Load DPR models and tokenizer
context_encoder = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")
question_encoder = DPRQuestionEncoder.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
tokenizer = DPRTokenizer.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")

# Initialize the index
ix = index.open_dir("indexdir")

# Define the query parser for BM25
qp = QueryParser("content", schema=ix.schema)

# Function to encode text with DPR
def encode_text(texts, model, tokenizer):
    inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        embeddings = model(**inputs).pooler_output
    return embeddings.cpu().numpy()

# Define a function for DPR-based search
def dpr_search(query, context_embeddings, faiss_index, model, tokenizer):
    # Encode the query
    query_embedding = encode_text([query], model, tokenizer)[0]

    # Perform the search
    distances, indices = faiss_index.search(np.array([query_embedding]), k=10)
    
    return distances, indices

# Load or create a FAISS index for DPR (this should be done when creating the index)
faiss_index = faiss.IndexFlatL2(768)  # Adjust dimensions as needed
# faiss_index.add(context_embeddings)  # Add your context embeddings here

# Perform the BM25 search
query_str = "Your search query"  # Replace with your actual query
query = qp.parse(query_str)
searcher = ix.searcher(weighting=scoring.BM25F())
bm25_results = searcher.search(query, limit=10)

# Print BM25 results
print("BM25 Results:")
for result in bm25_results:
    print(result['title'], result['content'])

# Encode all contexts from the index for DPR (one-time setup, not in every search)
contexts = [doc['content'] for doc in ix.searcher().documents()]
context_embeddings = encode_text(contexts, context_encoder, tokenizer)
faiss_index.add(context_embeddings)

# Perform DPR search
distances, indices = dpr_search(query_str, context_embeddings, faiss_index, question_encoder, tokenizer)

# Print DPR results
print("DPR Results:")
for idx in indices[0]:
    print(contexts[idx])

# If Spider model is used, you'll need a similar setup for it. 
# This code assumes the use of BM25 and DPR.
