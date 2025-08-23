#!/usr/bin/env python3
"""
Create a comprehensive dataset.csv file from the enhanced parser output files.
This script combines information from volumes, parts, chapters, sections, 
medical conditions, drugs, and drug dosages into a single dataset.
"""

import os
import csv
import pandas as pd
import glob

def load_csv(file_path):
    """Load a CSV file into a pandas DataFrame."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return pd.DataFrame()
    
    return pd.read_csv(file_path)

def create_dataset(input_dir="enhanced_test_output", output_file="dataset.csv"):
    """Create a comprehensive dataset from the parser output files."""
    # Load all CSV files
    volumes_df = load_csv(os.path.join(input_dir, "volumes.csv"))
    parts_df = load_csv(os.path.join(input_dir, "parts.csv"))
    chapters_df = load_csv(os.path.join(input_dir, "chapters.csv"))
    sections_df = load_csv(os.path.join(input_dir, "sections.csv"))
    conditions_df = load_csv(os.path.join(input_dir, "medical_conditions.csv"))
    drugs_df = load_csv(os.path.join(input_dir, "drugs.csv"))
    dosages_df = load_csv(os.path.join(input_dir, "drug_dosages.csv"))
    
    # Check if all required files were loaded
    if any(df.empty for df in [volumes_df, parts_df, chapters_df, sections_df, conditions_df, drugs_df, dosages_df]):
        print("One or more required files are missing or empty.")
        return
    
    # Merge parts with volumes
    parts_with_volumes = pd.merge(
        parts_df,
        volumes_df,
        left_on="volume_id",
        right_on="volume_id",
        how="left",
        suffixes=("", "_volume")
    )
    
    # Merge chapters with parts (which now include volume info)
    chapters_with_parts = pd.merge(
        chapters_df,
        parts_with_volumes,
        left_on="part_id",
        right_on="part_id",
        how="left",
        suffixes=("", "_part")
    )
    
    # Merge sections with chapters (which now include part and volume info)
    sections_with_chapters = pd.merge(
        sections_df,
        chapters_with_parts,
        left_on="chapter_id",
        right_on="chapter_id",
        how="left",
        suffixes=("", "_chapter")
    )
    
    # Merge conditions with sections
    conditions_with_sections = pd.merge(
        conditions_df,
        sections_with_chapters,
        left_on="section_id",
        right_on="section_id",
        how="left",
        suffixes=("", "_section")
    )
    
    # Merge dosages with drugs
    dosages_with_drugs = pd.merge(
        dosages_df,
        drugs_df,
        left_on="drug_id",
        right_on="drug_id",
        how="left",
        suffixes=("", "_drug")
    )
    
    # Create a comprehensive dataset for medical conditions
    condition_dataset = conditions_with_sections[[
        'condition_id', 'name', 'clinical_manifestations', 'epidemiology',
        'section_id', 'section_number', 'title', 
        'chapter_id', 'title_chapter', 'chapter_number',
        'part_id', 'part_number', 'title_part',
        'volume_id', 'title_volume'
    ]].copy()
    
    # Rename columns for clarity
    condition_dataset = condition_dataset.rename(columns={
        'name': 'condition_name',
        'title': 'section_title',
        'title_chapter': 'chapter_title',
        'title_part': 'part_title',
        'title_volume': 'volume_title'
    })
    
    # Create a comprehensive dataset for drugs and dosages
    drug_dataset = dosages_with_drugs[[
        'drug_id', 'drug_name', 'brand_names', 'indications',
        'dosage_id', 'dosage', 'route', 'age_group'
    ]].copy()
    
    # Combine both datasets (using outer join to include all conditions and drugs)
    # This will create a row for each condition-drug combination
    # For simplicity, we'll create separate datasets
    
    # Save the datasets
    condition_dataset.to_csv(os.path.join(input_dir, "condition_dataset.csv"), index=False)
    drug_dataset.to_csv(os.path.join(input_dir, "drug_dataset.csv"), index=False)
    
    # Create a combined dataset with essential information
    # Select key columns from each dataset
    condition_cols = ['condition_id', 'condition_name', 'section_title', 'chapter_title', 'part_title', 'volume_title']
    drug_cols = ['drug_id', 'drug_name', 'dosage', 'route', 'age_group']
    
    # Create a simplified dataset with the most important information
    simplified_conditions = condition_dataset[condition_cols].copy()
    simplified_drugs = drug_dataset[drug_cols].copy()
    
    # Add entity type column to distinguish between conditions and drugs
    simplified_conditions['entity_type'] = 'condition'
    simplified_drugs['entity_type'] = 'drug'
    
    # Rename columns for consistency
    simplified_conditions = simplified_conditions.rename(columns={
        'condition_id': 'entity_id',
        'condition_name': 'entity_name'
    })
    
    simplified_drugs = simplified_drugs.rename(columns={
        'drug_id': 'entity_id',
        'drug_name': 'entity_name'
    })
    
    # Select common columns for the combined dataset
    common_cols = ['entity_id', 'entity_type', 'entity_name']
    
    # Add context columns for conditions
    condition_context_cols = ['section_title', 'chapter_title', 'part_title', 'volume_title']
    
    # Add context columns for drugs
    drug_context_cols = ['dosage', 'route', 'age_group']
    
    # Ensure all columns exist in both dataframes (fill with NaN for missing columns)
    for col in condition_context_cols:
        if col not in simplified_drugs.columns:
            simplified_drugs[col] = None
    
    for col in drug_context_cols:
        if col not in simplified_conditions.columns:
            simplified_conditions[col] = None
    
    # Combine the datasets
    all_cols = common_cols + condition_context_cols + drug_context_cols
    combined_dataset = pd.concat([
        simplified_conditions[all_cols],
        simplified_drugs[all_cols]
    ], ignore_index=True)
    
    # Save the combined dataset
    combined_dataset.to_csv(output_file, index=False)
    print(f"Created combined dataset with {len(combined_dataset)} entries in {output_file}")
    
    return combined_dataset

if __name__ == "__main__":
    create_dataset()
