#!/usr/bin/env python3
"""
Supabase RAG Helper for Nelson Pediatrics Database

This module provides helper functions for querying the Nelson Pediatrics database
in Supabase for RAG (Retrieval Augmented Generation) applications.
"""

import os
import json
from typing import List, Dict, Any, Optional
import openai
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Initialize OpenAI client
openai.api_key = os.environ.get("OPENAI_API_KEY")


def search_by_text(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for content using full-text search
    
    Args:
        query: The search query
        limit: Maximum number of results to return
        
    Returns:
        List of matching content blocks
    """
    response = supabase.table("nelson_content").select("""
        id,
        title,
        content_text,
        content_type,
        nelson_chapters(chapter_number, title),
        nelson_sections(section_number, title),
        nelson_subsections(subsection_number, title)
    """).text_search("content_text", query).limit(limit).execute()
    
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error searching content: {response.error}")
    
    return response.data


def search_by_similarity(embedding: List[float], limit: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    Search for content using vector similarity
    
    Args:
        embedding: The query embedding vector
        limit: Maximum number of results to return
        threshold: Similarity threshold (0-1)
        
    Returns:
        List of matching content blocks
    """
    response = supabase.rpc(
        "match_nelson_content",
        {
            "query_embedding": embedding,
            "match_threshold": threshold,
            "match_count": limit
        }
    ).execute()
    
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error searching by similarity: {response.error}")
    
    return response.data


def get_drug_info(drug_name: str) -> List[Dict[str, Any]]:
    """
    Get drug information by name
    
    Args:
        drug_name: The drug name to search for
        
    Returns:
        List of matching drugs with dosages
    """
    response = supabase.table("nelson_drugs").select("""
        id,
        drug_name,
        drug_brand_name,
        drug_formulations,
        drug_indication,
        drug_mechanism,
        drug_adverse_effects,
        drug_contraindications,
        nelson_content(title, content_text),
        nelson_dosages(*)
    """).ilike("drug_name", f"%{drug_name}%").limit(10).execute()
    
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error getting drug info: {response.error}")
    
    return response.data


def get_dosage_info(drug_name: str, age_group: str) -> List[Dict[str, Any]]:
    """
    Get dosage information for a specific drug and age group
    
    Args:
        drug_name: The drug name to search for
        age_group: The age group (e.g., "CHILDREN 7-11 YR")
        
    Returns:
        List of matching dosages
    """
    response = supabase.table("nelson_dosages").select("""
        id,
        age_group,
        route,
        value,
        max_dose,
        frequency,
        special_considerations,
        nelson_drugs!inner(drug_name, drug_brand_name, drug_formulations)
    """).eq("nelson_drugs.drug_name", drug_name).ilike("age_group", f"%{age_group}%").limit(10).execute()
    
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error getting dosage info: {response.error}")
    
    return response.data


def get_content_by_type(content_type: str, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get content by type (e.g., epidemiology, clinical_manifestations)
    
    Args:
        content_type: The content type to search for
        query: Optional search query within the content type
        limit: Maximum number of results to return
        
    Returns:
        List of matching content blocks
    """
    query_builder = supabase.table("nelson_content").select("""
        id,
        title,
        content_text,
        content_type,
        nelson_chapters(chapter_number, title),
        nelson_sections(section_number, title),
        nelson_subsections(subsection_number, title)
    """).eq("content_type", content_type).limit(limit)
    
    if query:
        query_builder = query_builder.text_search("content_text", query)
    
    response = query_builder.execute()
    
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error getting content by type: {response.error}")
    
    return response.data


def get_content_structure() -> List[Dict[str, Any]]:
    """
    Get hierarchical content structure (chapters, sections, subsections)
    
    Returns:
        List of chapters with nested sections and subsections
    """
    response = supabase.table("nelson_chapters").select("""
        id,
        chapter_number,
        title,
        nelson_sections(
            id,
            section_number,
            title,
            nelson_subsections(
                id,
                subsection_number,
                title
            )
        )
    """).order("chapter_number", {"ascending": True}).execute()
    
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error getting content structure: {response.error}")
    
    return response.data


def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding for a text using OpenAI
    
    Args:
        text: The text to generate an embedding for
        
    Returns:
        The embedding vector
    """
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    
    return response["data"][0]["embedding"]


def example_rag_query(user_query: str) -> Dict[str, Any]:
    """
    Example RAG query using the Nelson Pediatrics database
    
    Args:
        user_query: The user's query
        
    Returns:
        Dictionary with relevant content and formatted context
    """
    try:
        # 1. Generate embedding for user query
        embedding = generate_embedding(user_query)
        
        # 2. Search for relevant content using vector similarity
        relevant_content = search_by_similarity(embedding, 5, 0.7)
        
        # 3. Format content for RAG
        context = "\n".join([
            f"""
Title: {item['title']}
Type: {item['content_type']}
Content: {item['content_text']}
Similarity: {item['similarity']}
---
"""
            for item in relevant_content
        ])
        
        # 4. Return formatted context for use in RAG
        return {
            "relevant_content": relevant_content,
            "formatted_context": context
        }
    except Exception as e:
        print(f"Error in RAG query: {e}")
        raise


# SQL to create the match function in Supabase
MATCH_FUNCTION_SQL = """
-- Create a function to match content by vector similarity
CREATE OR REPLACE FUNCTION match_nelson_content(
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id bigint,
  title text,
  content_text text,
  content_type text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    nelson_content.id,
    nelson_content.title,
    nelson_content.content_text,
    nelson_content.content_type,
    1 - (nelson_content.content_embedding <=> query_embedding) AS similarity
  FROM nelson_content
  WHERE 1 - (nelson_content.content_embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
"""


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Query the Nelson Pediatrics database")
    parser.add_argument("--query", required=True, help="The query to search for")
    parser.add_argument("--type", choices=["text", "similarity"], default="text", help="Search type")
    
    args = parser.parse_args()
    
    if args.type == "text":
        results = search_by_text(args.query)
        print(f"Found {len(results)} results for text search: {args.query}")
        for result in results:
            print(f"Title: {result['title']}")
            print(f"Type: {result['content_type']}")
            print(f"Content: {result['content_text'][:100]}...")
            print("---")
    else:
        # Generate embedding and search by similarity
        embedding = generate_embedding(args.query)
        results = search_by_similarity(embedding)
        print(f"Found {len(results)} results for similarity search: {args.query}")
        for result in results:
            print(f"Title: {result['title']}")
            print(f"Type: {result['content_type']}")
            print(f"Similarity: {result['similarity']}")
            print(f"Content: {result['content_text'][:100]}...")
            print("---")

