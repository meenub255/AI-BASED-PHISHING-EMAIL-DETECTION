import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict, Any
import traceback

class LocalEmbeddingFunction(chromadb.EmbeddingFunction):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"[VectorStore] Loading local embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("[VectorStore] Model loaded.")

    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        """Get embeddings using local SentenceTransformer."""
        # encode() returns a list of numpy arrays, we need list of lists
        embeddings = self.model.encode(input).tolist()
        return embeddings

class BrandVectorStore:
    def __init__(self, persist_directory: str = "data/vector_db"):
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize local embedding function
        self.ef = LocalEmbeddingFunction()
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="brand_guidelines",
            embedding_function=self.ef
        )

    def add_brand(self, brand_name: str, guidelines: str, official_domains: List[str]):
        """Store brand identity using local embeddings."""
        metadata = {
            "brand_name": brand_name,
            "domains": ",".join(official_domains)
        }
        self.collection.upsert(
            documents=[guidelines],
            metadatas=[metadata],
            ids=[brand_name.lower()]
        )
        print(f"[VectorStore] Brand '{brand_name}' added/updated locally.")

    def query_brand(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve using local embeddings."""
        results = self.collection.query(
            query_texts=[query],
            n_results=1
        )
        return results

if __name__ == "__main__":
    try:
        # Re-seed with local embeddings
        store = BrandVectorStore()
        
        store.add_brand(
            "Microsoft",
            "Official colors: #00A4EF, #7FBA00, #F25022, #FFB900. Fonts: Segoe UI. Urgent alerts always come from @microsoft.com domains.",
            ["microsoft.com", "office.com", "outlook.com"]
        )
        
        store.add_brand(
            "PayPal",
            "Official colors: #003087 (Blue), #009CDE (Light Blue). Links check: verified protocols.",
            ["paypal.com", "paypal-objects.com"]
        )
        
        print("\n[VectorStore] Success! Local Database seeded.")
        
        # Test
        test_query = "What are the official colors of PayPal?"
        result = store.query_brand(test_query)
        print(f"\n[Test Query] result: {result['documents'][0][0]}")
        
    except Exception:
        traceback.print_exc()
