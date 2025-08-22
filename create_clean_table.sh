#!/bin/bash
# Create Clean Table Script
# This script creates the nelson_pediatrics_clean table in Supabase using the REST API.

# Set environment variables
export SUPABASE_URL="https://nrtaztkewvbtzhbtkffc.supabase.co"
export SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ydGF6dGtld3ZidHpoYnRrZmZjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDI1NjM3NSwiZXhwIjoyMDY5ODMyMzc1fQ.qJas9ux_U-1V4lbx3XuIeEOIEx68so9kXbwRN7w5gXU"

# Create the table using the REST API
echo "Creating table nelson_pediatrics_clean..."

curl -X POST "${SUPABASE_URL}/rest/v1/rpc/execute_sql" \
  -H "apikey: ${SUPABASE_SERVICE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CREATE TABLE IF NOT EXISTS nelson_pediatrics_clean (
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
    );"
}'

echo "Creating search index..."

curl -X POST "${SUPABASE_URL}/rest/v1/rpc/execute_sql" \
  -H "apikey: ${SUPABASE_SERVICE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CREATE INDEX IF NOT EXISTS nelson_pediatrics_clean_search_idx ON nelson_pediatrics_clean 
    USING GIN (to_tsvector('\''english'\'', 
        chapter_title || '\'' '\'' || 
        section_title || '\'' '\'' || 
        subsection_title || '\'' '\'' || 
        topic_title || '\'' '\'' || 
        background || '\'' '\'' || 
        epidemiology || '\'' '\'' || 
        pathophysiology || '\'' '\'' || 
        clinical_presentation || '\'' '\'' || 
        diagnostics || '\'' '\'' || 
        differential_diagnoses || '\'' '\'' || 
        management || '\'' '\'' || 
        prevention || '\'' '\'' || 
        notes || '\'' '\'' || 
        drug_name || '\'' '\'' || 
        drug_indication || '\'' '\'' || 
        drug_mechanism || '\'' '\'' || 
        drug_adverse_effects || '\'' '\'' || 
        drug_contraindications
    ));"
}'

echo "Table creation completed."

