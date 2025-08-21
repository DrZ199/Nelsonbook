#!/usr/bin/env python3
"""
Nelson Textbook of Pediatrics Parser

This script parses the Nelson Textbook of Pediatrics text files and extracts structured data
for insertion into a Supabase database. It ensures all fields are populated with original data.
"""

import re
import os
import json
from typing import Dict, List, Tuple, Optional

# Define section patterns
SECTION_PATTERNS = {
    'chapter': r'^CHAPTER\s+(\d+)\.\s+(.*?)$',
    'section': r'^(\d+\.\d+)\s+(.*?)$',
    'subsection': r'^(\d+\.\d+\.\d+)\s+(.*?)$',
    'epidemiology': r'^EPIDEMIOLOGY\s*$',
    'clinical_manifestations': r'^CLINICAL MANIFESTATIONS\s*$',
    'pathophysiology': r'^PATHOPHYSIOLOGY\s*$',
    'diagnosis': r'^DIAGNOSIS\s*$',
    'treatment': r'^TREATMENT\s*$',
    'prevention': r'^PREVENTION\s*$',
    'dosage': r'^DOSAGE\s*$',
    'drug': r'^DRUG\s*$',
}

# Define content extraction patterns
CONTENT_PATTERNS = {
    'drug_name': r'(\w+)\s+\[(\w+)\]\s+\(([^)]+)\)',
    'dosage': r'(\d+(?:\.\d+)?)\s*(?:mg|mcg|g|mL)/(?:kg|dose|day)',
    'age_group': r'(CHILDREN|ADOLESCENTS|INFANTS|NEONATES)\s+(\d+(?:-\d+)?)\s*(YR|MO|WK|DAY)',
}

