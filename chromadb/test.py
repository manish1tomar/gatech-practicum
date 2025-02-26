import chromadb
import json
import csv

# Initialize ChromaDB (replace with your settings)
client = chromadb.PersistentClient(path="./general_chroma_db")
collection = client.get_collection(name="scholarship") #replace with your collection name

# Retrieve all data (or filter if needed)
results = collection.get( include=['embeddings','documents', 'metadatas'] )

print(results.keys())
print(results["documents"])
print(results["metadatas"])

questions = results["metadatas"]

# Combine questions and answers
data = []
for i in questions:
    print(i["question"])
    print(i["answer"],"\n")
    pass