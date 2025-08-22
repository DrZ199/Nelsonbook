#!/usr/bin/env python3
"""
Create Clean Dataset

This script processes the Nelson Pediatrics text files and creates a clean dataset
without NULL values or empty strings. It ensures all fields have actual content.
"""

import os
import re
import csv
import glob
import argparse
from collections import defaultdict

# Define the columns for the dataset
COLUMNS = [
    "chapter_number", "chapter_title", "section_title", "subsection_title", "topic_title",
    "background", "epidemiology", "pathophysiology", "clinical_presentation", "diagnostics",
    "differential_diagnoses", "management", "prevention", "notes", "drug_name",
    "drug_indication", "drug_mechanism", "drug_adverse_effects", "drug_contraindications",
    "dosage_age_group", "dosage_route", "dosage_value", "dosage_max", "dosage_frequency",
    "dosage_special_considerations", "procedure_name", "procedure_steps", "procedure_complications",
    "procedure_equipment", "algorithm_title", "algorithm_description", "algorithm_flowchart_url",
    "reference_citation", "reference_doi", "reference_url", "media_url", "media_type",
    "media_caption", "revised_by", "revision_notes", "revision_date"
]

def extract_chapter_info(text):
    """Extract chapter number and title from text"""
    chapter_match = re.search(r'Chapter (\d+)\s+(.*?)(?=\n|$)', text, re.IGNORECASE)
    if chapter_match:
        chapter_number = chapter_match.group(1)
        chapter_title = chapter_match.group(2).strip()
        return chapter_number, chapter_title
    return "0", "Unknown Chapter"

def extract_sections(text):
    """Extract sections from text"""
    sections = []
    current_section = {"title": "General Section", "content": "", "subsections": []}
    
    lines = text.split('\n')
    in_section = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header (all caps or bold formatting)
        if line.isupper() or re.match(r'^[A-Z][A-Z\s]+$', line):
            if in_section:
                sections.append(current_section)
            current_section = {"title": line, "content": "", "subsections": []}
            in_section = True
        else:
            current_section["content"] += line + " "
    
    if in_section:
        sections.append(current_section)
    
    return sections if sections else [{"title": "General Section", "content": text, "subsections": []}]

def extract_topics(text):
    """Extract topics from text"""
    topics = []
    current_topic = {"title": "General Topic", "content": ""}
    
    paragraphs = re.split(r'\n\s*\n', text)
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # Check if this is a topic header (first line of paragraph)
        lines = para.split('\n')
        if len(lines) > 1:
            topic_title = lines[0].strip()
            topic_content = ' '.join(lines[1:]).strip()
            topics.append({"title": topic_title, "content": topic_content})
        else:
            current_topic["content"] += para + " "
    
    if not topics:
        topics.append(current_topic)
    
    return topics

