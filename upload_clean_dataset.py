#!/usr/bin/env python3
"""
Upload Clean Dataset to Supabase

This script uploads the clean dataset to Supabase.
"""

import os
import csv
import time
import argparse
from supabase import create_client, Client

def upload_dataset(supabase_url, supabase_key, file_path, batch_size=1000, delay_seconds=3):
    """Upload the dataset to Supabase"""
    print(f"Uploading dataset from {file_path} to Supabase...")
    
    # Connect to Supabase
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Read the dataset
    print(f"Reading {file_path}...")
    rows = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    
    total_rows = len(rows)
    print(f"Total rows to process: {total_rows}")
    
    # Process the rows in batches
    batch_count = 0
    rows_processed = 0
    
    while rows_processed < total_rows:
        # Get the current batch
        batch_end = min(rows_processed + batch_size, total_rows)
        current_batch = rows[rows_processed:batch_end]
        batch_count += 1
        
        print(f"Processing batch {batch_count} (rows {rows_processed+1}-{batch_end})...")
        
        try:
            # Upload the batch
            print(f"Uploading batch {batch_count}...")
            supabase.table("nelson_pediatrics_clean").insert(current_batch).execute()
            print(f"Successfully uploaded batch {batch_count}")
            
            # Update the rows processed
            rows_processed = batch_end
            
            # Print progress
            progress = rows_processed / total_rows * 100
            print(f"Progress: {progress:.2f}% ({rows_processed}/{total_rows})")
            
            # Sleep to avoid rate limits
            if rows_processed < total_rows:
                print(f"Sleeping for {delay_seconds} seconds to avoid rate limits...")
                time.sleep(delay_seconds)
        except Exception as e:
            print(f"Error uploading batch {batch_count}: {e}")
            
            # Try with a smaller batch size
            if batch_size > 10:
                new_batch_size = batch_size // 2
                print(f"Reducing batch size to {new_batch_size} and retrying...")
                batch_size = new_batch_size
            else:
                print("Batch size already at minimum. Skipping to next batch.")
                rows_processed = batch_end
    
    print(f"Upload completed. {rows_processed} rows processed.")
    return rows_processed

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Upload clean dataset to Supabase")
    parser.add_argument("--file", default="clean_dataset.csv", help="Input file (default: clean_dataset.csv)")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size (default: 1000)")
    parser.add_argument("--delay-seconds", type=int, default=3, help="Delay between batches in seconds (default: 3)")
    
    args = parser.parse_args()
    
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    # Upload the dataset
    upload_dataset(supabase_url, supabase_key, args.file, args.batch_size, args.delay_seconds)

if __name__ == "__main__":
    main()

