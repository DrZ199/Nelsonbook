# Nelson Pediatrics Database Setup Instructions

This document provides instructions for setting up the Nelson Pediatrics database in Supabase.

## Step 1: Create the Table in Supabase

1. Log in to your Supabase account and navigate to your project.
2. Click on the "SQL Editor" tab.
3. Create a new query and paste the following SQL:

```sql
-- Create the nelson_pediatrics table
CREATE TABLE IF NOT EXISTS nelson_pediatrics (
    id BIGSERIAL PRIMARY KEY,
    
    -- Hierarchy
    chapter_number TEXT,
    chapter_title TEXT,
    section_title TEXT,
    subsection_title TEXT,
    topic_title TEXT,
    
    -- Core Content
    background TEXT,
    epidemiology TEXT,
    pathophysiology TEXT,
    clinical_presentation TEXT,
    diagnostics TEXT,
    differential_diagnoses TEXT,
    management TEXT,
    prevention TEXT,
    notes TEXT,
    
    -- Drugs & Dosages
    drug_name TEXT,
    drug_indication TEXT,
    drug_mechanism TEXT,
    drug_adverse_effects TEXT,
    drug_contraindications TEXT,
    dosage_age_group TEXT,
    dosage_route TEXT,
    dosage_value TEXT,
    dosage_max TEXT,
    dosage_frequency TEXT,
    dosage_special_considerations TEXT,
    
    -- Procedures
    procedure_name TEXT,
    procedure_steps TEXT,
    procedure_complications TEXT,
    procedure_equipment TEXT,
    
    -- Algorithms
    algorithm_title TEXT,
    algorithm_description TEXT,
    algorithm_flowchart_url TEXT,
    
    -- References
    reference_citation TEXT,
    reference_doi TEXT,
    reference_url TEXT,
    
    -- Media Assets
    media_url TEXT,
    media_type TEXT,
    media_caption TEXT,
    
    -- Revisions / Updates
    revised_by TEXT,
    revision_notes TEXT,
    revision_date TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create a simple index on chapter_number
CREATE INDEX IF NOT EXISTS idx_nelson_pediatrics_chapter_number ON nelson_pediatrics(chapter_number);

-- Create a simple index on drug_name
CREATE INDEX IF NOT EXISTS idx_nelson_pediatrics_drug_name ON nelson_pediatrics(drug_name);

-- Create a simple index on topic_title
CREATE INDEX IF NOT EXISTS idx_nelson_pediatrics_topic_title ON nelson_pediatrics(topic_title);
```

4. Click "Run" to create the table.

## Step 2: Upload the Data

After creating the table, you can upload the data using the `batch_upload.py` script:

```bash
# Set environment variables
export SUPABASE_URL="https://nrtaztkewvbtzhbtkffc.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-key"
export SUPABASE_ANON_KEY="your-anon-key"

# Run the batch upload script
python batch_upload.py --batch-size 50 --delay-seconds 2
```

This script will:
- Upload the data in batches of 50 rows
- Wait 2 seconds between batches to avoid rate limits
- Automatically retry failed batches
- Show progress as it uploads

## Step 3: Verify the Upload

After the upload is complete, you can verify the data in Supabase:

1. Go to the "Table Editor" tab.
2. Select the "nelson_pediatrics" table.
3. Check that the data has been uploaded correctly.

## Troubleshooting

If you encounter any issues:

1. **Rate Limiting**: If you hit rate limits, increase the `delay-seconds` parameter.
2. **Batch Size**: If you encounter errors with large batches, decrease the `batch-size` parameter.
3. **Connection Issues**: Check your Supabase credentials and make sure they are correct.
4. **Table Doesn't Exist**: Make sure you've created the table using the SQL in Step 1.

## Additional Scripts

The following scripts are available:

- `generate_insert_sql.py`: Generates SQL INSERT statements for manual upload.
- `split_sql.py`: Splits the SQL file into smaller chunks for manual upload.
- `create_table_supabase.py`: Attempts to create the table using the Supabase client.
- `test_supabase.py`: Tests the connection to Supabase.

## Next Steps

After uploading the data, you can:

1. Create additional indexes for better performance.
2. Set up Row Level Security (RLS) policies.
3. Create API endpoints for accessing the data.
4. Set up full-text search for the content.

