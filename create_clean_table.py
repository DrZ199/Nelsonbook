#!/usr/bin/env python3
"""
Create Clean Table in Supabase

This script creates the nelson_pediatrics_clean table in Supabase.
"""

import os
import requests
import json

def create_table():
    """Create the nelson_pediatrics_clean table in Supabase"""
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    print(f"Connecting to Supabase at {supabase_url}...")
    
    # Create the table using the REST API
    print("Creating table nelson_pediatrics_clean...")
    
    # SQL query to create the table
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
    
    # SQL query to create the index
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
    
    # Execute the SQL to create the table
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/rpc/execute_sql",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            },
            json={"query": create_table_sql}
        )
        
        if response.status_code == 200:
            print("Table created successfully")
        else:
            print(f"Error creating table: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error creating table: {e}")
    
    # Execute the SQL to create the index
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/rpc/execute_sql",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            },
            json={"query": create_index_sql}
        )
        
        if response.status_code == 200:
            print("Index created successfully")
        else:
            print(f"Error creating index: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error creating index: {e}")
    
    print("Table creation completed.")

if __name__ == "__main__":
    create_table()

