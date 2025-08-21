#!/usr/bin/env python3
"""
Create Sample Dataset and Upload to Supabase

This script creates a small sample dataset and uploads it to Supabase.
"""

import os
import pandas as pd
from supabase import create_client, Client

def create_sample_and_upload():
    """Create sample dataset and upload to Supabase"""
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service key for more permissions
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return
    
    print(f"Connecting to Supabase at {supabase_url}...")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Create a sample dataset
    print("Creating sample dataset...")
    
    # Create a sample row
    sample_data = [{
        "chapter_number": "1",
        "chapter_title": "Sample Chapter",
        "section_title": "Sample Section",
        "subsection_title": "Sample Subsection",
        "topic_title": "Sample Topic",
        "background": "Sample background text",
        "epidemiology": "Sample epidemiology text",
        "pathophysiology": "Sample pathophysiology text",
        "clinical_presentation": "Sample clinical presentation text",
        "diagnostics": "Sample diagnostics text",
        "differential_diagnoses": "Sample differential diagnoses text",
        "management": "Sample management text",
        "prevention": "Sample prevention text",
        "notes": "Sample notes text",
        "drug_name": "Sample drug name",
        "drug_indication": "Sample drug indication",
        "drug_mechanism": "Sample drug mechanism",
        "drug_adverse_effects": "Sample drug adverse effects",
        "drug_contraindications": "Sample drug contraindications",
        "dosage_age_group": "Sample dosage age group",
        "dosage_route": "Sample dosage route",
        "dosage_value": "Sample dosage value",
        "dosage_max": "Sample dosage max",
        "dosage_frequency": "Sample dosage frequency",
        "dosage_special_considerations": "Sample dosage special considerations",
        "procedure_name": "Sample procedure name",
        "procedure_steps": "Sample procedure steps",
        "procedure_complications": "Sample procedure complications",
        "procedure_equipment": "Sample procedure equipment",
        "algorithm_title": "Sample algorithm title",
        "algorithm_description": "Sample algorithm description",
        "algorithm_flowchart_url": "Sample algorithm flowchart URL",
        "reference_citation": "Sample reference citation",
        "reference_doi": "Sample reference DOI",
        "reference_url": "Sample reference URL",
        "media_url": "Sample media URL",
        "media_type": "Sample media type",
        "media_caption": "Sample media caption",
        "revised_by": "Sample revised by",
        "revision_notes": "Sample revision notes",
        "revision_date": "Sample revision date"
    }]
    
    # Try to upload the sample data
    print("Uploading sample data...")
    try:
        result = supabase.table("nelson_pediatrics").insert(sample_data).execute()
        
        # Check for errors
        if hasattr(result, 'error') and result.error:
            print(f"Error uploading sample data: {result.error}")
        else:
            print("Sample data uploaded successfully")
            print("Table created successfully")
    except Exception as e:
        print(f"Error uploading sample data: {e}")
        print("You will need to create the table manually using the SQL Editor in the Supabase dashboard")
        print("Copy and paste the SQL from simple_table_creation.sql into the SQL Editor")

if __name__ == "__main__":
    create_sample_and_upload()

