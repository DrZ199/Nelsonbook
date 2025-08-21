#!/usr/bin/env python3
"""
Test Supabase Connection

This script tests the connection to Supabase and checks if the table exists.
"""

import os
from supabase import create_client, Client

def test_supabase():
    """Test Supabase connection"""
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    print(f"Connecting to Supabase at {supabase_url}...")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Check if table exists
    print("Checking if table exists...")
    try:
        # Try to select a single row from the table
        response = supabase.table("nelson_pediatrics").select("*").limit(1).execute()
        print(f"Table exists with data: {response.data}")
    except Exception as e:
        print(f"Error: {e}")
        print("Please create the table manually using the SQL Editor in the Supabase dashboard")
        print("You can use the simple_table_creation.sql file as a reference")

if __name__ == "__main__":
    test_supabase()

