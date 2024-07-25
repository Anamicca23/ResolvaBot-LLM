# ResolvaBot-LLM - A User Query Resolving Bot for Textbooks.
A sophisticated platform leveraging advanced large language models (LLMs) for the dynamic resolution of user queries, utilizing state-of-the-art natural language processing (NLP) and machine learning algorithms to facilitate context-aware and precise information retrieval and problem-solving.


## Objective

The goal of this project is to create a comprehensive system for extracting content from textbooks, indexing it using RAPTOR in a MILVUS vector database, and developing a question-answering system using a Language Model (LLM). The assessment covers various aspects such as data extraction, data processing, vector database creation, retrieval techniques, and natural language processing.

## Task Description

### 1. Textbook Selection and Content Extraction

1. **Textbook Selection**:

    - The following textbooks were selected for content extraction and processing in this project:
    
    1. **Introduction to Algorithms (4th Edition)**  
       *Authors:* Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, and Clifford Stein  
       *Publisher:* MIT Press  
       *Link:* [Introduction to Algorithms (4th Edition)](https://dl.ebooksworld.ir/books/Introduction.to.Algorithms.4th.Leiserson.Stein.Rivest.Cormen.MIT.Press.9780262046305.EBooksWorld.ir.pdf)
    
    2. **Handbook of Natural Language Processing (Second Edition)**  
       *Editor:* Dan Jurafsky and James H. Martin  
       *Publisher:* Chapman & Hall/CRC  
       *Link:* [Handbook of Natural Language Processing (Second Edition)](https://karczmarczuk.users.greyc.fr/TEACH/TAL/Doc/Handbook%20Of%20Natural%20Language%20Processing,%20Second%20Edition%20Chapman%20&%20Hall%20Crc%20Machine%20Learning%20&%20Pattern%20Recognition%202010.pdf)
    
    3. **System Analysis and Design**  
       *Publisher:* Informatics Institute  
       *Link:* [System Analysis and Design](https://www.uoitc.edu.iq/images/documents/informatics-institute/Competitive_exam/Systemanalysisanddesign.pdf)


2. **Content Extraction**:
   - Extracted content from the selected textbooks, ensuring thorough coverage of all relevant text.

### 2. Data Chunking and RAPTOR Indexing

1. **Data Chunking**:
   - Chunking the extracted content into short, contiguous texts of approximately 100 tokens each, preserving sentence boundaries.
   - **Note**: Use NLTK’s `word_tokenize` for tokenization.

2. **Embedding and Indexing**:
   - Embeded the chunked texts using Sentence-BERT (SBERT) to create vector representations.
   - Implemented RAPTOR indexing with the following steps:
     - **Clustering**: Used Gaussian Mixture Models (GMMs) with soft clustering to allow nodes to belong to multiple clusters.
     - **Summarization**: Summarizing clusters using an LLM (e.g., GPT-3.5-turbo) to create concise representations.
     - **Recursive Clustering and Summarization**: Re-embeded the summarized texts and recursively apply clustering and summarization to form a hierarchical tree structure.
   - Stored the RAPTOR index in a MILVUS vector database, including metadata such as textbook titles and page numbers.

### 3. Retrieval Techniques

1. **Query Expansion**:
   - Implement query expansion techniques such as synonym expansion, stemming, or using external knowledge bases.

2. **Hybrid Retrieval Methods**:
   - Combine BM25 (Best Match 25) with BERT/bi-encoder-based retrieval methods like Dense Passage Retrieval (DPR) and Semantic Passage Retrieval (SPIDER).

3. **Re-ranking**:
   - Re-rank retrieved data based on relevance and similarity using appropriate ranking algorithms.

### 4. Question Answering

1. **LLM Integration**:
   - Use an LLM (e.g., OpenAI’s GPT-3.5-turbo) to generate accurate and relevant answers based on the retrieved data.

2. **Fallback to Wikipedia**:
   - If no relevant context is available, use Wikipedia as a fallback for answering questions. Handle Wikipedia API requests and error handling properly.

### 5. User Interface (Optional)

1. **UI Development**:
   - Developed a user interface using frameworks like Streamlit to demonstrate the system’s functionality.
   - The interface should allow users to input queries and view retrieved answers along with corresponding textbook titles and page numbers.

### streamlit interface:

![resolva bot llm](https://github.com/user-attachments/assets/c4f8aa6c-a607-4558-8b0c-72b806180d52)


## Installation and Setup

### Prerequisites

- Python 3.7 or later
- Git

### Clone the Repository

```bash
git clone https://github.com/Anamicca23/ResolvaBot-LLM.git
cd ResolvaBot-LLM
```

### Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Setup Environment Variables

- Create a `.env` file in the root directory and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key
```

- For Wikipedia API, ensure your `user_agent` is set appropriately in your code.

### Initialize the Index

1. Run the script to create the index from the textbooks:

```bash
python create_index.py
```

### Run the Application

1. Start the Streamlit app or Gradio interface:

```bash
streamlit run app.py
```

## Usage

1. **Upload Textbooks**: Use the Streamlit interface to upload textbooks for indexing.
2. **Query the System**: Input queries into the interface to retrieve and view answers.
3. **View Results**: Examine the results displayed, including relevant context and answers.

## Evaluation Criteria

- Appropriateness of textbooks and completeness of content extraction.
- Effectiveness of data chunking and RAPTOR indexing processes.
- Quality of retrieval techniques, including query expansion and hybrid methods.
- Relevance and accuracy of re-ranking algorithms.
- Accuracy of LLM-generated answers.
- Overall system performance and efficiency.
- (Optional) User interface design and user experience.

## Resources

- **RAPTOR Paper**: [RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval](https://example.com/raptor-paper)
- **MILVUS Documentation**: [MILVUS Documentation](https://milvus.io/docs/)
- **Relevant Python Libraries**:
  - **NLTK**: [Natural Language Toolkit](https://www.nltk.org/)
  - **Gensim**: [Gensim Documentation](https://radimrehurek.com/gensim/)
  - **Transformers**: [Transformers Documentation](https://huggingface.co/transformers/)
  - **PymuPDF2**: [PymuPDF Documentation](https://pythonhosted.org/PymuPDF/)
  - **Pyserini**: [Pyserini Documentation](https://github.com/castorini/pyserini)
  - **Sentence-Transformers**: [Sentence-Transformers Documentation](https://www.sbert.net/)