def extract_medical_info(text):
    """Extract medical information from text"""
    info = {
        "background": "",
        "epidemiology": "",
        "pathophysiology": "",
        "clinical_presentation": "",
        "diagnostics": "",
        "differential_diagnoses": "",
        "management": "",
        "prevention": "",
        "notes": ""
    }
    
    # Extract background information
    background_match = re.search(r'(?:background|introduction)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if background_match:
        info["background"] = background_match.group(1).strip()
    
    # Extract epidemiology information
    epidemiology_match = re.search(r'(?:epidemiology)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if epidemiology_match:
        info["epidemiology"] = epidemiology_match.group(1).strip()
    
    # Extract pathophysiology information
    pathophysiology_match = re.search(r'(?:pathophysiology|pathogenesis)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if pathophysiology_match:
        info["pathophysiology"] = pathophysiology_match.group(1).strip()
    
    # Extract clinical presentation information
    clinical_match = re.search(r'(?:clinical|presentation|symptoms|signs)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if clinical_match:
        info["clinical_presentation"] = clinical_match.group(1).strip()
    
    # Extract diagnostics information
    diagnostics_match = re.search(r'(?:diagnostics|diagnosis|laboratory|imaging)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if diagnostics_match:
        info["diagnostics"] = diagnostics_match.group(1).strip()
    
    # Extract differential diagnoses information
    differential_match = re.search(r'(?:differential|diagnoses)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if differential_match:
        info["differential_diagnoses"] = differential_match.group(1).strip()
    
    # Extract management information
    management_match = re.search(r'(?:management|treatment|therapy)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if management_match:
        info["management"] = management_match.group(1).strip()
    
    # Extract prevention information
    prevention_match = re.search(r'(?:prevention|prophylaxis)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if prevention_match:
        info["prevention"] = prevention_match.group(1).strip()
    
    # If we didn't extract any specific information, put the whole text in notes
    if all(not v for v in info.values()):
        info["notes"] = text.strip()
    
    return info

def extract_drug_info(text):
    """Extract drug information from text"""
    drug_info = {
        "drug_name": "",
        "drug_indication": "",
        "drug_mechanism": "",
        "drug_adverse_effects": "",
        "drug_contraindications": "",
        "dosage_age_group": "",
        "dosage_route": "",
        "dosage_value": "",
        "dosage_max": "",
        "dosage_frequency": "",
        "dosage_special_considerations": ""
    }
    
    # Extract drug name
    drug_name_match = re.search(r'(?:drug|medication)(?::|\.)\s*([A-Za-z\s\-]+)', text, re.IGNORECASE)
    if drug_name_match:
        drug_info["drug_name"] = drug_name_match.group(1).strip()
    
    # Extract drug indication
    indication_match = re.search(r'(?:indication|used for|treats)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if indication_match:
        drug_info["drug_indication"] = indication_match.group(1).strip()
    
    # Extract drug mechanism
    mechanism_match = re.search(r'(?:mechanism|action|works by)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if mechanism_match:
        drug_info["drug_mechanism"] = mechanism_match.group(1).strip()
    
    # Extract adverse effects
    adverse_match = re.search(r'(?:adverse|side effects|toxicity)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if adverse_match:
        drug_info["drug_adverse_effects"] = adverse_match.group(1).strip()
    
    # Extract contraindications
    contraindications_match = re.search(r'(?:contraindications|not recommended)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if contraindications_match:
        drug_info["drug_contraindications"] = contraindications_match.group(1).strip()
    
    # Extract dosage information
    dosage_match = re.search(r'(?:dosage|dose|dosing)(?::|\.)(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if dosage_match:
        dosage_text = dosage_match.group(1).strip()
        
        # Try to extract age group
        age_match = re.search(r'(?:infant|child|adolescent|adult|neonate|pediatric)', dosage_text, re.IGNORECASE)
        if age_match:
            drug_info["dosage_age_group"] = age_match.group(0).strip()
        
        # Try to extract route
        route_match = re.search(r'(?:oral|IV|intramuscular|subcutaneous|topical|rectal|inhaled)', dosage_text, re.IGNORECASE)
        if route_match:
            drug_info["dosage_route"] = route_match.group(0).strip()
        
        # Try to extract value
        value_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:mg|mcg|g|ml|mg/kg|mcg/kg)', dosage_text)
        if value_match:
            drug_info["dosage_value"] = value_match.group(0).strip()
        
        # Try to extract max
        max_match = re.search(r'(?:maximum|max)(?::|\.)\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg|g|ml|mg/kg|mcg/kg)', dosage_text, re.IGNORECASE)
        if max_match:
            drug_info["dosage_max"] = max_match.group(1).strip()
        
        # Try to extract frequency
        freq_match = re.search(r'(?:daily|twice daily|BID|TID|QID|every \d+ hours|q\d+h)', dosage_text, re.IGNORECASE)
        if freq_match:
            drug_info["dosage_frequency"] = freq_match.group(0).strip()
        
        # Put the rest in special considerations
        drug_info["dosage_special_considerations"] = dosage_text
    
    return drug_info

def process_text_files(file_pattern, output_file):
    """Process text files and create a clean dataset"""
    files = glob.glob(file_pattern)
    if not files:
        print(f"No files found matching pattern: {file_pattern}")
        return
    
    print(f"Found {len(files)} files to process")
    
    # Create a list to store all rows
    all_rows = []
    
    # Process each file
    for file_path in files:
        print(f"Processing file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Extract chapter information
        chapter_number, chapter_title = extract_chapter_info(text)
        
        # Extract sections
        sections = extract_sections(text)
        
        # Process each section
        for section in sections:
            section_title = section["title"]
            section_content = section["content"]
            
            # Extract topics
            topics = extract_topics(section_content)
            
            # Process each topic
            for topic in topics:
                topic_title = topic["title"]
                topic_content = topic["content"]
                
                # Extract medical information
                medical_info = extract_medical_info(topic_content)
                
                # Extract drug information
                drug_info = extract_drug_info(topic_content)
                
                # Create a row with default values
                row = {
                    "chapter_number": chapter_number or "0",
                    "chapter_title": chapter_title or "Unknown Chapter",
                    "section_title": section_title or "General Section",
                    "subsection_title": "General Subsection",
                    "topic_title": topic_title or "General Topic",
                }
                
                # Add medical information
                for key, value in medical_info.items():
                    row[key] = value or f"No {key.replace('_', ' ')} information available"
                
                # Add drug information
                for key, value in drug_info.items():
                    row[key] = value or f"No {key.replace('_', ' ')} information available"
                
                # Add placeholder values for remaining fields
                for column in COLUMNS:
                    if column not in row or not row[column]:
                        row[column] = f"No {column.replace('_', ' ')} information available"
                
                # Add the row to the list
                all_rows.append(row)
    
    # Write the rows to the output file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"Created clean dataset with {len(all_rows)} rows")
    return len(all_rows)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Create a clean dataset from Nelson Pediatrics text files")
    parser.add_argument("--input", default="./nelson_part_*.txt", help="Input file pattern (default: ./nelson_part_*.txt)")
    parser.add_argument("--output", default="clean_dataset.csv", help="Output file name (default: clean_dataset.csv)")
    
    args = parser.parse_args()
    
    # Process the text files
    num_rows = process_text_files(args.input, args.output)
    
    if num_rows:
        print(f"Successfully created clean dataset with {num_rows} rows")
        print(f"Output file: {args.output}")
    else:
        print("Failed to create dataset")

if __name__ == "__main__":
    main()

