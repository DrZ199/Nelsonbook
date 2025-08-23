#!/usr/bin/env python3
"""
Enhanced Structured Parser for Nelson Textbook of Pediatrics

This script parses the Nelson Textbook of Pediatrics text files into structured data formats
based on the actual organization of the 22nd Edition textbook.

It extracts volumes, parts, chapters, sections, content blocks, medical conditions, drugs, and drug dosages.
"""

import os
import re
import csv
import glob
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Set, Tuple
import string
import json

# Define data structures
@dataclass
class Volume:
    volume_id: int
    title: str = ""
    start_page: int = 1

@dataclass
class Part:
    part_id: int
    volume_id: int
    part_number: str = ""  # e.g., "I", "V"
    title: str = ""
    start_page: int = 1

@dataclass
class Chapter:
    chapter_id: int
    part_id: int
    chapter_number: Optional[str] = None
    title: str = ""
    title_tsv: str = ""  # Tokenized and sorted title for search
    start_page: int = 1

@dataclass
class Section:
    section_id: int
    chapter_id: int
    section_number: str = ""
    title: str = ""
    title_tsv: str = ""  # Tokenized and sorted title for search

@dataclass
class ContentBlock:
    block_id: int
    section_id: int
    content: str = ""
    content_tsv: str = ""  # Tokenized and sorted content for search

@dataclass
class MedicalCondition:
    condition_id: int
    section_id: int
    name: str = ""
    name_tsv: str = ""  # Tokenized and sorted name for search
    clinical_manifestations: Optional[str] = None
    epidemiology: Optional[str] = None

@dataclass
class Drug:
    drug_id: int
    drug_name: str = ""
    name_tsv: str = ""  # Tokenized and sorted name for search
    brand_names: Optional[str] = None
    indications: Optional[str] = None

@dataclass
class DrugDosage:
    dosage_id: int
    drug_id: int
    route: str = ""
    dosage: str = ""
    age_group: Optional[str] = None

# Helper functions
def tokenize_and_sort(text):
    """Tokenize and sort text for search."""
    if not text:
        return ""
    # Remove punctuation and convert to lowercase
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator).lower()
    # Split into words, sort, and join with spaces
    words = text.split()
    return " ".join(sorted(words))

def extract_part_number(filename):
    """Extract part number from filename."""
    match = re.search(r'nelson_part_(\d+)\.txt', filename)
    if match:
        return int(match.group(1))
    return None

