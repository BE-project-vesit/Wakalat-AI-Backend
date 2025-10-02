"""
Demonstration script for vector database search capabilities
Shows how semantic search works for legal case precedents
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from src.tools.precedent_search import search_precedents
from src.tools.case_law_finder import find_case_laws
from src.services.vector_db import get_vector_db


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


async def demo_precedent_search():
    """Demonstrate precedent search with vector database"""
    print_section("DEMO 1: Semantic Precedent Search")
    
    queries = [
        "breach of contract damages",
        "murder circumstantial evidence",
        "environmental pollution compensation"
    ]
    
    for query in queries:
        print(f"Query: '{query}'")
        print("-" * 80)
        
        result = await search_precedents(query, max_results=2)
        
        # Parse and display results
        import json
        data = json.loads(result)
        
        print(f"Found {data['total_found']} relevant cases:")
        for i, case in enumerate(data['results'], 1):
            print(f"\n{i}. {case['case_name']}")
            print(f"   Citation: {case['citation']}")
            print(f"   Relevance: {case['relevance_score']:.3f}")
            print(f"   Summary: {case['summary'][:100]}...")
        
        print()


async def demo_case_law_finder():
    """Demonstrate finding specific case laws"""
    print_section("DEMO 2: Case Law Finder by Citation")
    
    citation = "AIR 2020 SC 1234"
    print(f"Searching for: {citation}")
    print("-" * 80)
    
    result = await find_case_laws(citation=citation)
    
    import json
    data = json.loads(result)
    
    if data['cases_found']:
        case = data['cases_found'][0]
        print(f"\n✓ Found: {case['case_name']}")
        print(f"  Citation: {case['citation']}")
        print(f"  Court: {case['court']}")
        print(f"  Judges: {case['judges']}")
        print(f"  Summary: {case['summary']}")
    else:
        print("✗ No cases found")


def demo_vector_db_stats():
    """Show vector database statistics"""
    print_section("DEMO 3: Vector Database Statistics")
    
    vdb = get_vector_db()
    stats = vdb.get_collection_stats()
    
    print(f"Collection Name: {stats['collection_name']}")
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Storage Path: {stats['persist_directory']}")
    
    if stats['total_documents'] > 0:
        print(f"\n✓ Vector database is populated and ready for search")
    else:
        print(f"\n⚠ Vector database is empty. Run 'python scripts/load_sample_data.py' to load sample cases")


async def main():
    """Run all demonstrations"""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "WAKALAT-AI VECTOR DATABASE DEMONSTRATION" + " " * 22 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Check if database has data
    vdb = get_vector_db()
    stats = vdb.get_collection_stats()
    
    if stats['total_documents'] == 0:
        print("\n⚠ WARNING: Vector database is empty!")
        print("Please run: python scripts/load_sample_data.py")
        print("\nContinuing with empty database...\n")
    
    # Run demonstrations
    await demo_precedent_search()
    await demo_case_law_finder()
    demo_vector_db_stats()
    
    print("\n" + "=" * 80)
    print(" DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nFor more information, see docs/VECTOR_DATABASE.md\n")


if __name__ == "__main__":
    asyncio.run(main())
