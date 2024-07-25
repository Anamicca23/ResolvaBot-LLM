import os

# Define base path
BASE_PATH = "D:/youtube downloads/3textbook/"

def chunk_text(text, chunk_size=1000):
    """Splits the given text into chunks of specified size."""
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def process_files(file_indices):
    """Processes files specified by their indices, chunking their text and saving the chunks."""
    for i in file_indices:
        try:
            # Construct file paths
            input_path = os.path.join(BASE_PATH, f"textbook{i}.txt")
            output_path = os.path.join(BASE_PATH, f"chunks_textbook{i}.txt")
            
            # Read the text file
            with open(input_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Chunk the text
            chunks = chunk_text(text)
            
            # Write chunks to output file
            with open(output_path, 'w', encoding='utf-8') as chunk_file:
                chunk_file.write('\n'.join(chunks) + '\n')
                
            print(f"Processed {input_path} into {output_path}")
            
        except Exception as e:
            print(f"An error occurred with file {i}: {e}")

if __name__ == "__main__":
    process_files(range(1, 4))
