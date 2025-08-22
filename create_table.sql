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

