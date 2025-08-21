-- Create a simple version of the nelson_pediatrics table
-- Copy and paste this into the Supabase SQL Editor

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

