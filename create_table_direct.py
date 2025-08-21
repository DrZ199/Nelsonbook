#!/usr/bin/env python3
"""
Create Table Directly in Supabase

This script creates the nelson_pediatrics table directly in Supabase using the REST API.
"""

import os
import requests
import json

def create_table_direct():
    """Create table directly in Supabase"""
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    print(f"Connecting to Supabase at {supabase_url}...")
    
    # Read the SQL file
    with open("create_table.sql", "r") as f:
        sql = f.read()
    
    # Create the table using the REST API
    print("Creating table...")
    
    # Construct the URL for the SQL API
    url = f"{supabase_url}/rest/v1/sql"
    
    # Set up headers
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Set up data
    data = {
        "query": sql
    }
    
    # Make the request
    response = requests.post(url, headers=headers, json=data)
    
    # Check the response
    if response.status_code == 200:
        print("Table created successfully")
    else:
        print(f"Error creating table: {response.status_code} {response.text}")

if __name__ == "__main__":
    create_table_direct()

