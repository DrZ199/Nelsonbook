#!/usr/bin/env python3
"""
Create Table and Upload Sample Data to Supabase

This script creates the nelson_pediatrics table in Supabase and uploads a sample of data.
"""

import os
import pandas as pd
from supabase import create_client, Client

def create_table_and_upload():
    """Create table and upload sample data"""
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
    df = pd.read_csv("dataset.csv", nrows=100)  # Read first 100 rows
    
    # Clean data - replace NaN with empty string
    for column in df.columns:
        df[column] = df[column].fillna("")
    
    # Convert to list of dictionaries
    sample_data = df.to_dict(orient='records')
    
    # Create the table
    print("Creating table...")
    try:
        # Create the table using the REST API
        # This is a simplified approach - for a complete schema, use the SQL Editor
        
        # First, check if the table exists
        try:
            response = supabase.table("nelson_pediatrics").select("*").limit(1).execute()
            print("Table already exists")
        except Exception as e:
            if "relation" in str(e) and "does not exist" in str(e):
                print("Table doesn't exist, creating it...")
                
                # Create the table using the REST API
                # This is a simplified approach - for a complete schema, use the SQL Editor
                
                # Get column names from the sample data
                columns = list(sample_data[0].keys())
                
                # Create a SQL statement to create the table
                create_table_sql = "CREATE TABLE nelson_pediatrics (\n"
                create_table_sql += "    id BIGSERIAL PRIMARY KEY,\n"
                
                for column in columns:
                    create_table_sql += f"    {column} TEXT,\n"
                
                create_table_sql += "    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),\n"
                create_table_sql += "    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()\n"
                create_table_sql += ");"
                
                # Write the SQL to a file
                with open("create_table.sql", "w") as f:
                    f.write(create_table_sql)
                
                print("SQL statement written to create_table.sql")
                print("Please run this SQL statement in the Supabase SQL Editor")
                print("Then run this script again to upload the sample data")
                return
            else:
                print(f"Error: {e}")
                return
        
        # Upload sample data
        print(f"Uploading {len(sample_data)} rows of sample data...")
        result = supabase.table("nelson_pediatrics").insert(sample_data).execute()
        
        # Check for errors
        if hasattr(result, 'error') and result.error:
            print(f"Error uploading data: {result.error}")
        else:
            print("Sample data uploaded successfully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_table_and_upload()

