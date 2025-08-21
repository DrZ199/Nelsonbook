#!/usr/bin/env python3
"""
Upload Nelson Pediatrics Dataset to Supabase

This script uploads the dataset.csv file to Supabase using the provided credentials.
"""

import os
import csv
import time
import argparse
from typing import List, Dict, Any
import pandas as pd
from supabase import create_client, Client

def create_table(supabase: Client, table_name: str):
    """
    Create the table in Supabase
    
    Args:
        supabase: Supabase client
        table_name: Name of the table to create
    """
    print(f"Creating table {table_name}...")
    
    # Create the table using the REST API
    # Note: This is a simplified version of the table schema
    # For a complete schema, you would need to use the SQL Editor in the Supabase dashboard
    
    try:
        # Check if table exists
        response = supabase.table(table_name).select("count(*)", count="exact").limit(1).execute()
        print(f"Table {table_name} already exists with {response.count} rows")
        return True
    except Exception as e:
        # Table doesn't exist, create it
        print(f"Table {table_name} doesn't exist, creating it...")
        
        # Read the first row of the CSV to get column names
        df = pd.read_csv("dataset.csv", nrows=1)
        columns = df.columns.tolist()
        
        # Create a simple table with all columns as text
        # For a more complex schema, use the SQL Editor in the Supabase dashboard
        try:
            # Create the table using the REST API
            # This is a simplified approach - for a complete schema, use the SQL Editor
            response = supabase.rpc(
                "create_nelson_table",
                {
                    "table_name": table_name,
                    "columns": columns
                }
            ).execute()
            
            print(f"Table {table_name} created successfully")
            return True
        except Exception as e:
            print(f"Error creating table: {e}")
            print("Please create the table manually using the SQL Editor in the Supabase dashboard")
            print("You can use the create_supabase_table.sql file as a reference")
            return False

def upload_to_supabase(csv_file: str, batch_size: int = 1000, table_name: str = "nelson_pediatrics"):
    """
    Upload CSV data to Supabase
    
    Args:
        csv_file: Path to the CSV file
        batch_size: Number of rows to upload in each batch
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
    
    # Create the table if it doesn't exist
    # Note: For a complete schema, use the SQL Editor in the Supabase dashboard
    # This is just a simplified approach for demonstration purposes
    try:
        # Try to select from the table to see if it exists
        response = supabase.table(table_name).select("count(*)", count="exact").limit(1).execute()
        print(f"Table {table_name} already exists with {response.count} rows")
    except Exception as e:
        print(f"Table {table_name} doesn't exist or error occurred: {e}")
        print("Please create the table manually using the SQL Editor in the Supabase dashboard")
        print("You can use the create_supabase_table.sql file as a reference")
        return
    
    # Read CSV file in batches
    print(f"Reading {csv_file} in batches of {batch_size}...")
    
    # Use pandas to read the CSV file
    df = pd.read_csv(csv_file, encoding='utf-8')
    total_rows = len(df)
    print(f"Total rows to upload: {total_rows}")
    
    # Process in batches
    num_batches = (total_rows + batch_size - 1) // batch_size
    
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, total_rows)
        
        print(f"Processing batch {i+1}/{num_batches} (rows {start_idx+1}-{end_idx})...")
        
        # Get batch as list of dictionaries
        batch_df = df.iloc[start_idx:end_idx]
        batch_data = batch_df.to_dict(orient='records')
        
        # Clean data - replace NaN with empty string
        for row in batch_data:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = ""
        
        try:
            # Upload batch to Supabase
            result = supabase.table(table_name).insert(batch_data).execute()
            
            # Check for errors
            if hasattr(result, 'error') and result.error:
                print(f"Error uploading batch {i+1}: {result.error}")
            else:
                print(f"Successfully uploaded batch {i+1}/{num_batches}")
            
            # Sleep to avoid rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error uploading batch {i+1}: {e}")
    
    print("Upload complete!")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Upload Nelson Pediatrics Dataset to Supabase")
    parser.add_argument("--csv-file", default="dataset.csv", help="Path to the CSV file")
    parser.add_argument("--batch-size", type=int, default=1000, help="Number of rows to upload in each batch")
    parser.add_argument("--table-name", default="nelson_pediatrics", help="Name of the table to upload to")
    
    args = parser.parse_args()
    
    # Upload to Supabase
    upload_to_supabase(args.csv_file, args.batch_size, args.table_name)

if __name__ == "__main__":
    main()

