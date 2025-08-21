#!/usr/bin/env python3
"""
Check Upload Progress

This script checks the progress of the upload by counting the number of rows in the Supabase table.
"""

import os
import argparse
from supabase import create_client, Client

def check_progress(total_rows=445063):
    """Check the progress of the upload"""
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    print(f"Connecting to Supabase at {supabase_url}...")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Count the number of rows in the table
    print("Counting rows in the table...")
    try:
        response = supabase.table("nelson_pediatrics").select("id", count="exact").execute()
        
        # Get the count
        count = response.count
        
        # Calculate the progress
        progress = count / total_rows * 100
        
        print(f"Progress: {progress:.2f}% ({count}/{total_rows})")
        
    except Exception as e:
        print(f"Error counting rows: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Check Upload Progress")
    parser.add_argument("--total-rows", type=int, default=445063, help="Total number of rows to upload")
    
    args = parser.parse_args()
    
    # Check the progress
    check_progress(args.total_rows)

if __name__ == "__main__":
    main()

