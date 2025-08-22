#!/usr/bin/env python3
"""
Upload Clean Dataset to Supabase

This script creates a table in Supabase and uploads the clean dataset.
"""

import os
import csv
import time
import argparse
import requests
from supabase import create_client, Client

def create_table(supabase_url, supabase_key):
    """Create the nelson_pediatrics_clean table in Supabase"""
    print(f"Creating table nelson_pediatrics_clean in Supabase at {supabase_url}...")
    
    # SQL to create the table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS nelson_pediatrics_clean (
        id SERIAL PRIMARY KEY,
        chapter_number TEXT NOT NULL,
        chapter_title TEXT NOT NULL,
        section_title TEXT NOT NULL,
        subsection_title TEXT NOT NULL,
        topic_title TEXT NOT NULL,
        background TEXT NOT NULL,
        epidemiology TEXT NOT NULL,
        pathophysiology TEXT NOT NULL,
        clinical_presentation TEXT NOT NULL,
        diagnostics TEXT NOT NULL,
        differential_diagnoses TEXT NOT NULL,
        management TEXT NOT NULL,
        prevention TEXT NOT NULL,
        notes TEXT NOT NULL,
        drug_name TEXT NOT NULL,
        drug_indication TEXT NOT NULL,
        drug_mechanism TEXT NOT NULL,
        drug_adverse_effects TEXT NOT NULL,
        drug_contraindications TEXT NOT NULL,
        dosage_age_group TEXT NOT NULL,
        dosage_route TEXT NOT NULL,
        dosage_value TEXT NOT NULL,
        dosage_max TEXT NOT NULL,
        dosage_frequency TEXT NOT NULL,
        dosage_special_considerations TEXT NOT NULL,
        procedure_name TEXT NOT NULL,
        procedure_steps TEXT NOT NULL,
        procedure_complications TEXT NOT NULL,
        procedure_equipment TEXT NOT NULL,
        algorithm_title TEXT NOT NULL,
        algorithm_description TEXT NOT NULL,
        algorithm_flowchart_url TEXT NOT NULL,
        reference_citation TEXT NOT NULL,
        reference_doi TEXT NOT NULL,
        reference_url TEXT NOT NULL,
        media_url TEXT NOT NULL,
        media_type TEXT NOT NULL,
        media_caption TEXT NOT NULL,
        revised_by TEXT NOT NULL,
        revision_notes TEXT NOT NULL,
        revision_date TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    # SQL to create the index
    create_index_sql = """
    CREATE INDEX IF NOT EXISTS nelson_pediatrics_clean_search_idx ON nelson_pediatrics_clean 
    USING GIN (to_tsvector('english', 
        chapter_title || ' ' || 
        section_title || ' ' || 
        subsection_title || ' ' || 
        topic_title || ' ' || 
        background || ' ' || 
        epidemiology || ' ' || 
        pathophysiology || ' ' || 
        clinical_presentation || ' ' || 
        diagnostics || ' ' || 
        differential_diagnoses || ' ' || 
        management || ' ' || 
        prevention || ' ' || 
        notes || ' ' || 
        drug_name || ' ' || 
        drug_indication || ' ' || 
        drug_mechanism || ' ' || 
        drug_adverse_effects || ' ' || 
        drug_contraindications
    ));
    """
    
    # Connect to Supabase
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Check if the table exists
    try:
        # Try to get a single row from the table
        supabase.table("nelson_pediatrics_clean").select("*").limit(1).execute()
        print("Table nelson_pediatrics_clean already exists")
        return True
    except Exception as e:
        print(f"Table nelson_pediatrics_clean does not exist: {e}")
        
        # Try to create the table using the REST API
        try:
            # Use the REST API to execute SQL
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            
            # Execute the SQL to create the table
            print("Creating table using REST API...")
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/execute_sql",
                headers=headers,
                json={"query": create_table_sql}
            )
            
            if response.status_code == 200:
                print("Table created successfully")
            else:
                print(f"Error creating table: {response.status_code} - {response.text}")
                print("Please create the table manually using the Supabase dashboard SQL editor")
                print(create_table_sql)
                print(create_index_sql)
                return False
            
            # Execute the SQL to create the index
            print("Creating index...")
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/execute_sql",
                headers=headers,
                json={"query": create_index_sql}
            )
            
            if response.status_code == 200:
                print("Index created successfully")
                return True
            else:
                print(f"Error creating index: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error creating table: {e}")
            print("Please create the table manually using the Supabase dashboard SQL editor")
            print(create_table_sql)
            print(create_index_sql)
            return False

def upload_dataset(supabase_url, supabase_key, file_path, batch_size=1000, delay_seconds=3):
    """Upload the dataset to Supabase"""
    print(f"Uploading dataset from {file_path} to Supabase...")
    
    # Connect to Supabase
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Read the dataset
    print(f"Reading {file_path}...")
    rows = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    
    total_rows = len(rows)
    print(f"Total rows to process: {total_rows}")
    
    # Process the rows in batches
    batch_count = 0
    rows_processed = 0
    
    while rows_processed < total_rows:
        # Get the current batch
        batch_end = min(rows_processed + batch_size, total_rows)
        current_batch = rows[rows_processed:batch_end]
        batch_count += 1
        
        print(f"Processing batch {batch_count} (rows {rows_processed+1}-{batch_end})...")
        
        try:
            # Upload the batch
            print(f"Uploading batch {batch_count}...")
            supabase.table("nelson_pediatrics_clean").insert(current_batch).execute()
            print(f"Successfully uploaded batch {batch_count}")
            
            # Update the rows processed
            rows_processed = batch_end
            
            # Print progress
            progress = rows_processed / total_rows * 100
            print(f"Progress: {progress:.2f}% ({rows_processed}/{total_rows})")
            
            # Sleep to avoid rate limits
            if rows_processed < total_rows:
                print(f"Sleeping for {delay_seconds} seconds to avoid rate limits...")
                time.sleep(delay_seconds)
        except Exception as e:
            print(f"Error uploading batch {batch_count}: {e}")
            
            # Try with a smaller batch size
            if batch_size > 10:
                new_batch_size = batch_size // 2
                print(f"Reducing batch size to {new_batch_size} and retrying...")
                batch_size = new_batch_size
            else:
                print("Batch size already at minimum. Skipping to next batch.")
                rows_processed = batch_end
    
    print(f"Upload completed. {rows_processed} rows processed.")
    return rows_processed

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Upload clean dataset to Supabase")
    parser.add_argument("--file", default="clean_dataset.csv", help="Input file (default: clean_dataset.csv)")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size (default: 1000)")
    parser.add_argument("--delay-seconds", type=int, default=3, help="Delay between batches in seconds (default: 3)")
    
    args = parser.parse_args()
    
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    # Create the table
    if create_table(supabase_url, supabase_key):
        # Upload the dataset
        upload_dataset(supabase_url, supabase_key, args.file, args.batch_size, args.delay_seconds)
    else:
        print("Table creation failed. Please create the table manually and try again.")

if __name__ == "__main__":
    main()

