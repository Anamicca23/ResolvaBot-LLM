import time
import pickle
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, MilvusException, utility

def create_milvus_collection(collection_name, dim, max_retries=10, wait_time=5):
    for attempt in range(max_retries):
        try:
            # Connect to Milvus
            connections.connect("default", host="localhost", port="19530")
            print("Connected to Milvus")

            # Check if collection already exists
            if collection_name in utility.list_collections():
                collection = Collection(collection_name)
                print(f"Collection '{collection_name}' already exists")
                return collection

            # Define fields with dynamic field enabled
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=dim),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
            ]

            # Create collection schema with dynamic fields enabled
            schema = CollectionSchema(fields, description="RAPTOR Index Collection")

            # Create collection
            collection = Collection(name=collection_name, schema=schema)
            print(f"Collection '{collection_name}' created with dynamic fields enabled")
            return collection
        except MilvusException as e:
            print(f"Milvus not ready, attempt {attempt + 1}/{max_retries}. Retrying in {wait_time} seconds...")
            print(f"Error: {e}")
            time.sleep(wait_time)
    raise Exception("Failed to connect to Milvus after several retries")

def insert_data_to_milvus(collection, embeddings, texts):
    # Ensure that embeddings and texts have the same length
    assert len(embeddings) == len(texts), "Embeddings and texts must have the same length"

    try:
        # Prepare data for insertion
        data = [
            embeddings,
            texts
        ]

        # Insert data into collection
        collection.insert(data)
        #collection.flush()
        print("Data inserted and flushed successfully")
    except MilvusException as e:
        print(f"Error during data insertion: {e}")
        raise

if __name__ == "__main__":
    collection_name = "raptor_index_textbook1"
    embedding_dim = 384  # Specify your embedding dimension

    collection = create_milvus_collection(collection_name, embedding_dim)

    # Load your embeddings and text chunks
    with open(f"D:/youtube downloads/3textbook/embeddings_textbook1.pkl", 'rb') as f:
        embeddings = pickle.load(f)

    with open(f"D:/youtube downloads/3textbook/chunks_textbook1.txt", 'r', encoding='utf-8') as f:
        texts = [line.strip() for line in f.readlines()]

    # Debug: Print lengths
    print(f"Number of embeddings: {len(embeddings)}")
    print(f"Number of text chunks: {len(texts)}")

    # Check if embeddings and texts are aligned
    if len(embeddings) != len(texts):
        raise ValueError("Mismatch between the number of embeddings and text chunks")

    insert_data_to_milvus(collection, embeddings, texts)
