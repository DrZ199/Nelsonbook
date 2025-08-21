#!/bin/bash
# Create Table in Supabase using curl
# This script creates the nelson_pediatrics table in Supabase using curl.

# Get Supabase credentials from environment variables
SUPABASE_URL="${SUPABASE_URL}"
SUPABASE_KEY="${SUPABASE_SERVICE_KEY}"

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
  echo "Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set"
  exit 1
fi

echo "Connecting to Supabase at ${SUPABASE_URL}..."

# Create a sample row
SAMPLE_DATA='[{
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
}]'

# Try to upload the sample data
echo "Uploading sample data..."
curl -X POST "${SUPABASE_URL}/rest/v1/nelson_pediatrics" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=minimal" \
  -d "${SAMPLE_DATA}"

echo ""
echo "If you see an error, you will need to create the table manually using the SQL Editor in the Supabase dashboard"
echo "Copy and paste the SQL from simple_table_creation.sql into the SQL Editor"

