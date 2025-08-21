#!/usr/bin/env python3
"""
Example Usage of Nelson Pediatrics Database

This script demonstrates how to use the Nelson Pediatrics database parser,
SQL generator, and RAG helper to create and query a Supabase database.
"""

import os
import argparse
import subprocess
from nelson_parser import NelsonParser
from generate_supabase_sql import SqlGenerator
from generate_embeddings import EmbeddingGenerator
from supabase_rag_helper import example_rag_query

def parse_nelson_files(input_dir, output_dir):
    """Parse Nelson files and extract structured data"""
    print(f"Parsing Nelson files from {input_dir}...")
    
    # Get all nelson part files
    input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) 
                  if f.startswith('nelson_part_') and f.endswith('.txt')]
    input_files.sort()
    
    # Initialize and run parser
    parser = NelsonParser(input_files, output_dir)
    parser.parse_files()
    
    print(f"Parsing complete! Data saved to {output_dir}")


def generate_sql(data_dir, output_file):
    """Generate SQL for Supabase"""
    print(f"Generating SQL from {data_dir}...")
    
    # Create SQL generator and generate SQL
    generator = SqlGenerator(data_dir, output_file)
    generator.generate_sql()
    
    print(f"SQL generation complete! SQL saved to {output_file}")


def generate_embeddings(data_dir, output_dir, api_key=None):
    """Generate embeddings for content blocks"""
    print(f"Generating embeddings for content in {data_dir}...")
    
    # Create embedding generator and generate embeddings
    generator = EmbeddingGenerator(data_dir, output_dir, api_key)
    generator.generate_embeddings()
    
    print(f"Embedding generation complete! Embeddings saved to {output_dir}")


def import_to_supabase(sql_file, embedding_sql_file, supabase_url, supabase_key):
    """Import data to Supabase"""
    print(f"Importing data to Supabase...")
    
    # Use the Supabase CLI to import data
    # Note: This requires the Supabase CLI to be installed
    # https://supabase.com/docs/guides/cli
    
    # Set environment variables
    os.environ["SUPABASE_URL"] = supabase_url
    os.environ["SUPABASE_KEY"] = supabase_key
    
    # Import schema and data
    subprocess.run(["supabase", "db", "execute", "--file", sql_file])
    
    # Import embeddings
    subprocess.run(["supabase", "db", "execute", "--file", embedding_sql_file])
    
    print("Data import complete!")


def query_example(query, supabase_url, supabase_key, openai_api_key):
    """Run an example query against the database"""
    print(f"Running example query: {query}")
    
    # Set environment variables
    os.environ["SUPABASE_URL"] = supabase_url
    os.environ["SUPABASE_ANON_KEY"] = supabase_key
    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # Run the example query
    result = example_rag_query(query)
    
    print("\nRelevant content:")
    for item in result["relevant_content"]:
        print(f"- {item['title']} (Similarity: {item['similarity']:.2f})")
    
    print("\nFormatted context for RAG:")
    print(result["formatted_context"])


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Nelson Pediatrics Database Example")
    parser.add_argument("--action", choices=["parse", "sql", "embeddings", "import", "query", "all"], 
                        required=True, help="Action to perform")
    parser.add_argument("--input-dir", default=".", help="Directory containing Nelson text files")
    parser.add_argument("--data-dir", default="parsed_data", help="Directory for parsed data")
    parser.add_argument("--output-dir", default="embeddings", help="Directory for embeddings")
    parser.add_argument("--sql-file", default="nelson_supabase.sql", help="Output SQL file")
    parser.add_argument("--embedding-sql-file", default="embeddings/embedding_updates.sql", 
                        help="Embedding SQL file")
    parser.add_argument("--supabase-url", help="Supabase URL")
    parser.add_argument("--supabase-key", help="Supabase key")
    parser.add_argument("--openai-api-key", help="OpenAI API key")
    parser.add_argument("--query", help="Query for example")
    
    args = parser.parse_args()
    
    # Create directories if they don't exist
    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Perform the requested action
    if args.action == "parse" or args.action == "all":
        parse_nelson_files(args.input_dir, args.data_dir)
    
    if args.action == "sql" or args.action == "all":
        generate_sql(args.data_dir, args.sql_file)
    
    if args.action == "embeddings" or args.action == "all":
        if not args.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
            print("Error: OpenAI API key is required for generating embeddings")
            print("Please provide it with --openai-api-key or set the OPENAI_API_KEY environment variable")
            return
        generate_embeddings(args.data_dir, args.output_dir, args.openai_api_key)
    
    if args.action == "import" or args.action == "all":
        if not args.supabase_url or not args.supabase_key:
            print("Error: Supabase URL and key are required for importing data")
            print("Please provide them with --supabase-url and --supabase-key")
            return
        import_to_supabase(args.sql_file, args.embedding_sql_file, args.supabase_url, args.supabase_key)
    
    if args.action == "query":
        if not args.query:
            print("Error: Query is required for example query")
            print("Please provide it with --query")
            return
        if not args.supabase_url or not args.supabase_key or not args.openai_api_key:
            print("Error: Supabase URL, key, and OpenAI API key are required for querying")
            print("Please provide them with --supabase-url, --supabase-key, and --openai-api-key")
            return
        query_example(args.query, args.supabase_url, args.supabase_key, args.openai_api_key)


if __name__ == "__main__":
    main()

