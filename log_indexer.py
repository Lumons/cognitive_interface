import os
import json
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh import index

# Define the schema for the index
schema = Schema(role=TEXT(stored=True), 
                content=TEXT(stored=True), 
                timestamp=ID(stored=True),
                filename=ID(stored=True))  # New field for filename

# Create an index directory
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

# Create an index using the schema
ix = create_in("indexdir", schema)

# Function to add documents to the index
def add_documents_to_index(indexer, logs_folder):
    writer = indexer.writer()
    for filename in os.listdir(logs_folder):
        if filename.endswith(".json"):
            filepath = os.path.join(logs_folder, filename)
            with open(filepath, 'r') as file:
                data = json.load(file)
                for entry in data:
                    writer.add_document(role=entry["role"],
                                        content=entry["content"],
                                        timestamp=entry.get("timestamp", ""),
                                        filename=filename)  # Add filename here
    writer.commit()

# add folder
    
logs_folder_path = 'logs'  # Replace with your logs folder path
add_documents_to_index(ix, logs_folder_path)


# Function to search the index
def search_index(query_str):
    ix = index.open_dir("indexdir")
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_str)
        results = searcher.search(query)
        for result in results:
            print(f"Filename: {result['filename']}, Role: {result['role']}, Content: {result['content']}")

# Example search
        
search_index("log")

