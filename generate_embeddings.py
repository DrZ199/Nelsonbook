#!/usr/bin/env python3
"""
Generate Embeddings for Nelson Textbook of Pediatrics

This script generates embeddings for the parsed Nelson Textbook of Pediatrics data
to enable semantic search in Supabase.
"""

import os
import json
import argparse
import time
from typing import Dict, List, Any, Optional

# Note: You'll need to install these dependencies:
# pip install openai numpy tqdm

try:
    import numpy as np
    from tqdm import tqdm
    import openai
except ImportError:
    print("Please install required dependencies:")
    print("pip install openai numpy tqdm")
    exit(1)

class EmbeddingGenerator:
    """Generate embeddings for Nelson content"""
    
    def __init__(self, data_dir: str, output_dir: str, api_key: Optional[str] = None, model: str = "text-embedding-ada-002"):
        """Initialize with data directory, output directory, and OpenAI API key"""
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.model = model
        
        # Set up OpenAI API
        if api_key:
            openai.api_key = api_key
        elif os.environ.get("OPENAI_API_KEY"):
            openai.api_key = os.environ.get("OPENAI_API_KEY")
        else:
            print("Warning: No OpenAI API key provided. Please set OPENAI_API_KEY environment variable or provide via --api-key.")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def load_data(self, file_name: str) -> List[Dict[str, Any]]:
        """Load data from a JSON file"""
        file_path = os.path.join(self.data_dir, file_name)
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} does not exist")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_embeddings(self):
        """Generate embeddings for all content blocks"""
        # Load content blocks
        content_blocks = self.load_data('content_blocks.json')
        
        if not content_blocks:
            print("No content blocks found. Run the parser first.")
            return
        
        print(f"Generating embeddings for {len(content_blocks)} content blocks...")
        
        # Process content blocks in batches to avoid rate limits
        batch_size = 100
        batches = [content_blocks[i:i + batch_size] for i in range(0, len(content_blocks), batch_size)]
        
        all_embeddings = []
        
        for batch_idx, batch in enumerate(tqdm(batches, desc="Processing batches")):
            # Prepare texts for embedding
            texts = []
            for content in batch:
                # Combine title and content for better semantic representation
                title = content.get('title', '')
                content_text = content.get('content_text', '')
                combined_text = f"{title}\n\n{content_text}"
                texts.append(combined_text)
            
            # Generate embeddings
            try:
                response = openai.Embedding.create(
                    input=texts,
                    model=self.model
                )
                
                # Extract embeddings
                batch_embeddings = [item['embedding'] for item in response['data']]
                all_embeddings.extend(batch_embeddings)
                
                # Add embeddings to content blocks
                for i, embedding in enumerate(batch_embeddings):
                    idx = batch_idx * batch_size + i
                    if idx < len(content_blocks):
                        content_blocks[idx]['embedding'] = embedding
                
                # Sleep to avoid rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error generating embeddings for batch {batch_idx}: {e}")
                # Continue with next batch
                continue
        
        # Save content blocks with embeddings
        output_path = os.path.join(self.output_dir, 'content_blocks_with_embeddings.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(content_blocks, f, indent=2)
        
        print(f"Generated {len(all_embeddings)} embeddings and saved to {output_path}")
        
        # Generate SQL update statements for embeddings
        self.generate_embedding_sql(content_blocks)
    
    def generate_embedding_sql(self, content_blocks: List[Dict[str, Any]]):
        """Generate SQL update statements for embeddings"""
        output_path = os.path.join(self.output_dir, 'embedding_updates.sql')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("-- Update content embeddings\n\n")
            
            for i, content in enumerate(content_blocks):
                if 'embedding' in content:
                    # Convert embedding to SQL array format
                    embedding_str = str(content['embedding']).replace('[', '{').replace(']', '}')
                    
                    # Write SQL update statement
                    f.write(f"UPDATE nelson_content SET content_embedding = '{embedding_str}'::vector WHERE id = {i + 1};\n")
            
            # Add index for vector similarity search
            f.write("\n-- Create vector similarity search index\n")
            f.write("CREATE INDEX IF NOT EXISTS nelson_content_embedding_idx ON nelson_content USING ivfflat (content_embedding vector_cosine_ops);\n")
        
        print(f"Generated embedding SQL updates and saved to {output_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate embeddings for Nelson content")
    parser.add_argument("--data-dir", default="parsed_data", help="Directory containing parsed data")
    parser.add_argument("--output-dir", default="embeddings", help="Directory to save embeddings")
    parser.add_argument("--api-key", help="OpenAI API key (optional, can use OPENAI_API_KEY env var)")
    parser.add_argument("--model", default="text-embedding-ada-002", help="OpenAI embedding model to use")
    
    args = parser.parse_args()
    
    # Create embedding generator and generate embeddings
    generator = EmbeddingGenerator(args.data_dir, args.output_dir, args.api_key, args.model)
    generator.generate_embeddings()
    
    print("Embedding generation complete!")


if __name__ == "__main__":
    main()

