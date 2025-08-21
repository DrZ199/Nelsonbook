#!/usr/bin/env python3
"""
Setup Supabase for Nelson Pediatrics Dataset

This script sets up the Supabase database by running the SQL script to create the table.
"""

import os
import argparse
from supabase import create_client, Client

def setup_supabase(sql_file: str):
    """
    Setup Supabase by running the SQL script
    
    Args:
        sql_file: Path to the SQL file
    """
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    print(f"Connecting to Supabase at {supabase_url}...")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Read SQL file
    print(f"Reading SQL file {sql_file}...")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Split SQL into statements
    statements = sql.split(';')
    
    # Execute each statement
    for i, statement in enumerate(statements):
        if not statement.strip():
            continue
        
        print(f"Executing SQL statement {i+1}/{len(statements)}...")
        try:
            # Execute SQL statement
            result = supabase.rpc('exec_sql', {'sql': statement}).execute()
            
            # Check for errors
            if hasattr(result, 'error') and result.error:
                print(f"Error executing SQL statement {i+1}: {result.error}")
            else:
                print(f"Successfully executed SQL statement {i+1}")
            
        except Exception as e:
            print(f"Error executing SQL statement {i+1}: {e}")
    
    print("Setup complete!")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Setup Supabase for Nelson Pediatrics Dataset")
    parser.add_argument("--sql-file", default="create_supabase_table.sql", help="Path to the SQL file")
    
    args = parser.parse_args()
    
    # Setup Supabase
    setup_supabase(args.sql_file)

if __name__ == "__main__":
    main()

