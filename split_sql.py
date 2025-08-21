#!/usr/bin/env python3
"""
Split SQL File into Smaller Chunks

This script splits the insert_data.sql file into smaller chunks that can be uploaded to Supabase.
"""

import os
import re

def split_sql_file(input_file, output_dir, chunk_size=10):
    """
    Split SQL file into smaller chunks
    
    Args:
        input_file: Path to the input SQL file
        output_dir: Path to the output directory
        chunk_size: Number of batches per chunk
    """
    print(f"Reading {input_file}...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the SQL file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the table creation statement
    table_creation = re.search(r'-- Create the nelson_pediatrics table.*?;', content, re.DOTALL)
    if table_creation:
        table_creation = table_creation.group(0)
    else:
        table_creation = ""
    
    # Split the content into batches
    batches = re.findall(r'-- Batch \d+/\d+ \(rows \d+-\d+\).*?;', content, re.DOTALL)
    
    print(f"Found {len(batches)} batches")
    
    # Split batches into chunks
    num_chunks = (len(batches) + chunk_size - 1) // chunk_size
    
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(batches))
        
        print(f"Processing chunk {i+1}/{num_chunks} (batches {start_idx+1}-{end_idx})...")
        
        # Create chunk content
        chunk_content = table_creation + "\n\n"
        chunk_content += "\n\n".join(batches[start_idx:end_idx])
        
        # Write chunk to file
        output_file = os.path.join(output_dir, f"chunk_{i+1:04d}.sql")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(chunk_content)
        
        print(f"Wrote chunk to {output_file}")
    
    print(f"Split {len(batches)} batches into {num_chunks} chunks")

def main():
    """Main function"""
    # Set input and output files
    input_file = "insert_data.sql"
    output_dir = "sql_chunks"
    chunk_size = 10
    
    # Split SQL file
    split_sql_file(input_file, output_dir, chunk_size)
    
    print("SQL file splitting complete!")

if __name__ == "__main__":
    main()

