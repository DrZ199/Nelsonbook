#!/usr/bin/env python3
"""
Create Table in Supabase using REST API

This script creates the nelson_pediatrics table in Supabase using the REST API.
"""

import os
import requests
import json

def create_table_rest():
    """Create table in Supabase using REST API"""
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    print(f"Connecting to Supabase at {supabase_url}...")
    
    # Read the SQL file
    with open("simple_table_creation.sql", "r") as f:
        sql = f.read()
    
    # Create the table using the REST API
    print("Creating table...")
    
    # Construct the URL for the SQL API
    url = f"{supabase_url}/rest/v1/rpc/exec_sql"
    
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
        print("You will need to create the table manually using the SQL Editor in the Supabase dashboard")
        print("Copy and paste the SQL from simple_table_creation.sql into the SQL Editor")

if __name__ == "__main__":
    create_table_rest()

