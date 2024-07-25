import pickle
from sklearn.mixture import GaussianMixture
from sentence_transformers import SentenceTransformer
import numpy as np
import os


def raptor_index(embeddings, chunks, model_name='sentence-transformers/all-MiniLM-L6-v2'):
    # Fit a Gaussian Mixture Model
    gmm = GaussianMixture(n_components=10, random_state=0)
    gmm.fit(embeddings)
    labels = gmm.predict(embeddings)

    # Summarize each cluster using an LLM (simplified for demonstration purposes)
    summaries = {}
    for cluster in set(labels):
        cluster_indices = np.where(labels == cluster)[0]
        cluster_texts = [chunks[idx] for idx in cluster_indices]
        cluster_text = " ".join(cluster_texts)
        summaries[cluster] = cluster_text[:512]  # Summarize simply by taking first 512 tokens

    # Embed the summaries
    model = SentenceTransformer(model_name)
    summary_embeddings = model.encode(list(summaries.values()))

    return summaries, summary_embeddings, labels


if __name__ == "__main__":
    for i in range(1, 4):
        embeddings_path = f"E:/TEXT_EXTRACTION_LLM/data/embeddings_textbook{i}.pkl"
        chunks_path = f"E:/TEXT_EXTRACTION_LLM/data/chunks_textbook{i}.txt"

        with open(embeddings_path, 'rb') as embed_file:
            embeddings = pickle.load(embed_file)

        with open(chunks_path, 'r', encoding='utf-8') as chunk_file:
            chunks = chunk_file.read().splitlines()

        summaries, summary_embeddings, labels = raptor_index(embeddings, chunks)

        # Save the RAPTOR index
        raptor_path = f"E:/TEXT_EXTRACTION_LLM/data/raptor_index_textbook{i}.pkl"
        with open(raptor_path, 'wb') as raptor_file:
            pickle.dump((summaries, summary_embeddings, labels), raptor_file)
