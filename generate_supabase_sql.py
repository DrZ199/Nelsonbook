#!/usr/bin/env python3
"""
Generate Supabase SQL for Nelson Textbook of Pediatrics

This script generates SQL statements for creating tables and inserting data
into a Supabase database based on the parsed Nelson Textbook of Pediatrics data.
"""

import os
import json
import re
from typing import Dict, List, Any

# SQL Schema
SCHEMA_SQL = """
-- Create extension for vector support
CREATE EXTENSION IF NOT EXISTS vector;

-- Hierarchical structure tables
CREATE TABLE nelson_chapters (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chapter_number INT NOT NULL,
    title TEXT NOT NULL,
    UNIQUE(chapter_number)
);

CREATE TABLE nelson_sections (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chapter_id BIGINT REFERENCES nelson_chapters(id),
    section_number TEXT NOT NULL,
    title TEXT NOT NULL,
    UNIQUE(chapter_id, section_number)
);

CREATE TABLE nelson_subsections (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    section_id BIGINT REFERENCES nelson_sections(id),
    subsection_number TEXT NOT NULL,
    title TEXT NOT NULL,
    UNIQUE(section_id, subsection_number)
);

-- Main content table with hierarchical structure
CREATE TABLE nelson_content (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- Hierarchy (normalized)
    chapter_id BIGINT REFERENCES nelson_chapters(id),
    section_id BIGINT REFERENCES nelson_sections(id),
    subsection_id BIGINT REFERENCES nelson_subsections(id),
    
    -- Core Content
    title TEXT NOT NULL,
    content_text TEXT NOT NULL,
    content_type TEXT NOT NULL, -- 'background', 'epidemiology', 'pathophysiology', etc.
    
    -- Vector embedding for semantic search
    content_embedding vector(1536),  -- For OpenAI embeddings
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Drugs table (normalized)
CREATE TABLE nelson_drugs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    content_id BIGINT REFERENCES nelson_content(id),
    drug_name TEXT NOT NULL,
    drug_brand_name TEXT NOT NULL,
    drug_formulations TEXT NOT NULL,
    drug_indication TEXT NOT NULL,
    drug_mechanism TEXT NOT NULL,
    drug_adverse_effects TEXT NOT NULL,
    drug_contraindications TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Dosages table (normalized from drugs)
CREATE TABLE nelson_dosages (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    drug_id BIGINT REFERENCES nelson_drugs(id),
    age_group TEXT NOT NULL,
    route TEXT NOT NULL,
    value TEXT NOT NULL,
    max_dose TEXT NOT NULL,
    frequency TEXT NOT NULL,
    special_considerations TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX idx_nelson_content_chapter_id ON nelson_content(chapter_id);
CREATE INDEX idx_nelson_content_title ON nelson_content USING GIN (to_tsvector('english', title));
CREATE INDEX idx_nelson_content_content_text ON nelson_content USING GIN (to_tsvector('english', content_text));
CREATE INDEX idx_nelson_drugs_name ON nelson_drugs USING GIN (to_tsvector('english', drug_name));

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to update the updated_at timestamp
CREATE TRIGGER update_nelson_content_updated_at
BEFORE UPDATE ON nelson_content
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
"""

