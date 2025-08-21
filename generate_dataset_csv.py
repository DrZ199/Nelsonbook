#!/usr/bin/env python3
"""
Generate Dataset CSV from Nelson Textbook of Pediatrics

This script parses the Nelson Textbook of Pediatrics text files and generates
a CSV dataset suitable for import into Supabase or other databases.
"""

import os
import re
import csv
import json
from typing import Dict, List, Any, Optional

# Define section patterns
SECTION_PATTERNS = {
    'chapter': r'CHAPTER\s+(\d+)\.\s+(.*?)$',
    'section': r'(\d+\.\d+)\s+(.*?)$',
    'subsection': r'(\d+\.\d+\.\d+)\s+(.*?)$',
}

# Define content type patterns
CONTENT_TYPE_PATTERNS = {
    'epidemiology': r'EPIDEMIOLOGY',
    'clinical_manifestations': r'CLINICAL MANIFESTATIONS',
    'pathophysiology': r'PATHOPHYSIOLOGY',
    'diagnosis': r'DIAGNOSIS',
    'treatment': r'TREATMENT',
    'prevention': r'PREVENTION',
    'background': r'BACKGROUND',
    'etiology': r'ETIOLOGY',
    'clinical_presentation': r'CLINICAL PRESENTATION',
    'differential_diagnoses': r'DIFFERENTIAL DIAGNOSES',
    'management': r'MANAGEMENT',
    'prognosis': r'PROGNOSIS',
    'complications': r'COMPLICATIONS',
}

# Define drug and dosage patterns
DRUG_PATTERNS = {
    'drug_name': r'(\w+)\s+\[(\w+)\]\s+\(([^)]+)\)',
    'dosage': r'(\d+(?:\.\d+)?)\s*(?:mg|mcg|g|mL)/(?:kg|dose|day)',
    'age_group': r'(CHILDREN|ADOLESCENTS|INFANTS|NEONATES)\s+(\d+(?:-\d+)?)\s*(YR|MO|WK|DAY)',
}

