#!/usr/bin/env python3
"""
Create Table in Supabase

This script creates the nelson_pediatrics table in Supabase using the Supabase client.
"""

import os
import pandas as pd
from supabase import create_client, Client

def create_table():
    """Create table in Supabase"""
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    print(f"Connecting to Supabase at {supabase_url}...")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Create a sample of data
    print("Creating sample data...")
    df = pd.read_csv("dataset.csv", nrows=10)  # Read first 10 rows
    
    # Clean data - replace NaN with empty string
    for column in df.columns:
        df[column] = df[column].fillna("")
    
    # Convert to list of dictionaries
    sample_data = df.to_dict(orient='records')
    
    # Try to create the table
    print("Attempting to create table...")
    try:
        # Try to insert data - this will fail if the table doesn't exist
        result = supabase.table("nelson_pediatrics").insert(sample_data).execute()
        print("Table already exists and data inserted successfully")
    except Exception as e:
        print(f"Error: {e}")
        print("Please create the table manually using the SQL Editor in the Supabase dashboard")
        print("You can use the create_table.sql file as a reference")

if __name__ == "__main__":
    create_table()

