#!/usr/bin/env python3
"""
Generate INSERT SQL for Nelson Pediatrics Dataset

This script generates SQL INSERT statements for the Nelson Pediatrics dataset.
"""

import os
import csv
import pandas as pd

def escape_sql_string(s):
    """Escape a string for SQL"""
    if pd.isna(s):
        return "''"
    return "'" + str(s).replace("'", "''") + "'"

def generate_insert_sql(csv_file, output_file, batch_size=100):
    """
    Generate SQL INSERT statements for the CSV file
    
    Args:
        csv_file: Path to the CSV file
        output_file: Path to the output SQL file
        batch_size: Number of rows per INSERT statement
    """
    print(f"Reading {csv_file}...")
    
    # Read CSV file
    df = pd.read_csv(csv_file)
    total_rows = len(df)
    print(f"Total rows: {total_rows}")
    
    # Get column names
    columns = df.columns.tolist()
    
    # Open output file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write table creation statement
        f.write("-- Create the nelson_pediatrics table\n")
        f.write("CREATE TABLE IF NOT EXISTS nelson_pediatrics (\n")
        f.write("    id BIGSERIAL PRIMARY KEY,\n")
        
        for column in columns:
            f.write(f"    {column} TEXT,\n")
        
        f.write("    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),\n")
        f.write("    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()\n")
        f.write(");\n\n")
        
        # Process in batches
        num_batches = (total_rows + batch_size - 1) // batch_size
        
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_rows)
            
            print(f"Processing batch {i+1}/{num_batches} (rows {start_idx+1}-{end_idx})...")
            
            # Get batch
            batch_df = df.iloc[start_idx:end_idx]
            
            # Generate INSERT statement
            f.write(f"-- Batch {i+1}/{num_batches} (rows {start_idx+1}-{end_idx})\n")
            f.write("INSERT INTO nelson_pediatrics (\n    ")
            f.write(",\n    ".join(columns))
            f.write("\n) VALUES\n")
            
            # Generate VALUES for each row
            values = []
            for _, row in batch_df.iterrows():
                row_values = []
                for column in columns:
                    row_values.append(escape_sql_string(row[column]))
                values.append("(" + ", ".join(row_values) + ")")
            
            f.write(",\n".join(values))
            f.write(";\n\n")
    
    print(f"SQL file written to {output_file}")

def main():
    """Main function"""
    # Set input and output files
    csv_file = "dataset.csv"
    output_file = "insert_data.sql"
    batch_size = 100
    
    # Generate INSERT SQL
    generate_insert_sql(csv_file, output_file, batch_size)
    
    print("SQL generation complete!")

if __name__ == "__main__":
    main()

