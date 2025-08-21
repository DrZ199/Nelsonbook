#!/usr/bin/env python3
"""
Batch Upload to Supabase with Rate Limiting

This script uploads the Nelson Pediatrics dataset to Supabase in small batches
with delays between batches to avoid hitting rate limits.
"""

import os
import time
import argparse
import pandas as pd
from supabase import create_client, Client

def batch_upload(csv_file, batch_size=50, delay_seconds=2, table_name="nelson_pediatrics"):
    """
    Upload CSV data to Supabase in batches with rate limiting
    
    Args:
        csv_file: Path to the CSV file
        batch_size: Number of rows to upload in each batch
        delay_seconds: Delay between batches in seconds
        table_name: Name of the table to upload to
    """
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    print(f"Connecting to Supabase at {supabase_url}...")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Check if table exists
    print(f"Checking if table {table_name} exists...")
    try:
        response = supabase.table(table_name).select("*").limit(1).execute()
        print(f"Table {table_name} exists")
    except Exception as e:
        print(f"Error: {e}")
        print("Please create the table manually using the SQL Editor in the Supabase dashboard")
        print("You can use the create_table.sql file as a reference")
        return
    
    # Read CSV file
    print(f"Reading {csv_file}...")
    
    # Use pandas to read the CSV file in chunks
    chunk_size = 1000  # Read in chunks to avoid memory issues
    total_rows_processed = 0
    total_rows_uploaded = 0
    
    # Get total number of rows
    total_rows = sum(1 for _ in open(csv_file)) - 1  # Subtract header row
    print(f"Total rows to process: {total_rows}")
    
    # Process in chunks
    for chunk_num, chunk in enumerate(pd.read_csv(csv_file, chunksize=chunk_size)):
        print(f"Processing chunk {chunk_num+1} (rows {total_rows_processed+1}-{total_rows_processed+len(chunk)})...")
        
        # Clean data - replace NaN with empty string
        for column in chunk.columns:
            chunk[column] = chunk[column].fillna("")
        
        # Process in batches
        for i in range(0, len(chunk), batch_size):
            batch_df = chunk.iloc[i:i+batch_size]
            batch_data = batch_df.to_dict(orient='records')
            
            batch_num = total_rows_processed // batch_size + 1
            start_idx = total_rows_processed + 1
            end_idx = total_rows_processed + len(batch_data)
            
            print(f"Uploading batch {batch_num} (rows {start_idx}-{end_idx})...")
            
            # Upload batch to Supabase
            try:
                result = supabase.table(table_name).insert(batch_data).execute()
                
                # Check for errors
                if hasattr(result, 'error') and result.error:
                    print(f"Error uploading batch {batch_num}: {result.error}")
                else:
                    print(f"Successfully uploaded batch {batch_num}")
                    total_rows_uploaded += len(batch_data)
                
                # Sleep to avoid rate limits
                print(f"Sleeping for {delay_seconds} seconds to avoid rate limits...")
                time.sleep(delay_seconds)
                
            except Exception as e:
                print(f"Error uploading batch {batch_num}: {e}")
                print("Retrying in 10 seconds...")
                time.sleep(10)
                
                try:
                    result = supabase.table(table_name).insert(batch_data).execute()
                    
                    # Check for errors
                    if hasattr(result, 'error') and result.error:
                        print(f"Error uploading batch {batch_num} (retry): {result.error}")
                    else:
                        print(f"Successfully uploaded batch {batch_num} (retry)")
                        total_rows_uploaded += len(batch_data)
                    
                    # Sleep to avoid rate limits
                    print(f"Sleeping for {delay_seconds} seconds to avoid rate limits...")
                    time.sleep(delay_seconds)
                    
                except Exception as e:
                    print(f"Error uploading batch {batch_num} (retry): {e}")
                    print("Skipping batch and continuing...")
            
            total_rows_processed += len(batch_data)
            
            # Print progress
            progress = total_rows_processed / total_rows * 100
            print(f"Progress: {progress:.2f}% ({total_rows_processed}/{total_rows})")
    
    print(f"Upload complete! Uploaded {total_rows_uploaded} rows out of {total_rows}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Batch Upload to Supabase with Rate Limiting")
    parser.add_argument("--csv-file", default="dataset.csv", help="Path to the CSV file")
    parser.add_argument("--batch-size", type=int, default=50, help="Number of rows to upload in each batch")
    parser.add_argument("--delay-seconds", type=int, default=2, help="Delay between batches in seconds")
    parser.add_argument("--table-name", default="nelson_pediatrics", help="Name of the table to upload to")
    
    args = parser.parse_args()
    
    # Upload to Supabase
    batch_upload(args.csv_file, args.batch_size, args.delay_seconds, args.table_name)

if __name__ == "__main__":
    main()