# Main parser class
class EnhancedStructuredParser:
    def __init__(self, output_dir="enhanced_output"):
        self.output_dir = output_dir
        
        # Data structures
        self.volumes = []
        self.parts = []
        self.chapters = []
        self.sections = []
        self.content_blocks = []
        self.medical_conditions = []
        self.drugs = []
        self.drug_dosages = []
        
        # Counters for IDs
        self.volume_id_counter = 1
        self.part_id_counter = 1
        self.chapter_id_counter = 1
        self.section_id_counter = 1
        self.block_id_counter = 1
        self.condition_id_counter = 1
        self.drug_id_counter = 1
        self.dosage_id_counter = 1
        
        # Track drug names to avoid duplicates
        self.drug_names = set()
        self.drug_name_to_id = {}
        
        # Track condition names to avoid duplicates
        self.condition_names = set()
        self.condition_name_to_id = {}
        
        # Initialize textbook structure based on TOC
        self._initialize_textbook_structure()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _initialize_textbook_structure(self):
        """Initialize the textbook structure based on the table of contents."""
        # Create volumes
        volume1 = Volume(volume_id=self.volume_id_counter, title="Core Concepts and Development", start_page=1)
        self.volumes.append(volume1)
        self.volume_id_counter += 1
        
        volume2 = Volume(volume_id=self.volume_id_counter, title="Clinical Disorders and Therapeutics", start_page=1)
        self.volumes.append(volume2)
        self.volume_id_counter += 1
        
        # Create parts for Volume 1
        part1 = Part(part_id=self.part_id_counter, volume_id=volume1.volume_id, part_number="I", 
                    title="The Field of Pediatrics", start_page=1)
        self.parts.append(part1)
        self.part_id_counter += 1
        
        part2 = Part(part_id=self.part_id_counter, volume_id=volume1.volume_id, part_number="II", 
                    title="Growth, Development, and Behavior", start_page=260)
        self.parts.append(part2)
        self.part_id_counter += 1
        
        # Create parts for Volume 2
        part5 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="V", 
                    title="Cardiovascular Disease", start_page=1)
        self.parts.append(part5)
        self.part_id_counter += 1
        
        part6 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="VI", 
                    title="Respiratory Disease", start_page=225)
        self.parts.append(part6)
        self.part_id_counter += 1
        
        part7 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="VII", 
                    title="Hematology and Oncology", start_page=415)
        self.parts.append(part7)
        self.part_id_counter += 1
        
        part8 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="VIII", 
                    title="Gastroenterology and Nutrition", start_page=670)
        self.parts.append(part8)
        self.part_id_counter += 1
        
        part9 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="IX", 
                    title="Endocrinology", start_page=910)
        self.parts.append(part9)
        self.part_id_counter += 1
        
        part10 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="X", 
                     title="Nephrology and Urology", start_page=1030)
        self.parts.append(part10)
        self.part_id_counter += 1
        
        part11 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="XI", 
                     title="Neurology", start_page=1135)
        self.parts.append(part11)
        self.part_id_counter += 1
        
        part12 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="XII", 
                     title="Infectious Diseases", start_page=1240)
        self.parts.append(part12)
        self.part_id_counter += 1
        
        part13 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="XIII", 
                     title="Rheumatology and Immunology", start_page=1345)
        self.parts.append(part13)
        self.part_id_counter += 1
        
        part14 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="XIV", 
                     title="Critical Care", start_page=1435)
        self.parts.append(part14)
        self.part_id_counter += 1
        
        part15 = Part(part_id=self.part_id_counter, volume_id=volume2.volume_id, part_number="XV", 
                     title="Surgery", start_page=1525)
        self.parts.append(part15)
        self.part_id_counter += 1
        
        # Initialize chapters based on TOC
        self._initialize_chapters()
        
        # Load common drugs and conditions
        self.common_drugs = self._load_common_drugs()
        self.common_conditions = self._load_common_conditions()
        
        # Add conditions from chapter titles
        self._add_conditions_from_chapters()
    
    def _initialize_chapters(self):
        """Initialize chapters based on the table of contents."""
        # Part I chapters
        self._add_chapter(part_id=1, title="Overview of Pediatrics", start_page=1)
        self._add_chapter(part_id=1, title="Child Health Disparities", start_page=20)
        self._add_chapter(part_id=1, title="Global Child Health", start_page=35)
        self._add_chapter(part_id=1, title="Quality and Value in Healthcare for Children", start_page=50)
        self._add_chapter(part_id=1, title="Safety in Healthcare for Children", start_page=65)
        self._add_chapter(part_id=1, title="Ethics in Pediatric Care", start_page=80)
        self._add_chapter(part_id=1, title="Pediatric Palliative Care", start_page=95)
        self._add_chapter(part_id=1, title="Domestic and International Adoption", start_page=110)
        self._add_chapter(part_id=1, title="Foster and Kinship Care", start_page=125)
        self._add_chapter(part_id=1, title="Medical Evaluation of the Foreign-Born Child", start_page=140)
        self._add_chapter(part_id=1, title="Cultural Issues in Pediatric Care", start_page=155)
        self._add_chapter(part_id=1, title="Maximizing Children's Health: Screening, Counseling", start_page=170)
        self._add_chapter(part_id=1, title="Injury Control", start_page=185)
        self._add_chapter(part_id=1, title="Impact of Violence Exposure on Children", start_page=200)
        self._add_chapter(part_id=1, title="Child Trafficking for Sex and Labor", start_page=215)
        self._add_chapter(part_id=1, title="Abused and Neglected Children", start_page=230)
        self._add_chapter(part_id=1, title="Strategies for Health Behavior Change", start_page=245)
        
        # Part II chapters
        self._add_chapter(part_id=2, title="Developmental and Behavioral Theories", start_page=260)
        self._add_chapter(part_id=2, title="Positive Parenting and Support", start_page=275)
        self._add_chapter(part_id=2, title="Assessment of Fetal Growth and Development", start_page=290)
        self._add_chapter(part_id=2, title="The Newborn", start_page=305)
        self._add_chapter(part_id=2, title="The First Year", start_page=320)
        self._add_chapter(part_id=2, title="The Second Year", start_page=335)
        self._add_chapter(part_id=2, title="The Preschool Years", start_page=350)
        self._add_chapter(part_id=2, title="Middle Childhood", start_page=365)
        self._add_chapter(part_id=2, title="Adolescence", start_page=380)
        self._add_chapter(part_id=2, title="Assessment of Growth", start_page=395)
        self._add_chapter(part_id=2, title="Developmental and Behavioral Screening", start_page=410)
        self._add_chapter(part_id=2, title="Child Care", start_page=425)
        self._add_chapter(part_id=2, title="Loss, Separation, and Bereavement", start_page=440)
        self._add_chapter(part_id=2, title="Sleep Medicine", start_page=455)
        
        # Part V chapters
        self._add_chapter(part_id=3, title="Congenital Heart Disease", start_page=1)
        self._add_chapter(part_id=3, title="Acquired Heart Disease", start_page=25)
        self._add_chapter(part_id=3, title="Hypertension", start_page=50)
        self._add_chapter(part_id=3, title="Dyslipidemia", start_page=70)
        self._add_chapter(part_id=3, title="Cardiomyopathies", start_page=90)
        self._add_chapter(part_id=3, title="Arrhythmias", start_page=110)
        self._add_chapter(part_id=3, title="Heart Failure", start_page=130)
        self._add_chapter(part_id=3, title="Cardiac Transplantation", start_page=150)
        self._add_chapter(part_id=3, title="Endocarditis", start_page=170)
        self._add_chapter(part_id=3, title="Hypercoagulable States", start_page=190)
        self._add_chapter(part_id=3, title="Cardiovascular Imaging", start_page=210)
        
        # Part VI chapters
        self._add_chapter(part_id=4, title="Upper Respiratory Tract Infections", start_page=225)
        self._add_chapter(part_id=4, title="Lower Respiratory Tract Infections", start_page=240)
        self._add_chapter(part_id=4, title="Asthma", start_page=260)
        self._add_chapter(part_id=4, title="Cystic Fibrosis", start_page=280)
        self._add_chapter(part_id=4, title="Bronchopulmonary Dysplasia", start_page=300)
        self._add_chapter(part_id=4, title="Interstitial Lung Disease", start_page=320)
        self._add_chapter(part_id=4, title="Pulmonary Hypertension", start_page=340)
        self._add_chapter(part_id=4, title="Sleep-Disordered Breathing", start_page=360)
        self._add_chapter(part_id=4, title="Respiratory Failure", start_page=380)
        self._add_chapter(part_id=4, title="Lung Transplantation", start_page=400)
        
        # Add more chapters for other parts as needed...
    
    def _add_chapter(self, part_id, title, start_page):
        """Add a chapter to the chapters list."""
        chapter = Chapter(
            chapter_id=self.chapter_id_counter,
            part_id=part_id,
            title=title,
            title_tsv=tokenize_and_sort(title),
            start_page=start_page
        )
        
        self.chapters.append(chapter)
        self.chapter_id_counter += 1
    
    def _add_conditions_from_chapters(self):
        """Add medical conditions based on chapter titles."""
        condition_chapters = [
            "Asthma", "Cystic Fibrosis", "Hypertension", "Heart Failure", 
            "Endocarditis", "Dyslipidemia", "Diabetes Mellitus", "Obesity",
            "Cerebral Palsy", "Seizure Disorders", "Headache and Migraine",
            "Juvenile Arthritis", "Systemic Lupus Erythematosus"
        ]
        
        for chapter in self.chapters:
            if any(condition in chapter.title for condition in condition_chapters):
                # Extract the condition name from the chapter title
                condition_name = chapter.title.split(" and ")[0]  # Handle "Headache and Migraine" case
                
                if condition_name not in self.condition_names:
                    condition = MedicalCondition(
                        condition_id=self.condition_id_counter,
                        section_id=0,  # Will be updated when sections are processed
                        name=condition_name,
                        name_tsv=tokenize_and_sort(condition_name)
                    )
                    
                    self.medical_conditions.append(condition)
                    self.condition_names.add(condition_name)
                    self.condition_name_to_id[condition_name] = self.condition_id_counter
                    self.condition_id_counter += 1
    
    def _load_common_drugs(self):
        """Load common pediatric drugs."""
        # This is a small sample - in a real implementation, this would be loaded from a comprehensive database
        return [
            "acetaminophen", "ibuprofen", "amoxicillin", "ceftriaxone", "albuterol", 
            "fluticasone", "prednisolone", "prednisone", "methylphenidate", "loratadine", 
            "cetirizine", "diphenhydramine", "ondansetron", "azithromycin", "cephalexin",
            "penicillin", "ampicillin", "gentamicin", "vancomycin", "metronidazole",
            "clindamycin", "dexamethasone", "budesonide", "montelukast", "levalbuterol",
            "morphine", "fentanyl", "oxycodone", "hydrocodone", "codeine",
            "meperidine", "tramadol", "midazolam", "lorazepam", "diazepam",
            "phenobarbital", "carbamazepine", "valproic acid", "levetiracetam", "phenytoin",
            "lamotrigine", "topiramate", "gabapentin", "ethosuximide", "clonazepam",
            "insulin", "metformin", "levothyroxine", "hydrocortisone", "fludrocortisone",
            "epinephrine", "norepinephrine", "dopamine", "dobutamine", "milrinone",
            "furosemide", "spironolactone", "hydrochlorothiazide", "enalapril", "captopril",
            "lisinopril", "propranolol", "atenolol", "metoprolol", "carvedilol",
            "digoxin", "adenosine", "amiodarone", "procainamide", "lidocaine",
            "heparin", "enoxaparin", "warfarin", "aspirin", "clopidogrel",
            "ranitidine", "famotidine", "omeprazole", "lansoprazole", "sucralfate",
            "lactulose", "polyethylene glycol", "docusate", "senna", "bisacodyl",
            "metoclopramide", "erythromycin", "domperidone", "nystatin", "fluconazole",
            "acyclovir", "oseltamivir", "ribavirin", "zidovudine", "lamivudine",
            "abacavir", "nevirapine", "efavirenz", "ritonavir", "lopinavir",
            "vitamin a", "vitamin b", "vitamin c", "vitamin d", "vitamin e",
            "vitamin k", "folic acid", "iron", "zinc", "calcium",
            "potassium", "sodium", "magnesium", "phosphorus", "selenium"
        ]
    
    def _load_common_conditions(self):
        """Load common pediatric medical conditions."""
        # This is a small sample - in a real implementation, this would be loaded from a comprehensive database
        return [
            "asthma", "pneumonia", "bronchiolitis", "croup", "otitis media",
            "pharyngitis", "tonsillitis", "sinusitis", "urinary tract infection", "pyelonephritis",
            "gastroenteritis", "appendicitis", "intussusception", "pyloric stenosis", "constipation",
            "eczema", "impetigo", "cellulitis", "scabies", "tinea",
            "meningitis", "encephalitis", "febrile seizure", "epilepsy", "cerebral palsy",
            "attention deficit hyperactivity disorder", "autism spectrum disorder", "depression", "anxiety", "eating disorder",
            "type 1 diabetes", "hypothyroidism", "hyperthyroidism", "adrenal insufficiency", "congenital adrenal hyperplasia",
            "sickle cell disease", "iron deficiency anemia", "hemophilia", "idiopathic thrombocytopenic purpura", "leukemia",
            "lymphoma", "neuroblastoma", "wilms tumor", "osteosarcoma", "rhabdomyosarcoma",
            "congenital heart disease", "ventricular septal defect", "atrial septal defect", "patent ductus arteriosus", "tetralogy of fallot",
            "kawasaki disease", "rheumatic fever", "juvenile idiopathic arthritis", "henoch-schonlein purpura", "systemic lupus erythematosus",
            "nephrotic syndrome", "glomerulonephritis", "hemolytic uremic syndrome", "vesicoureteral reflux", "hydronephrosis",
            "cleft lip", "cleft palate", "pyloric stenosis", "hirschsprung disease", "gastroschisis",
            "down syndrome", "turner syndrome", "fragile x syndrome", "prader-willi syndrome", "williams syndrome",
            "cystic fibrosis", "spinal muscular atrophy", "duchenne muscular dystrophy", "phenylketonuria", "galactosemia",
            "rickets", "scurvy", "failure to thrive", "obesity", "malnutrition",
            "neonatal jaundice", "respiratory distress syndrome", "necrotizing enterocolitis", "intraventricular hemorrhage", "retinopathy of prematurity"
        ]
    
    def parse_files(self, file_pattern="*.txt"):
        """Parse all text files matching the pattern."""
        files = glob.glob(file_pattern)
        files.sort()  # Ensure files are processed in order
        
        # Filter out non-nelson files
        nelson_files = [f for f in files if re.match(r'nelson_part_\d+\.txt', os.path.basename(f))]
        
        if not nelson_files:
            print(f"No Nelson text files found matching pattern: {file_pattern}")
            return
        
        print(f"Processing {len(nelson_files)} Nelson text files...")
        
        # First pass: Extract chapters and sections
        for file_path in nelson_files:
            part_number = extract_part_number(file_path)
            self._extract_chapters_and_sections(file_path, part_number)
        
        # Second pass: Extract content blocks and medical entities
        for file_path in nelson_files:
            self._extract_content_and_entities(file_path)
        
        # Export data to CSV files
        self._export_to_csv()
        
        # Print summary
        self._print_summary()
    
    def _extract_chapters_and_sections(self, file_path, part_number):
        """Extract chapters and sections from a file."""
        print(f"Extracting chapters and sections from {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract chapters
        chapter_pattern = r'Chapter\s+(\d+(?:\.\d+)?)\s*\n+([^\n]+)'
        chapter_matches = re.finditer(chapter_pattern, content)
        
        for match in chapter_matches:
            chapter_number = match.group(1)
            chapter_title = match.group(2).strip()
            
            # Find the appropriate part for this chapter
            part_id = None
            for part in self.parts:
                if part.part_number == str(part_number):
                    part_id = part.part_id
                    break
            
            if part_id is None:
                # Default to the first part if we can't determine
                part_id = self.parts[0].part_id if self.parts else 1
            
            # Create chapter
            chapter = Chapter(
                chapter_id=self.chapter_id_counter,
                part_id=part_id,
                chapter_number=chapter_number,
                title=chapter_title,
                title_tsv=tokenize_and_sort(chapter_title)
            )
            
            self.chapters.append(chapter)
            self.chapter_id_counter += 1
        
        # Extract sections
        # This pattern matches both simple (X.Y) and complex (XXX.Y) section numbers
        section_pattern = r'(\d+\.\d+)\.\s+([^\n]+)'
        section_matches = re.finditer(section_pattern, content)
        
        for match in section_matches:
            section_number = match.group(1)
            section_title = match.group(2).strip()
            
            # Find the appropriate chapter for this section
            # For simplicity, assign to the last chapter if we can't determine
            chapter_id = self.chapters[-1].chapter_id if self.chapters else 1
            
            # Try to match section to chapter based on prefix
            section_prefix = section_number.split('.')[0]
            for chapter in reversed(self.chapters):  # Check most recent chapters first
                if chapter.chapter_number and chapter.chapter_number.startswith(section_prefix):
                    chapter_id = chapter.chapter_id
                    break
            
            # Create section
            section = Section(
                section_id=self.section_id_counter,
                chapter_id=chapter_id,
                section_number=section_number,
                title=section_title,
                title_tsv=tokenize_and_sort(section_title)
            )
            
            self.sections.append(section)
            self.section_id_counter += 1
    
    def _extract_content_and_entities(self, file_path):
        """Extract content blocks and medical entities from a file."""
        print(f"Extracting content and medical entities from {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split content into blocks based on chapter and section markers
        block_pattern = r'(Chapter\s+\d+(?:\.\d+)?|(?:\d+\.\d+)\.\s+[^\n]+)'
        blocks = re.split(block_pattern, content)
        
        current_section_id = None
        current_chapter_id = None
        buffer = ""
        
        for block in blocks:
            if not block or block.isspace():
                continue
            
            # Check if this is a chapter marker
            chapter_match = re.match(r'Chapter\s+(\d+(?:\.\d+)?)', block)
            if chapter_match:
                # Process previous buffer if any
                if buffer and current_section_id:
                    self._process_content_block(buffer, current_section_id)
                    buffer = ""
                
                chapter_number = chapter_match.group(1)
                # Find the chapter ID
                for chapter in self.chapters:
                    if chapter.chapter_number == chapter_number:
                        current_chapter_id = chapter.chapter_id
                        break
                continue
            
            # Check if this is a section marker
            section_match = re.match(r'(\d+\.\d+)\.\s+([^\n]+)', block)
            if section_match:
                # Process previous buffer if any
                if buffer and current_section_id:
                    self._process_content_block(buffer, current_section_id)
                    buffer = ""
                
                section_number = section_match.group(1)
                # Find the section ID
                for section in self.sections:
                    if section.section_number == section_number:
                        current_section_id = section.section_id
                        break
                continue
            
            # This is content - add to buffer
            buffer += block
        
        # Process any remaining buffer
        if buffer and current_section_id:
            self._process_content_block(buffer, current_section_id)
    
    def _process_content_block(self, content, section_id):
        """Process a content block and extract medical entities."""
        # Create content block
        content_block = ContentBlock(
            block_id=self.block_id_counter,
            section_id=section_id,
            content=content,
            content_tsv=tokenize_and_sort(content)
        )
        
        self.content_blocks.append(content_block)
        self.block_id_counter += 1
        
        # Extract drugs with context awareness
        self._extract_drugs_with_context(content, section_id)
        
        # Extract medical conditions with context awareness
        self._extract_conditions_with_context(content, section_id)
    
    def _extract_drugs_with_context(self, content, section_id):
        """Extract drugs and dosages from content with context awareness."""
        # Get the chapter and part for this section to provide context
        chapter_id = None
        part_id = None
        part_title = ""
        
        for section in self.sections:
            if section.section_id == section_id:
                chapter_id = section.chapter_id
                break
        
        if chapter_id:
            for chapter in self.chapters:
                if chapter.chapter_id == chapter_id:
                    part_id = chapter.part_id
                    break
        
        if part_id:
            for part in self.parts:
                if part.part_id == part_id:
                    part_title = part.title
                    break
        
        # Determine if this section is likely to contain drug information
        drug_related_parts = ["Therapeutics", "Pharmacology", "Treatment"]
        is_drug_context = any(term in part_title for term in drug_related_parts)
        
        # Look for common drug names
        for drug_name in self.common_drugs:
            # Use word boundary to match whole words only
            pattern = r'\b' + re.escape(drug_name) + r'\b'
            if re.search(pattern, content.lower()):
                # Check if we've already seen this drug
                if drug_name not in self.drug_names:
                    drug = Drug(
                        drug_id=self.drug_id_counter,
                        drug_name=drug_name,
                        name_tsv=tokenize_and_sort(drug_name)
                    )
                    
                    self.drugs.append(drug)
                    self.drug_names.add(drug_name)
                    self.drug_name_to_id[drug_name] = self.drug_id_counter
                    self.drug_id_counter += 1
                
                # Extract dosage information near drug mentions
                drug_id = self.drug_name_to_id[drug_name]
                
                # If this is a drug-related context, use more aggressive dosage extraction
                if is_drug_context:
                    self._extract_dosages_aggressive(content, drug_id, drug_name)
                else:
                    self._extract_dosages(content, drug_id, drug_name)
    
    def _extract_dosages(self, content, drug_id, drug_name):
        """Extract dosage information for a drug."""
        # Look for dosage patterns near drug mentions
        drug_index = content.lower().find(drug_name.lower())
        if drug_index == -1:
            return
        
        # Extract a window of text around the drug mention
        window_size = 500  # Characters
        start = max(0, drug_index - window_size)
        end = min(len(content), drug_index + len(drug_name) + window_size)
        window = content[start:end]
        
        # Dosage patterns
        dosage_patterns = [
            # Age-based dosing
            r'(\d+(?:-\d+)?\s*(?:yr|year|mo|month|wk|week|day)s?):\s*([\d\.-]+(?:\s*-\s*[\d\.]+)?\s*(?:mg|mcg|g|mL|L|IU|units)(?:/(?:kg|dose|day|hr|h))?(?:\s*(?:q|every)\s*\d+(?:-\d+)?\s*(?:hr|h|min|day))?)',
            
            # Weight-based dosing
            r'(\d+(?:\.\d+)?\s*(?:mg|mcg|g|mL|L|IU|units)(?:/(?:kg|dose|day|hr|h))?)',
            
            # Route and frequency
            r'(PO|IV|IM|SC|PR|SL|intranasal|topical)(?:[:/]\s*)([\d\.-]+(?:\s*-\s*[\d\.]+)?\s*(?:mg|mcg|g|mL|L|IU|units)(?:/(?:kg|dose|day|hr|h))?(?:\s*(?:q|every)\s*\d+(?:-\d+)?\s*(?:hr|h|min|day))?)'
        ]
        
        for pattern in dosage_patterns:
            matches = re.finditer(pattern, window, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    age_group = match.group(1) if 'yr' in match.group(1) or 'mo' in match.group(1) or 'wk' in match.group(1) or 'day' in match.group(1) else None
                    route = match.group(1) if 'PO' in match.group(1) or 'IV' in match.group(1) or 'IM' in match.group(1) or 'SC' in match.group(1) or 'PR' in match.group(1) or 'SL' in match.group(1) else ""
                    dosage = match.group(2) if age_group or route else match.group(1)
                    
                    # Create dosage entry
                    drug_dosage = DrugDosage(
                        dosage_id=self.dosage_id_counter,
                        drug_id=drug_id,
                        route=route,
                        dosage=dosage,
                        age_group=age_group
                    )
                    
                    self.drug_dosages.append(drug_dosage)
                    self.dosage_id_counter += 1
    
    def _extract_dosages_aggressive(self, content, drug_id, drug_name):
        """Extract dosage information for a drug with more aggressive pattern matching."""
        # Similar to _extract_dosages but with wider window and more patterns
        drug_index = content.lower().find(drug_name.lower())
        if drug_index == -1:
            return
        
        # Extract a larger window of text around the drug mention
        window_size = 1000  # Characters
        start = max(0, drug_index - window_size)
        end = min(len(content), drug_index + len(drug_name) + window_size)
        window = content[start:end]
        
        # Additional dosage patterns for aggressive extraction
        dosage_patterns = [
            # Age-based dosing
            r'(\d+(?:-\d+)?\s*(?:yr|year|mo|month|wk|week|day)s?):\s*([\d\.-]+(?:\s*-\s*[\d\.]+)?\s*(?:mg|mcg|g|mL|L|IU|units)(?:/(?:kg|dose|day|hr|h))?(?:\s*(?:q|every)\s*\d+(?:-\d+)?\s*(?:hr|h|min|day))?)',
            
            # Weight-based dosing
            r'(\d+(?:\.\d+)?\s*(?:mg|mcg|g|mL|L|IU|units)(?:/(?:kg|dose|day|hr|h))?)',
            
            # Route and frequency
            r'(PO|IV|IM|SC|PR|SL|intranasal|topical)(?:[:/]\s*)([\d\.-]+(?:\s*-\s*[\d\.]+)?\s*(?:mg|mcg|g|mL|L|IU|units)(?:/(?:kg|dose|day|hr|h))?(?:\s*(?:q|every)\s*\d+(?:-\d+)?\s*(?:hr|h|min|day))?)',
            
            # Dosing frequency
            r'(q\d+(?:-\d+)?h)\s+([\d\.-]+(?:\s*-\s*[\d\.]+)?\s*(?:mg|mcg|g|mL|L|IU|units))',
            
            # Maximum dose
            r'(max(?:imum)?\s+(?:daily|single)?\s*dose)\s+([\d\.-]+(?:\s*-\s*[\d\.]+)?\s*(?:mg|mcg|g|mL|L|IU|units))',
            
            # Loading dose
            r'(loading\s+dose)\s+([\d\.-]+(?:\s*-\s*[\d\.]+)?\s*(?:mg|mcg|g|mL|L|IU|units))',
            
            # Maintenance dose
            r'(maintenance\s+dose)\s+([\d\.-]+(?:\s*-\s*[\d\.]+)?\s*(?:mg|mcg|g|mL|L|IU|units))'
        ]
        
        for pattern in dosage_patterns:
            matches = re.finditer(pattern, window, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 1:
                    # Determine if this is an age group, route, or other context
                    first_group = match.group(1)
                    age_group = first_group if 'yr' in first_group or 'mo' in first_group or 'wk' in first_group or 'day' in first_group else None
                    route = first_group if 'PO' in first_group or 'IV' in first_group or 'IM' in first_group or 'SC' in first_group or 'PR' in first_group or 'SL' in first_group else ""
                    
                    # Get the dosage information
                    if len(match.groups()) >= 2:
                        dosage = match.group(2)
                    else:
                        dosage = first_group
                    
                    # Create dosage entry
                    drug_dosage = DrugDosage(
                        dosage_id=self.dosage_id_counter,
                        drug_id=drug_id,
                        route=route,
                        dosage=dosage,
                        age_group=age_group
                    )
                    
                    self.drug_dosages.append(drug_dosage)
                    self.dosage_id_counter += 1
    
    def _extract_conditions_with_context(self, content, section_id):
        """Extract medical conditions from content with context awareness."""
        # Get the chapter and part for this section to provide context
        chapter_id = None
        chapter_title = ""
        part_id = None
        part_title = ""
        
        for section in self.sections:
            if section.section_id == section_id:
                chapter_id = section.chapter_id
                break
        
        if chapter_id:
            for chapter in self.chapters:
                if chapter.chapter_id == chapter_id:
                    chapter_title = chapter.title
                    part_id = chapter.part_id
                    break
        
        if part_id:
            for part in self.parts:
                if part.part_id == part_id:
                    part_title = part.title
                    break
        
        # Determine if this section is likely to contain condition information
        condition_related_parts = ["Disease", "Disorders", "Clinical", "Pathology"]
        is_condition_context = any(term in part_title for term in condition_related_parts)
        
        # If the chapter title itself is a condition, add it with this section
        for condition in self.medical_conditions:
            if condition.name in chapter_title and condition.section_id == 0:
                # Update the condition with this section ID
                condition.section_id = section_id
        
        # Look for common condition names in the content
        for condition_name in self.common_conditions:
            # Use word boundary to match whole words only
            pattern = r'\b' + re.escape(condition_name) + r'\b'
            if re.search(pattern, content.lower()):
                # Check if we've already seen this condition
                if condition_name not in self.condition_names:
                    condition = MedicalCondition(
                        condition_id=self.condition_id_counter,
                        section_id=section_id,
                        name=condition_name,
                        name_tsv=tokenize_and_sort(condition_name)
                    )
                    
                    self.medical_conditions.append(condition)
                    self.condition_names.add(condition_name)
                    self.condition_name_to_id[condition_name] = self.condition_id_counter
                    self.condition_id_counter += 1
                elif is_condition_context:
                    # If this is a condition-focused context, update the existing condition
                    # to associate it with this more relevant section
                    condition_id = self.condition_name_to_id[condition_name]
                    for condition in self.medical_conditions:
                        if condition.condition_id == condition_id:
                            condition.section_id = section_id
                            break
    
    def _export_to_csv(self):
        """Export data to CSV files."""
        # Export volumes
        self._export_dataclass_to_csv(self.volumes, os.path.join(self.output_dir, "volumes.csv"))
        
        # Export parts
        self._export_dataclass_to_csv(self.parts, os.path.join(self.output_dir, "parts.csv"))
        
        # Export chapters
        self._export_dataclass_to_csv(self.chapters, os.path.join(self.output_dir, "chapters.csv"))
        
        # Export sections
        self._export_dataclass_to_csv(self.sections, os.path.join(self.output_dir, "sections.csv"))
        
        # Export content blocks
        self._export_dataclass_to_csv(self.content_blocks, os.path.join(self.output_dir, "content_blocks.csv"))
        
        # Export medical conditions
        self._export_dataclass_to_csv(self.medical_conditions, os.path.join(self.output_dir, "medical_conditions.csv"))
        
        # Export drugs
        self._export_dataclass_to_csv(self.drugs, os.path.join(self.output_dir, "drugs.csv"))
        
        # Export drug dosages
        self._export_dataclass_to_csv(self.drug_dosages, os.path.join(self.output_dir, "drug_dosages.csv"))
    
    def _export_dataclass_to_csv(self, data_list, file_path):
        """Export a list of dataclass instances to a CSV file."""
        if not data_list:
            print(f"No data to export to {file_path}")
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = asdict(data_list[0]).keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in data_list:
                writer.writerow(asdict(item))
        
        print(f"Exported {len(data_list)} records to {file_path}")
    
    def _print_summary(self):
        """Print a summary of the parsed data."""
        print("\nParsing Summary:")
        print(f"Volumes: {len(self.volumes)}")
        print(f"Parts: {len(self.parts)}")
        print(f"Chapters: {len(self.chapters)}")
        print(f"Sections: {len(self.sections)}")
        print(f"Content Blocks: {len(self.content_blocks)}")
        print(f"Medical Conditions: {len(self.medical_conditions)}")
        print(f"Drugs: {len(self.drugs)}")
        print(f"Drug Dosages: {len(self.drug_dosages)}")

if __name__ == "__main__":
    parser = EnhancedStructuredParser()
    parser.parse_files("nelson_part_*.txt")