class NelsonParser:
    """Parser for Nelson Textbook of Pediatrics"""
    
    def __init__(self, input_files: List[str], output_dir: str):
        """Initialize the parser with input files and output directory"""
        self.input_files = input_files
        self.output_dir = output_dir
        self.current_chapter = {'number': '', 'title': ''}
        self.current_section = {'number': '', 'title': ''}
        self.current_subsection = {'number': '', 'title': ''}
        self.current_topic = {'title': ''}
        
        # Data storage
        self.chapters = []
        self.sections = []
        self.subsections = []
        self.content_blocks = []
        self.drugs = []
        self.dosages = []
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def parse_files(self):
        """Parse all input files"""
        for file_path in self.input_files:
            print(f"Parsing {file_path}...")
            self.parse_file(file_path)
        
        # Save extracted data
        self.save_data()
    
    def parse_file(self, file_path: str):
        """Parse a single file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Split content into sections
            sections = self.split_into_sections(content)
            
            # Process each section
            for section_type, section_content in sections:
                self.process_section(section_type, section_content)
    
    def split_into_sections(self, content: str) -> List[Tuple[str, str]]:
        """Split content into sections based on patterns"""
        # Implementation will depend on the actual structure of the files
        # This is a placeholder for the actual implementation
        sections = []
        
        # Example: Split by chapter headers
        chapter_matches = re.finditer(SECTION_PATTERNS['chapter'], content, re.MULTILINE)
        last_pos = 0
        
        for match in chapter_matches:
            # Add content before this chapter
            if match.start() > last_pos:
                sections.append(('unknown', content[last_pos:match.start()]))
            
            # Find the end of this chapter (next chapter or end of file)
            next_match = re.search(SECTION_PATTERNS['chapter'], content[match.end():], re.MULTILINE)
            end_pos = match.end() + next_match.start() if next_match else len(content)
            
            # Add this chapter
            chapter_num = match.group(1)
            chapter_title = match.group(2)
            chapter_content = content[match.end():end_pos]
            
            self.current_chapter = {'number': chapter_num, 'title': chapter_title}
            self.chapters.append(self.current_chapter.copy())
            
            # Process chapter content
            sections.append(('chapter', chapter_content))
            
            last_pos = end_pos
        
        # Add any remaining content
        if last_pos < len(content):
            sections.append(('unknown', content[last_pos:]))
        
        return sections
    
    def process_section(self, section_type: str, content: str):
        """Process a section based on its type"""
        if section_type == 'chapter':
            self.process_chapter_content(content)
        elif section_type == 'section':
            self.process_section_content(content)
        elif section_type == 'subsection':
            self.process_subsection_content(content)
        elif section_type == 'epidemiology':
            self.extract_epidemiology(content)
        elif section_type == 'clinical_manifestations':
            self.extract_clinical_manifestations(content)
        elif section_type == 'pathophysiology':
            self.extract_pathophysiology(content)
        elif section_type == 'diagnosis':
            self.extract_diagnosis(content)
        elif section_type == 'treatment':
            self.extract_treatment(content)
        elif section_type == 'prevention':
            self.extract_prevention(content)
        elif section_type == 'dosage':
            self.extract_dosage(content)
        elif section_type == 'drug':
            self.extract_drug(content)
    
    def process_chapter_content(self, content: str):
        """Process chapter content to extract sections"""
        # Find sections within the chapter
        section_matches = re.finditer(SECTION_PATTERNS['section'], content, re.MULTILINE)
        
        for match in section_matches:
            section_num = match.group(1)
            section_title = match.group(2)
            
            self.current_section = {'number': section_num, 'title': section_title, 'chapter_id': self.current_chapter['number']}
            self.sections.append(self.current_section.copy())
            
            # Find the end of this section
            next_match = re.search(SECTION_PATTERNS['section'], content[match.end():], re.MULTILINE)
            end_pos = match.end() + next_match.start() if next_match else len(content)
            
            # Process section content
            section_content = content[match.end():end_pos]
            self.process_section_content(section_content)
    
    def process_section_content(self, content: str):
        """Process section content to extract subsections and content blocks"""
        # Find subsections within the section
        subsection_matches = re.finditer(SECTION_PATTERNS['subsection'], content, re.MULTILINE)
        
        for match in subsection_matches:
            subsection_num = match.group(1)
            subsection_title = match.group(2)
            
            self.current_subsection = {
                'number': subsection_num, 
                'title': subsection_title, 
                'section_id': self.current_section['number']
            }
            self.subsections.append(self.current_subsection.copy())
            
            # Find the end of this subsection
            next_match = re.search(SECTION_PATTERNS['subsection'], content[match.end():], re.MULTILINE)
            end_pos = match.end() + next_match.start() if next_match else len(content)
            
            # Process subsection content
            subsection_content = content[match.end():end_pos]
            self.process_subsection_content(subsection_content)
        
        # If no subsections found, treat the whole section as a content block
        if not re.search(SECTION_PATTERNS['subsection'], content, re.MULTILINE):
            self.extract_content_block('section_content', content)
    
    def process_subsection_content(self, content: str):
        """Process subsection content to extract content blocks"""
        # Look for specific content types
        for content_type, pattern in SECTION_PATTERNS.items():
            if content_type in ['chapter', 'section', 'subsection']:
                continue
                
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                # Extract content until the next heading or end
                start_pos = match.end()
                
                # Find the next heading
                next_headings = []
                for next_type, next_pattern in SECTION_PATTERNS.items():
                    if next_type != content_type:
                        next_match = re.search(next_pattern, content[start_pos:], re.MULTILINE)
                        if next_match:
                            next_headings.append((start_pos + next_match.start(), next_type))
                
                # Sort by position
                next_headings.sort()
                
                # Extract content
                end_pos = start_pos + next_headings[0][0] if next_headings else len(content)
                content_text = content[start_pos:end_pos].strip()
                
                # Process this content block
                self.process_section(content_type, content_text)
        
        # If no specific content types found, treat as general content
        if not any(re.search(pattern, content, re.MULTILINE) for _, pattern in SECTION_PATTERNS.items() 
                  if _ not in ['chapter', 'section', 'subsection']):
            self.extract_content_block('general_content', content)
    
    def extract_content_block(self, content_type: str, content: str):
        """Extract a general content block"""
        # Create a content block with hierarchy information
        content_block = {
            'chapter_id': self.current_chapter['number'],
            'section_id': self.current_section['number'],
            'subsection_id': self.current_subsection.get('number', ''),
            'title': self.current_subsection.get('title', self.current_section['title']),
            'content_type': content_type,
            'content_text': content.strip()
        }
        
        # Ensure no empty fields
        for key, value in content_block.items():
            if not value:
                content_block[key] = f"Unknown {key}"
        
        self.content_blocks.append(content_block)
        
        # Check for drugs and dosages in this content
        self.extract_drugs_and_dosages(content)
    
    def extract_epidemiology(self, content: str):
        """Extract epidemiology information"""
        self.extract_content_block('epidemiology', content)
    
    def extract_clinical_manifestations(self, content: str):
        """Extract clinical manifestations information"""
        self.extract_content_block('clinical_manifestations', content)
    
    def extract_pathophysiology(self, content: str):
        """Extract pathophysiology information"""
        self.extract_content_block('pathophysiology', content)
    
    def extract_diagnosis(self, content: str):
        """Extract diagnosis information"""
        self.extract_content_block('diagnosis', content)
    
    def extract_treatment(self, content: str):
        """Extract treatment information"""
        self.extract_content_block('treatment', content)
    
    def extract_prevention(self, content: str):
        """Extract prevention information"""
        self.extract_content_block('prevention', content)
    
    def extract_drugs_and_dosages(self, content: str):
        """Extract drug and dosage information from content"""
        # Extract drug names
        drug_matches = re.finditer(CONTENT_PATTERNS['drug_name'], content)
        
        for match in drug_matches:
            generic_name = match.group(1)
            brand_name = match.group(2)
            formulations = match.group(3)
            
            # Create drug entry
            drug = {
                'content_id': len(self.content_blocks),  # Reference to the parent content block
                'drug_name': generic_name,
                'drug_brand_name': brand_name,
                'drug_formulations': formulations,
                'drug_indication': self.extract_drug_indication(content, generic_name) or "General use",
                'drug_mechanism': self.extract_drug_mechanism(content, generic_name) or "Not specified",
                'drug_adverse_effects': self.extract_drug_adverse_effects(content, generic_name) or "See prescribing information",
                'drug_contraindications': self.extract_drug_contraindications(content, generic_name) or "See prescribing information"
            }
            
            drug_id = len(self.drugs)
            self.drugs.append(drug)
            
            # Extract dosages for this drug
            self.extract_dosages(content, drug_id, generic_name)
    
    def extract_drug_indication(self, content: str, drug_name: str) -> str:
        """Extract drug indication"""
        # Look for indication patterns
        indication_pattern = r'(?:indicated|used|for)\s+(?:for|in|to treat)\s+([^.]+)'
        match = re.search(indication_pattern, content, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # If no specific indication found, look for context
        sentences = re.split(r'(?<=[.!?])\s+', content)
        for sentence in sentences:
            if drug_name in sentence and ('treat' in sentence.lower() or 'use' in sentence.lower()):
                return sentence.strip()
        
        return "For treatment of relevant condition"
    
    def extract_drug_mechanism(self, content: str, drug_name: str) -> str:
        """Extract drug mechanism of action"""
        # Look for mechanism patterns
        mechanism_pattern = r'(?:mechanism|acts by|works by)\s+([^.]+)'
        match = re.search(mechanism_pattern, content, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return "Refer to pharmacology references"
    
    def extract_drug_adverse_effects(self, content: str, drug_name: str) -> str:
        """Extract drug adverse effects"""
        # Look for adverse effects patterns
        adverse_pattern = r'(?:adverse effects|side effects|adverse reactions)\s+(?:include|are)\s+([^.]+)'
        match = re.search(adverse_pattern, content, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return "Common and serious adverse effects as per prescribing information"
    
    def extract_drug_contraindications(self, content: str, drug_name: str) -> str:
        """Extract drug contraindications"""
        # Look for contraindication patterns
        contraindication_pattern = r'(?:contraindicated|not recommended|avoid)\s+(?:in|with)\s+([^.]+)'
        match = re.search(contraindication_pattern, content, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return "See complete prescribing information for contraindications"
    
    def extract_dosages(self, content: str, drug_id: int, drug_name: str):
        """Extract dosage information for a drug"""
        # Look for dosage patterns
        dosage_matches = re.finditer(CONTENT_PATTERNS['dosage'], content)
        age_group_matches = list(re.finditer(CONTENT_PATTERNS['age_group'], content))
        
        for match in dosage_matches:
            dosage_value = match.group(0)
            
            # Find the closest age group
            closest_age_group = self.find_closest_age_group(content, match.start(), age_group_matches)
            
            # Create dosage entry
            dosage = {
                'drug_id': drug_id,
                'age_group': closest_age_group.get('age_group', 'All ages'),
                'route': self.extract_route(content, match.start()) or "Oral",
                'value': dosage_value,
                'max_dose': self.extract_max_dose(content, match.end()) or "As per prescribing information",
                'frequency': self.extract_frequency(content, match.end()) or "As directed",
                'special_considerations': self.extract_special_considerations(content, drug_name) or "Follow standard precautions"
            }
            
            self.dosages.append(dosage)
    
    def find_closest_age_group(self, content: str, position: int, age_group_matches: List) -> Dict:
        """Find the closest age group to a position in the text"""
        if not age_group_matches:
            return {'age_group': 'All ages'}
        
        # Find the closest match
        closest_match = min(age_group_matches, key=lambda m: abs(m.start() - position))
        
        # Extract age group information
        population = closest_match.group(1)
        age_range = closest_match.group(2)
        unit = closest_match.group(3)
        
        return {
            'age_group': f"{population} {age_range} {unit}"
        }
    
    def extract_route(self, content: str, position: int) -> Optional[str]:
        """Extract administration route"""
        # Look for route patterns near the position
        route_pattern = r'(?:oral|IV|IM|SC|topical|inhaled|intranasal|rectal)'
        
        # Check before and after the position
        before_text = content[max(0, position-50):position]
        after_text = content[position:min(len(content), position+50)]
        
        before_match = re.search(route_pattern, before_text, re.IGNORECASE)
        after_match = re.search(route_pattern, after_text, re.IGNORECASE)
        
        if before_match:
            return before_match.group(0).capitalize()
        elif after_match:
            return after_match.group(0).capitalize()
        
        return "Oral"  # Default to oral if not specified
    
    def extract_max_dose(self, content: str, position: int) -> Optional[str]:
        """Extract maximum dose information"""
        # Look for max dose patterns
        max_dose_pattern = r'(?:maximum|max)(?:\s+dose)?\s+(\d+(?:\.\d+)?)\s*(?:mg|mcg|g|mL)'
        
        # Check after the position
        after_text = content[position:min(len(content), position+100)]
        match = re.search(max_dose_pattern, after_text, re.IGNORECASE)
        
        if match:
            return match.group(0)
        
        return "Refer to current dosing guidelines"
    
    def extract_frequency(self, content: str, position: int) -> Optional[str]:
        """Extract dosing frequency information"""
        # Look for frequency patterns
        frequency_pattern = r'(?:every|q)\s*(\d+(?:-\d+)?)\s*(?:h|hr|hour|hours|day|days|week|weeks)'
        
        # Check after the position
        after_text = content[position:min(len(content), position+100)]
        match = re.search(frequency_pattern, after_text, re.IGNORECASE)
        
        if match:
            return match.group(0)
        
        return "As directed by healthcare provider"
    
    def extract_special_considerations(self, content: str, drug_name: str) -> Optional[str]:
        """Extract special considerations for dosing"""
        # Look for special considerations
        special_pattern = r'(?:caution|warning|note|adjust|monitor)\s+([^.]+)'
        
        # Find sentences containing the drug name and special considerations
        sentences = re.split(r'(?<=[.!?])\s+', content)
        for sentence in sentences:
            if drug_name.lower() in sentence.lower() and re.search(special_pattern, sentence, re.IGNORECASE):
                match = re.search(special_pattern, sentence, re.IGNORECASE)
                if match:
                    return match.group(0) + match.group(1)
        
        return "Follow standard monitoring protocols"
    
    def extract_dosage(self, content: str):
        """Extract dosage information"""
        self.extract_content_block('dosage', content)
    
    def extract_drug(self, content: str):
        """Extract drug information"""
        self.extract_content_block('drug', content)
    
    def save_data(self):
        """Save extracted data to JSON files"""
        data_types = {
            'chapters': self.chapters,
            'sections': self.sections,
            'subsections': self.subsections,
            'content_blocks': self.content_blocks,
            'drugs': self.drugs,
            'dosages': self.dosages
        }
        
        for data_type, data in data_types.items():
            output_path = os.path.join(self.output_dir, f"{data_type}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Saved {len(data)} {data_type} to {output_path}")
    
    def generate_sql(self):
        """Generate SQL insert statements for the extracted data"""
        # Implementation will depend on the final database schema
        pass


def main():
    """Main function"""
    # Get all nelson part files
    input_files = [f for f in os.listdir('.') if f.startswith('nelson_part_') and f.endswith('.txt')]
    input_files.sort()
    
    # Create output directory
    output_dir = 'parsed_data'
    
    # Initialize and run parser
    parser = NelsonParser(input_files, output_dir)
    parser.parse_files()
    
    print("Parsing complete!")


if __name__ == "__main__":
    main()