class NelsonCsvGenerator:
    """Generate CSV dataset from Nelson Textbook of Pediatrics"""
    
    def __init__(self, input_files: List[str], output_file: str):
        """Initialize with input files and output file"""
        self.input_files = input_files
        self.output_file = output_file
        self.rows = []
        
        # Current context
        self.current_chapter = {'number': '', 'title': ''}
        self.current_section = {'number': '', 'title': ''}
        self.current_subsection = {'number': '', 'title': ''}
        self.current_topic = {'title': ''}
        self.current_content_type = ''
    
    def parse_files(self):
        """Parse all input files"""
        for file_path in self.input_files:
            print(f"Parsing {file_path}...")
            self.parse_file(file_path)
        
        # Write CSV file
        self.write_csv()
    
    def parse_file(self, file_path: str):
        """Parse a single file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Process content by paragraphs
            paragraphs = re.split(r'\n\n+', content)
            
            for i, paragraph in enumerate(paragraphs):
                # Skip empty paragraphs
                if not paragraph.strip():
                    continue
                
                # Check for chapter, section, subsection headers
                self.check_for_headers(paragraph)
                
                # Check for content type
                content_type = self.identify_content_type(paragraph)
                if content_type:
                    self.current_content_type = content_type
                
                # Extract drug information
                drug_info = self.extract_drug_info(paragraph)
                
                # Create a row for this paragraph
                self.create_row(paragraph, drug_info)
    
    def check_for_headers(self, text: str):
        """Check for chapter, section, subsection headers in text"""
        # Check for chapter header
        chapter_match = re.search(SECTION_PATTERNS['chapter'], text, re.MULTILINE)
        if chapter_match:
            self.current_chapter = {
                'number': chapter_match.group(1),
                'title': chapter_match.group(2).strip()
            }
            self.current_section = {'number': '', 'title': ''}
            self.current_subsection = {'number': '', 'title': ''}
            self.current_topic = {'title': self.current_chapter['title']}
            return
        
        # Check for section header
        section_match = re.search(SECTION_PATTERNS['section'], text, re.MULTILINE)
        if section_match:
            self.current_section = {
                'number': section_match.group(1),
                'title': section_match.group(2).strip()
            }
            self.current_subsection = {'number': '', 'title': ''}
            self.current_topic = {'title': self.current_section['title']}
            return
        
        # Check for subsection header
        subsection_match = re.search(SECTION_PATTERNS['subsection'], text, re.MULTILINE)
        if subsection_match:
            self.current_subsection = {
                'number': subsection_match.group(1),
                'title': subsection_match.group(2).strip()
            }
            self.current_topic = {'title': self.current_subsection['title']}
            return
    
    def identify_content_type(self, text: str) -> Optional[str]:
        """Identify content type from text"""
        for content_type, pattern in CONTENT_TYPE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return content_type
        return None
    
    def extract_drug_info(self, text: str) -> Dict[str, Any]:
        """Extract drug information from text"""
        drug_info = {
            'drug_name': '',
            'drug_brand_name': '',
            'drug_formulations': '',
            'dosage_value': '',
            'dosage_age_group': '',
            'dosage_route': '',
            'dosage_frequency': '',
        }
        
        # Extract drug name
        drug_match = re.search(DRUG_PATTERNS['drug_name'], text)
        if drug_match:
            drug_info['drug_name'] = drug_match.group(1)
            drug_info['drug_brand_name'] = drug_match.group(2)
            drug_info['drug_formulations'] = drug_match.group(3)
        
        # Extract dosage
        dosage_match = re.search(DRUG_PATTERNS['dosage'], text)
        if dosage_match:
            drug_info['dosage_value'] = dosage_match.group(0)
        
        # Extract age group
        age_group_match = re.search(DRUG_PATTERNS['age_group'], text)
        if age_group_match:
            drug_info['dosage_age_group'] = f"{age_group_match.group(1)} {age_group_match.group(2)} {age_group_match.group(3)}"
        
        # Extract route (simple pattern matching)
        if re.search(r'\b(oral|IV|IM|SC|topical|inhaled|intranasal|rectal)\b', text, re.IGNORECASE):
            route_match = re.search(r'\b(oral|IV|IM|SC|topical|inhaled|intranasal|rectal)\b', text, re.IGNORECASE)
            if route_match:
                drug_info['dosage_route'] = route_match.group(1)
        
        # Extract frequency
        frequency_match = re.search(r'(?:every|q)\s*(\d+(?:-\d+)?)\s*(?:h|hr|hour|hours|day|days|week|weeks)', text, re.IGNORECASE)
        if frequency_match:
            drug_info['dosage_frequency'] = frequency_match.group(0)
        
        return drug_info
    
    def create_row(self, text: str, drug_info: Dict[str, Any]):
        """Create a row for the CSV file"""
        # Determine content type based on current context or text analysis
        content_type = self.current_content_type
        
        # If no specific content type identified, use general content
        if not content_type:
            # Try to identify content type from text
            for type_name, pattern in CONTENT_TYPE_PATTERNS.items():
                if re.search(pattern, text, re.IGNORECASE):
                    content_type = type_name
                    break
            
            # If still no content type, use general content
            if not content_type:
                content_type = 'general_content'
        
        # Create row with all fields populated
        row = {
            # Hierarchy
            'chapter_number': self.current_chapter.get('number', '') or '0',
            'chapter_title': self.current_chapter.get('title', '') or 'Unknown Chapter',
            'section_title': self.current_section.get('title', '') or 'General Section',
            'subsection_title': self.current_subsection.get('title', '') or 'General Subsection',
            'topic_title': self.current_topic.get('title', '') or 'General Topic',
            
            # Core Content
            'background': text if content_type == 'background' else '',
            'epidemiology': text if content_type == 'epidemiology' else '',
            'pathophysiology': text if content_type == 'pathophysiology' else '',
            'clinical_presentation': text if content_type == 'clinical_presentation' or content_type == 'clinical_manifestations' else '',
            'diagnostics': text if content_type == 'diagnosis' else '',
            'differential_diagnoses': text if content_type == 'differential_diagnoses' else '',
            'management': text if content_type == 'management' or content_type == 'treatment' else '',
            'prevention': text if content_type == 'prevention' else '',
            'notes': text if content_type == 'general_content' else '',
            
            # Drugs & Dosages
            'drug_name': drug_info.get('drug_name', '') or '',
            'drug_indication': self.extract_drug_indication(text, drug_info.get('drug_name', '')) or '',
            'drug_mechanism': self.extract_drug_mechanism(text, drug_info.get('drug_name', '')) or '',
            'drug_adverse_effects': self.extract_drug_adverse_effects(text, drug_info.get('drug_name', '')) or '',
            'drug_contraindications': self.extract_drug_contraindications(text, drug_info.get('drug_name', '')) or '',
            'dosage_age_group': drug_info.get('dosage_age_group', '') or '',
            'dosage_route': drug_info.get('dosage_route', '') or '',
            'dosage_value': drug_info.get('dosage_value', '') or '',
            'dosage_max': self.extract_max_dose(text) or '',
            'dosage_frequency': drug_info.get('dosage_frequency', '') or '',
            'dosage_special_considerations': self.extract_special_considerations(text, drug_info.get('drug_name', '')) or '',
            
            # Procedures
            'procedure_name': self.extract_procedure_name(text) or '',
            'procedure_steps': self.extract_procedure_steps(text) or '',
            'procedure_complications': self.extract_procedure_complications(text) or '',
            'procedure_equipment': self.extract_procedure_equipment(text) or '',
            
            # Algorithms
            'algorithm_title': self.extract_algorithm_title(text) or '',
            'algorithm_description': self.extract_algorithm_description(text) or '',
            'algorithm_flowchart_url': '',
            
            # References
            'reference_citation': self.extract_reference_citation(text) or '',
            'reference_doi': self.extract_reference_doi(text) or '',
            'reference_url': self.extract_reference_url(text) or '',
            
            # Media Assets
            'media_url': '',
            'media_type': '',
            'media_caption': '',
            
            # Revisions / Updates
            'revised_by': '',
            'revision_notes': '',
            'revision_date': '',
        }
        
        # Only add row if it has meaningful content
        if any(value for key, value in row.items() if key not in ['chapter_number', 'chapter_title', 'section_title', 'subsection_title', 'topic_title']):
            self.rows.append(row)
    
    def extract_drug_indication(self, text: str, drug_name: str) -> Optional[str]:
        """Extract drug indication"""
        if not drug_name:
            return ''
        
        # Look for indication patterns
        indication_pattern = r'(?:indicated|used|for)\s+(?:for|in|to treat)\s+([^.]+)'
        match = re.search(indication_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # If no specific indication found, look for context
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            if drug_name in sentence and ('treat' in sentence.lower() or 'use' in sentence.lower()):
                return sentence.strip()
        
        return ''
    
    def extract_drug_mechanism(self, text: str, drug_name: str) -> Optional[str]:
        """Extract drug mechanism of action"""
        if not drug_name:
            return ''
        
        # Look for mechanism patterns
        mechanism_pattern = r'(?:mechanism|acts by|works by)\s+([^.]+)'
        match = re.search(mechanism_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_drug_adverse_effects(self, text: str, drug_name: str) -> Optional[str]:
        """Extract drug adverse effects"""
        if not drug_name:
            return ''
        
        # Look for adverse effects patterns
        adverse_pattern = r'(?:adverse effects|side effects|adverse reactions)\s+(?:include|are)\s+([^.]+)'
        match = re.search(adverse_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_drug_contraindications(self, text: str, drug_name: str) -> Optional[str]:
        """Extract drug contraindications"""
        if not drug_name:
            return ''
        
        # Look for contraindication patterns
        contraindication_pattern = r'(?:contraindicated|not recommended|avoid)\s+(?:in|with)\s+([^.]+)'
        match = re.search(contraindication_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_max_dose(self, text: str) -> Optional[str]:
        """Extract maximum dose information"""
        # Look for max dose patterns
        max_dose_pattern = r'(?:maximum|max)(?:\s+dose)?\s+(\d+(?:\.\d+)?)\s*(?:mg|mcg|g|mL)'
        match = re.search(max_dose_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(0)
        
        return ''
    
    def extract_special_considerations(self, text: str, drug_name: str) -> Optional[str]:
        """Extract special considerations for dosing"""
        if not drug_name:
            return ''
        
        # Look for special considerations
        special_pattern = r'(?:caution|warning|note|adjust|monitor)\s+([^.]+)'
        
        # Find sentences containing the drug name and special considerations
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            if drug_name.lower() in sentence.lower() and re.search(special_pattern, sentence, re.IGNORECASE):
                match = re.search(special_pattern, sentence, re.IGNORECASE)
                if match:
                    return match.group(0) + match.group(1)
        
        return ''
    
    def extract_procedure_name(self, text: str) -> Optional[str]:
        """Extract procedure name"""
        # Look for procedure patterns
        procedure_pattern = r'(?:procedure|technique|method):\s+([^.]+)'
        match = re.search(procedure_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_procedure_steps(self, text: str) -> Optional[str]:
        """Extract procedure steps"""
        # Look for step patterns
        steps_pattern = r'(?:steps|procedure|technique):\s+(.*?)(?:\n\n|$)'
        match = re.search(steps_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_procedure_complications(self, text: str) -> Optional[str]:
        """Extract procedure complications"""
        # Look for complication patterns
        complications_pattern = r'(?:complications|risks|adverse events):\s+(.*?)(?:\n\n|$)'
        match = re.search(complications_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_procedure_equipment(self, text: str) -> Optional[str]:
        """Extract procedure equipment"""
        # Look for equipment patterns
        equipment_pattern = r'(?:equipment|materials|supplies):\s+(.*?)(?:\n\n|$)'
        match = re.search(equipment_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_algorithm_title(self, text: str) -> Optional[str]:
        """Extract algorithm title"""
        # Look for algorithm patterns
        algorithm_pattern = r'(?:algorithm|flowchart|decision tree):\s+([^.]+)'
        match = re.search(algorithm_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_algorithm_description(self, text: str) -> Optional[str]:
        """Extract algorithm description"""
        # Look for algorithm description patterns
        description_pattern = r'(?:algorithm|flowchart|decision tree):\s+[^.]+\.\s+(.*?)(?:\n\n|$)'
        match = re.search(description_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_reference_citation(self, text: str) -> Optional[str]:
        """Extract reference citation"""
        # Look for reference patterns
        reference_pattern = r'(?:reference|citation):\s+(.*?)(?:\n\n|$)'
        match = re.search(reference_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_reference_doi(self, text: str) -> Optional[str]:
        """Extract reference DOI"""
        # Look for DOI patterns
        doi_pattern = r'(?:doi|DOI):\s+(10\.\d+/[^\s]+)'
        match = re.search(doi_pattern, text)
        
        if match:
            return match.group(1).strip()
        
        return ''
    
    def extract_reference_url(self, text: str) -> Optional[str]:
        """Extract reference URL"""
        # Look for URL patterns
        url_pattern = r'(?:https?://[^\s]+)'
        match = re.search(url_pattern, text)
        
        if match:
            return match.group(0).strip()
        
        return ''
    
    def write_csv(self):
        """Write rows to CSV file"""
        if not self.rows:
            print("No data to write to CSV")
            return
        
        print(f"Writing {len(self.rows)} rows to {self.output_file}...")
        
        # Get all field names
        fieldnames = list(self.rows[0].keys())
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.rows)
        
        print(f"CSV file written to {self.output_file}")


def main():
    """Main function"""
    # Get all nelson part files
    input_files = [f for f in os.listdir('.') if f.startswith('nelson_part_') and f.endswith('.txt')]
    input_files.sort()
    
    # Set output file
    output_file = 'dataset.csv'
    
    # Initialize and run CSV generator
    generator = NelsonCsvGenerator(input_files, output_file)
    generator.parse_files()
    
    print("CSV generation complete!")


if __name__ == "__main__":
    main()

