#!/usr/bin/env python3
"""
Check Progress of Upload to Supabase

This script checks the progress of the upload to Supabase.
"""

import os
from supabase import create_client, Client

def check_progress():
    """Check the progress of the upload to Supabase"""
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    # Connect to Supabase
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Check the progress
    try:
        # Get the count of rows in the table
        response = supabase.table("nelson_pediatrics_clean").select("*", count="exact").execute()
        count = response.count
        print(f"Total rows in nelson_pediatrics_clean: {count}")
        
        # Get a sample of rows
        response = supabase.table("nelson_pediatrics_clean").select("*").limit(5).execute()
        rows = response.data
        
        print("\nSample rows:")
        for row in rows:
            print(f"Row ID: {row['id']}")
            print(f"Chapter: {row['chapter_number']} - {row['chapter_title']}")
            print(f"Section: {row['section_title']}")
            print(f"Topic: {row['topic_title']}")
            print("---")
        
        return count
    except Exception as e:
        print(f"Error checking progress: {e}")
        return None

if __name__ == "__main__":
    check_progress()

