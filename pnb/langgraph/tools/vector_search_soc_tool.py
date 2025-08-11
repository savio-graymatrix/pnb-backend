from typing import Dict
import numpy as np
from pymongo import MongoClient
import os
from openai import OpenAI
from dotenv import load_dotenv
from pnb import SETTINGS

load_dotenv()

# Connect to MongoDB Atlas
client = MongoClient(SETTINGS.MONGO_URI)
db = client["soc_incidents"]

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedding_model = "text-embedding-3-small"

def get_embedding(text: str, model: str = embedding_model) -> list:
    """Generate embedding for given text using OpenAI."""
    try:
        text = text.replace("\n", " ")
        response = openai_client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding generation failed: {e}")
        return []

def vector_search_in_collection(input: dict) -> Dict[str, list]:
    """
    This function receives:
    - 'collection': str – the incident report name (mapped to 'report_name' in the DB)
    - 'query': str – the search query

    The MongoDB collection is always 'Incidents'.
    It filters by report_name first, then does similarity search.
    """
    SIMILARITY_THRESHOLD = 0.1
    MONGO_COLLECTION = "Incidents"

    try:
        report_name = input.get("collection")  # Actually the report_name filter
        query = input.get("query")

        if not isinstance(report_name, str):
            raise ValueError("'collection' (report_name) must be a string.")
        if not isinstance(query, str):
            raise ValueError("'query' must be a string.")

        query_embedding = np.array(get_embedding(query))
        collection = db[MONGO_COLLECTION]

        # Fetch only documents with the same report_name
        docs = list(collection.find(
            {"report_name": report_name},
            {"embedding": 1}
        ))

        if not docs:
            return {"message": f"No documents found in '{MONGO_COLLECTION}' for report_name '{report_name}'."}

        matched_docs = []
        for doc in docs:
            doc_emb = np.array(doc.get("embedding", []))
            if doc_emb.size != query_embedding.size:
                continue

            try:
                score = np.dot(doc_emb, query_embedding) / (
                    np.linalg.norm(doc_emb) * np.linalg.norm(query_embedding)
                )
                if score >= SIMILARITY_THRESHOLD:
                    full_doc = collection.find_one(
                        {"_id": doc["_id"]},
                        {"_id": 0, "embedding": 0}
                    )
                    if full_doc:
                        matched_docs.append((score, full_doc))
            except Exception as e:
                print(f"Skipping doc due to scoring error: {e}")

        if matched_docs:
            return {
                "report_name": report_name,
                "results": [doc for _, doc in sorted(matched_docs, key=lambda x: x[0], reverse=True)]
            }
        else:
            return {"message": f"No matching documents found in '{MONGO_COLLECTION}' for report_name '{report_name}'."}

    except Exception as e:
        return {"error": f"Vector search failed: {str(e)}"}
