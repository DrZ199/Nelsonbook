#!/usr/bin/env python3
"""
Create Clean Table in Supabase

This script creates the nelson_pediatrics_clean table in Supabase using direct SQL.
"""

import os
import psycopg2
from urllib.parse import urlparse

def create_table():
    """Create the nelson_pediatrics_clean table in Supabase using direct PostgreSQL connection"""
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    # Parse the Supabase URL to get the host
    parsed_url = urlparse(supabase_url)
    host = parsed_url.netloc
    
    # Connect to the database
    print(f"Connecting to Supabase at {host}...")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=5432,
            dbname="postgres",
            user="postgres",
            password=supabase_key
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
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
        print("Creating table nelson_pediatrics_clean...")
        cursor.execute(create_table_sql)
        
        # Execute the SQL to create the index
        print("Creating search index...")
        cursor.execute(create_index_sql)
        
        # Commit the changes
        conn.commit()
        
        print("Table creation completed.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_table()

