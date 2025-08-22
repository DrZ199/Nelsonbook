#!/usr/bin/env python3
"""
Nelson Textbook of Pediatrics Structured Parser

This script parses the Nelson Textbook of Pediatrics text files into structured data.
"""

import os
import re
import csv
from dataclasses import dataclass
from typing import List, Optional

# ----------------------------
# Utility: simple TSV generator
# ----------------------------

def simple_tsv(text: str) -> str:
    if not text:
        return ""
    words = re.findall(r'\w+', text.lower())
    return ' '.join(sorted(set(words)))

# ----------------------------
# Dataclasses
# ----------------------------

@dataclass
class Chapter:
    chapter_id: int
    part_number: int
    chapter_number: str
    title: str
    title_tsv: str

@dataclass
class Section:
    section_id: int
    chapter_id: int
    section_number: str
    title: str
    title_tsv: str

@dataclass
class ContentBlock:
    block_id: int
    section_id: int
    content: str
    content_tsv: str

@dataclass
class MedicalCondition:
    condition_id: int
    section_id: int
    name: str
    name_tsv: str
    clinical_manifestations: Optional[str] = None
    epidemiology: Optional[str] = None

@dataclass
class Drug:
    drug_id: int
    drug_name: str
    name_tsv: str
    brand_names: Optional[List[str]] = None
    indications: Optional[str] = None

@dataclass
class DrugDosage:
    dosage_id: int
    drug_id: int
    route: str
    dosage: str
    age_group: Optional[str] = None

# ----------------------------
# Parser
# ----------------------------

class NelsonTextParser:
    def __init__(self, txt_dir: str, output_dir: str):
        self.txt_dir = txt_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Counters
        self.chapter_counter = 1
        self.section_counter = 1
        self.block_counter = 1
        self.condition_counter = 1
        self.drug_counter = 1
        self.dosage_counter = 1

        # Storage
        self.chapters: List[Chapter] = []
        self.sections: List[Section] = []
        self.content_blocks: List[ContentBlock] = []
        self.medical_conditions: List[MedicalCondition] = []
        self.drugs: List[Drug] = []
        self.drug_dosages: List[DrugDosage] = []

        # Lookup for drug IDs
        self.drug_lookup = {}

    # ----------------------------
    # Parse directory
    # ----------------------------
    def parse_all(self):
        files = sorted([f for f in os.listdir(self.txt_dir) if f.endswith(".txt")])
        for i, filename in enumerate(files, 1):
            filepath = os.path.join(self.txt_dir, filename)
            self.parse_file(filepath, part_number=i)

    # ----------------------------
    # Parse a single file
    # ----------------------------
    def parse_file(self, filepath: str, part_number: int):
        with open(filepath, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        current_chapter_id = None
        current_section_id = None
        buffer = []

        for line in lines:
            # Detect chapter
            chap_match = re.match(r"^Chapter (\d+)[:\s]+(.+)$", line)
            if chap_match:
                if buffer and current_section_id:
                    self._store_content_block(current_section_id, buffer)
                    buffer = []

                chap_num, title = chap_match.groups()
                chap = Chapter(
                    chapter_id=self.chapter_counter,
                    part_number=part_number,
                    chapter_number=chap_num,
                    title=title,
                    title_tsv=simple_tsv(title)
                )
                self.chapters.append(chap)
                current_chapter_id = self.chapter_counter
                self.chapter_counter += 1
                continue

            # Detect section
            sec_match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
            if sec_match and current_chapter_id:
                if buffer and current_section_id:
                    self._store_content_block(current_section_id, buffer)
                    buffer = []

                sec_num, title = sec_match.groups()
                sec = Section(
                    section_id=self.section_counter,
                    chapter_id=current_chapter_id,
                    section_number=sec_num,
                    title=title,
                    title_tsv=simple_tsv(title)
                )
                self.sections.append(sec)
                current_section_id = self.section_counter
                self.section_counter += 1
                continue

            # Detect drug
            drug_match = re.match(r"^Drug:\s*(.+)$", line)
            if drug_match:
                drug_name = drug_match.group(1).strip()
                if drug_name.lower() not in self.drug_lookup:
                    drug = Drug(
                        drug_id=self.drug_counter,
                        drug_name=drug_name,
                        name_tsv=simple_tsv(drug_name)
                    )
                    self.drugs.append(drug)
                    self.drug_lookup[drug_name.lower()] = self.drug_counter
                    self.drug_counter += 1
                continue

            # Detect dosage
            dosage_match = re.match(r"^Dosage:\s*(.+)$", line)
            if dosage_match and self.drugs:
                dosage_text = dosage_match.group(1).strip()
                last_drug_id = self.drugs[-1].drug_id
                dosage = DrugDosage(
                    dosage_id=self.dosage_counter,
                    drug_id=last_drug_id,
                    route="oral",
                    dosage=dosage_text
                )
                self.drug_dosages.append(dosage)
                self.dosage_counter += 1
                continue

            # Buffer content
            if current_section_id:
                buffer.append(line)

        # Flush leftover buffer
        if buffer and current_section_id:
            self._store_content_block(current_section_id, buffer)

    # ----------------------------
    # Store content block
    # ----------------------------
    def _store_content_block(self, section_id: int, buffer: List[str]):
        text = " ".join(buffer)
        block = ContentBlock(
            block_id=self.block_counter,
            section_id=section_id,
            content=text,
            content_tsv=simple_tsv(text)
        )
        self.content_blocks.append(block)
        self.block_counter += 1

    # ----------------------------
    # Export CSVs
    # ----------------------------
    def export_csvs(self):
        self._export("chapters.csv", self.chapters)
        self._export("sections.csv", self.sections)
        self._export("content_blocks.csv", self.content_blocks)
        self._export("medical_conditions.csv", self.medical_conditions)
        self._export("drugs.csv", self.drugs)
        self._export("drug_dosages.csv", self.drug_dosages)

    def _export(self, filename: str, data):
        if not data:
            return
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].__dataclass_fields__.keys())
            writer.writeheader()
            for row in data:
                row_dict = row.__dict__.copy()
                # truncate long text only for content fields
                if "content" in row_dict:
                    row_dict["content"] = row_dict["content"][:5000]
                writer.writerow(row_dict)

    # ----------------------------
    # Summary
    # ----------------------------
    def summary(self):
        return {
            "chapters": len(self.chapters),
            "sections": len(self.sections),
            "content_blocks": len(self.content_blocks),
            "medical_conditions": len(self.medical_conditions),
            "drugs": len(self.drugs),
            "drug_dosages": len(self.drug_dosages),
        }

# ----------------------------
# Main
# ----------------------------

if __name__ == "__main__":
    parser = NelsonTextParser(txt_dir=".", output_dir="structured_output")
    parser.parse_all()
    parser.export_csvs()
    print("Summary:", parser.summary())

