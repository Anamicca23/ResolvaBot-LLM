from operator import index
from whoosh.qparser import QueryParser
from whoosh import scoring

from t1 import expand_query

# Initialize the index
ix = index.open_dir("indexdir")

# Define the query parser
qp = QueryParser("content", schema=ix.schema)

# Parse the query
query = qp.parse(expand_query)

# Use BM25 scoring
searcher = ix.searcher(weighting=scoring.BM25F())

# Perform the search
results = searcher.search(query, limit=10)

# Print results
for result in results:
    print(result['title'], result['content'])
