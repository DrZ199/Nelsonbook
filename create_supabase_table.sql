-- Create the nelson_pediatrics table
CREATE TABLE IF NOT EXISTS nelson_pediatrics (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- Hierarchy
    chapter_number TEXT NOT NULL,
    chapter_title TEXT NOT NULL,
    section_title TEXT NOT NULL,
    subsection_title TEXT NOT NULL,
    topic_title TEXT NOT NULL,
    
    -- Core Content
    background TEXT NOT NULL,
    epidemiology TEXT NOT NULL,
    pathophysiology TEXT NOT NULL,
    clinical_presentation TEXT NOT NULL,
    diagnostics TEXT NOT NULL,
    differential_diagnoses TEXT NOT NULL,
    management TEXT NOT NULL,
    prevention TEXT NOT NULL,
    notes TEXT NOT NULL,
    
    -- Drugs & Dosages
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
    
    -- Procedures
    procedure_name TEXT NOT NULL,
    procedure_steps TEXT NOT NULL,
    procedure_complications TEXT NOT NULL,
    procedure_equipment TEXT NOT NULL,
    
    -- Algorithms
    algorithm_title TEXT NOT NULL,
    algorithm_description TEXT NOT NULL,
    algorithm_flowchart_url TEXT NOT NULL,
    
    -- References
    reference_citation TEXT NOT NULL,
    reference_doi TEXT NOT NULL,
    reference_url TEXT NOT NULL,
    
    -- Media Assets
    media_url TEXT NOT NULL,
    media_type TEXT NOT NULL,
    media_caption TEXT NOT NULL,
    
    -- Revisions / Updates
    revised_by TEXT NOT NULL,
    revision_notes TEXT NOT NULL,
    revision_date TEXT NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_nelson_pediatrics_chapter_number ON nelson_pediatrics(chapter_number);
CREATE INDEX IF NOT EXISTS idx_nelson_pediatrics_drug_name ON nelson_pediatrics USING GIN (to_tsvector('english', drug_name));
CREATE INDEX IF NOT EXISTS idx_nelson_pediatrics_topic_title ON nelson_pediatrics USING GIN (to_tsvector('english', topic_title));
CREATE INDEX IF NOT EXISTS idx_nelson_pediatrics_content ON nelson_pediatrics USING GIN (to_tsvector('english', 
    background || ' ' || 
    epidemiology || ' ' || 
    pathophysiology || ' ' || 
    clinical_presentation || ' ' || 
    diagnostics || ' ' || 
    differential_diagnoses || ' ' || 
    management || ' ' || 
    prevention || ' ' || 
    notes
));

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to update the updated_at timestamp
CREATE TRIGGER update_nelson_pediatrics_updated_at
BEFORE UPDATE ON nelson_pediatrics
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create a function for full-text search
CREATE OR REPLACE FUNCTION search_nelson_pediatrics(search_query TEXT)
RETURNS SETOF nelson_pediatrics AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM nelson_pediatrics
    WHERE to_tsvector('english', 
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
        drug_indication
    ) @@ to_tsquery('english', search_query);
END;
$$ LANGUAGE plpgsql;

