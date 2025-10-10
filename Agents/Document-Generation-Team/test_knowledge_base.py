"""Test script to verify documents are in the vector database"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.huggingface import HuggingfaceCustomEmbedder

TMP_DIR = Path("tmp")
CONVERTED_DIR = Path("converted_docs")

print("Connecting to knowledge base...")
knowledge_base = Knowledge(
    vector_db=LanceDb(
        uri=str(TMP_DIR / "lancedb"),
        table_name="document_knowledge",
        search_type=SearchType.hybrid,
        embedder=HuggingfaceCustomEmbedder(
            id="BAAI/bge-small-en-v1.5",
            dimensions=384,
            api_key=os.getenv("HUGGINGFACE_HUB_TOKEN"),
        ),
    ),
    max_results=5,
)

# Load documents into knowledge base
if CONVERTED_DIR.exists() and any(CONVERTED_DIR.iterdir()):
    print("Loading documents into knowledge base...")
    for doc_file in CONVERTED_DIR.iterdir():
        if doc_file.suffix in [".md", ".txt"]:
            print(f"  Loading: {doc_file.name}")
            knowledge_base.add_content(path=str(doc_file))
    print("Knowledge base loaded\n")

# Test 1: Search for TechVision Corporation
print("\n" + "=" * 70)
print("TEST 1: Searching for 'TechVision Corporation'...")
print("=" * 70)
results = knowledge_base.search("TechVision Corporation")

if results:
    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Content: {result.content[:300]}...")
        if hasattr(result, "meta_data"):
            print(f"  Metadata: {result.meta_data}")
        print()
else:
    print("NO RESULTS FOUND!")

# Test 2: Search for founding year
print("\n" + "=" * 70)
print("TEST 2: Searching for 'founded 2015'...")
print("=" * 70)
results2 = knowledge_base.search("founded 2015")

if results2:
    print(f"\nFound {len(results2)} results:\n")
    for i, result in enumerate(results2, 1):
        print(f"Result {i}:")
        print(f"  Content: {result.content[:300]}...")
        print()
else:
    print("NO RESULTS FOUND!")

# Test 3: Search for revenue
print("\n" + "=" * 70)
print("TEST 3: Searching for 'revenue 550M'...")
print("=" * 70)
results3 = knowledge_base.search("revenue 550M ARR")

if results3:
    print(f"\nFound {len(results3)} results:\n")
    for i, result in enumerate(results3, 1):
        print(f"Result {i}:")
        print(f"  Content: {result.content[:300]}...")
        print()
else:
    print("NO RESULTS FOUND!")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
