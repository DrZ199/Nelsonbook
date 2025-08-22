# Nelson Pediatrics Supabase Upload

This repository contains scripts to process the Nelson Textbook of Pediatrics data and upload it to Supabase.

## Clean Dataset

The clean dataset has been created with the following characteristics:
- 34,306 rows of clean data
- No NULL values
- No empty strings
- All fields contain actual content or descriptive placeholders

## Scripts

### 1. Create Clean Dataset
```bash
./create_clean_dataset.py
```
This script processes the Nelson text files and creates a clean dataset with no NULL or empty values.

### 2. Create Table in Supabase
The table must be created manually in the Supabase dashboard SQL editor using the SQL in `create_table.sql`.

```sql
-- Create the nelson_pediatrics_clean table
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

-- Create a search index
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
```

### 3. Upload Clean Dataset to Supabase
```bash
export SUPABASE_URL="https://nrtaztkewvbtzhbtkffc.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-key"
./upload_clean_dataset.py --batch-size 10000 --delay-seconds 5
```
This script uploads the clean dataset to Supabase in batches.

### 4. Check Progress of Upload
```bash
export SUPABASE_URL="https://nrtaztkewvbtzhbtkffc.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-key"
./check_progress.py
```
This script checks the progress of the upload to Supabase.

## Data Structure

The clean dataset has the following structure:
- Basic information (chapter, section, topic)
- Medical content (background, epidemiology, etc.)
- Drug information
- Procedures and algorithms
- References and media
- Revision tracking

## Upload Configuration

The upload script is configured with the following parameters:
- Batch size: 10,000 rows per batch
- Delay: 5 seconds between batches
- Automatic retry with reduced batch size on failure
- Progress tracking and logging

## Error Handling and Recovery

The upload script includes the following error handling features:
- Batch size reduction on failure
- Descriptive error messages
- Exception handling
- Progress recovery capability

## Search Optimization

The table is optimized for search with the following features:
- GIN index for full-text search
- Comprehensive text vector creation
- Optimized field combinations
- Proper index configuration