class SqlGenerator:
    """Generate SQL for Supabase from parsed Nelson data"""
    
    def __init__(self, data_dir: str, output_file: str):
        """Initialize with data directory and output file"""
        self.data_dir = data_dir
        self.output_file = output_file
        self.chapter_id_map = {}  # Map chapter numbers to IDs
        self.section_id_map = {}  # Map section numbers to IDs
        self.subsection_id_map = {}  # Map subsection numbers to IDs
        self.content_id_map = {}  # Map content indices to IDs
        self.drug_id_map = {}  # Map drug indices to IDs
    
    def load_data(self, file_name: str) -> List[Dict[str, Any]]:
        """Load data from a JSON file"""
        file_path = os.path.join(self.data_dir, file_name)
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} does not exist")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def escape_sql_string(self, s: str) -> str:
        """Escape a string for SQL"""
        if s is None:
            return "''"
        return "'" + s.replace("'", "''") + "'"
    
    def generate_sql(self):
        """Generate SQL for all data"""
        # Load data
        chapters = self.load_data('chapters.json')
        sections = self.load_data('sections.json')
        subsections = self.load_data('subsections.json')
        content_blocks = self.load_data('content_blocks.json')
        drugs = self.load_data('drugs.json')
        dosages = self.load_data('dosages.json')
        
        # Generate SQL
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Write schema
            f.write(SCHEMA_SQL)
            f.write("\n\n-- Insert data\n")
            
            # Insert chapters
            f.write("\n-- Insert chapters\n")
            for i, chapter in enumerate(chapters):
                chapter_number = int(chapter['number']) if chapter['number'].isdigit() else i + 1
                title = chapter['title'] or f"Chapter {chapter_number}"
                
                sql = f"INSERT INTO nelson_chapters (chapter_number, title) VALUES ({chapter_number}, {self.escape_sql_string(title)});\n"
                f.write(sql)
                
                # Map chapter number to ID (1-based for simplicity)
                self.chapter_id_map[chapter['number']] = i + 1
            
            # Insert sections
            f.write("\n-- Insert sections\n")
            for i, section in enumerate(sections):
                chapter_id = self.chapter_id_map.get(section['chapter_id'], 1)  # Default to 1 if not found
                section_number = section['number'] or f"{chapter_id}.{i+1}"
                title = section['title'] or f"Section {section_number}"
                
                sql = f"INSERT INTO nelson_sections (chapter_id, section_number, title) VALUES ({chapter_id}, {self.escape_sql_string(section_number)}, {self.escape_sql_string(title)});\n"
                f.write(sql)
                
                # Map section number to ID
                self.section_id_map[section['number']] = i + 1
            
            # Insert subsections
            f.write("\n-- Insert subsections\n")
            for i, subsection in enumerate(subsections):
                section_id = self.section_id_map.get(subsection['section_id'], 1)  # Default to 1 if not found
                subsection_number = subsection['number'] or f"{section_id}.{i+1}"
                title = subsection['title'] or f"Subsection {subsection_number}"
                
                sql = f"INSERT INTO nelson_subsections (section_id, subsection_number, title) VALUES ({section_id}, {self.escape_sql_string(subsection_number)}, {self.escape_sql_string(title)});\n"
                f.write(sql)
                
                # Map subsection number to ID
                self.subsection_id_map[subsection['number']] = i + 1
            
            # Insert content blocks
            f.write("\n-- Insert content blocks\n")
            for i, content in enumerate(content_blocks):
                chapter_id = self.chapter_id_map.get(content['chapter_id'], 1)  # Default to 1 if not found
                section_id = self.section_id_map.get(content['section_id'], 1)  # Default to 1 if not found
                subsection_id = self.subsection_id_map.get(content['subsection_id'], 1)  # Default to 1 if not found
                
                title = content['title'] or f"Content {i+1}"
                content_text = content['content_text'] or f"Content for {title}"
                content_type = content['content_type'] or "general_content"
                
                sql = f"""INSERT INTO nelson_content (chapter_id, section_id, subsection_id, title, content_text, content_type) 
                VALUES ({chapter_id}, {section_id}, {subsection_id}, {self.escape_sql_string(title)}, {self.escape_sql_string(content_text)}, {self.escape_sql_string(content_type)});\n"""
                f.write(sql)
                
                # Map content index to ID
                self.content_id_map[i] = i + 1
            
            # Insert drugs
            f.write("\n-- Insert drugs\n")
            for i, drug in enumerate(drugs):
                content_id = self.content_id_map.get(drug['content_id'], 1)  # Default to 1 if not found
                
                drug_name = drug['drug_name'] or f"Drug {i+1}"
                drug_brand_name = drug.get('drug_brand_name', '') or f"Brand for {drug_name}"
                drug_formulations = drug.get('drug_formulations', '') or "Various formulations"
                drug_indication = drug.get('drug_indication', '') or "For treatment of relevant conditions"
                drug_mechanism = drug.get('drug_mechanism', '') or "Refer to pharmacology references"
                drug_adverse_effects = drug.get('drug_adverse_effects', '') or "See prescribing information"
                drug_contraindications = drug.get('drug_contraindications', '') or "See prescribing information"
                
                sql = f"""INSERT INTO nelson_drugs (content_id, drug_name, drug_brand_name, drug_formulations, drug_indication, drug_mechanism, drug_adverse_effects, drug_contraindications) 
                VALUES ({content_id}, {self.escape_sql_string(drug_name)}, {self.escape_sql_string(drug_brand_name)}, {self.escape_sql_string(drug_formulations)}, 
                {self.escape_sql_string(drug_indication)}, {self.escape_sql_string(drug_mechanism)}, {self.escape_sql_string(drug_adverse_effects)}, {self.escape_sql_string(drug_contraindications)});\n"""
                f.write(sql)
                
                # Map drug index to ID
                self.drug_id_map[i] = i + 1
            
            # Insert dosages
            f.write("\n-- Insert dosages\n")
            for i, dosage in enumerate(dosages):
                drug_id = self.drug_id_map.get(dosage['drug_id'], 1)  # Default to 1 if not found
                
                age_group = dosage.get('age_group', '') or "All ages"
                route = dosage.get('route', '') or "Oral"
                value = dosage.get('value', '') or "As directed by healthcare provider"
                max_dose = dosage.get('max_dose', '') or "Refer to current dosing guidelines"
                frequency = dosage.get('frequency', '') or "As directed by healthcare provider"
                special_considerations = dosage.get('special_considerations', '') or "Follow standard monitoring protocols"
                
                sql = f"""INSERT INTO nelson_dosages (drug_id, age_group, route, value, max_dose, frequency, special_considerations) 
                VALUES ({drug_id}, {self.escape_sql_string(age_group)}, {self.escape_sql_string(route)}, {self.escape_sql_string(value)}, 
                {self.escape_sql_string(max_dose)}, {self.escape_sql_string(frequency)}, {self.escape_sql_string(special_considerations)});\n"""
                f.write(sql)
            
            print(f"SQL generated and saved to {self.output_file}")


def main():
    """Main function"""
    # Set input and output paths
    data_dir = 'parsed_data'
    output_file = 'nelson_supabase.sql'
    
    # Create SQL generator and generate SQL
    generator = SqlGenerator(data_dir, output_file)
    generator.generate_sql()
    
    print("SQL generation complete!")


if __name__ == "__main__":
    main()

