from sentence_transformers import SentenceTransformer
import pickle
import pickle as pkl
import pandas as pd

def generate_embeddings(chunks, model_name='paraphrase-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings

if __name__ == "__main__":
    for i in range(1, 4):
        with open(f"D:/youtube downloads/3textbook/chunks_textbook{i}.txt", 'r', encoding='utf-8') as file:
            chunks = [line.strip() for line in file.readlines()]
            embeddings = generate_embeddings(chunks)
            with open(f"D:/youtube downloads/3textbook/embeddings_textbook{i}.pkl", 'wb') as f:
                pickle.dump(embeddings, f)


