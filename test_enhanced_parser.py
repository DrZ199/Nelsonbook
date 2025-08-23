#!/usr/bin/env python3
"""
Test version of the Enhanced Structured Parser for Nelson Textbook of Pediatrics
This version processes only one file for testing purposes.
"""

import os
import re
import csv
import glob
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Set, Tuple
import string
import json
from enhanced_structured_parser import Volume, Part, Chapter, Section, ContentBlock, MedicalCondition, Drug, DrugDosage
from enhanced_structured_parser import tokenize_and_sort, extract_part_number, EnhancedStructuredParser

class TestEnhancedParser(EnhancedStructuredParser):
    def __init__(self, output_dir="enhanced_test_output"):
        super().__init__(output_dir)
    
    def parse_file(self, file_path):
        """Parse a single text file."""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        print(f"Processing file: {file_path}")
        
        part_number = extract_part_number(file_path)
        
        # First pass: Extract chapters and sections
        self._extract_chapters_and_sections(file_path, part_number)
        
        # Second pass: Extract content blocks and medical entities
        self._extract_content_and_entities(file_path)
        
        # Export data to CSV files
        self._export_to_csv()
        
        # Print summary
        self._print_summary()

if __name__ == "__main__":
    parser = TestEnhancedParser()
    parser.parse_file("nelson_part_1.txt")
