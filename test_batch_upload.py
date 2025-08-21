#!/usr/bin/env python3
"""
Test Batch Upload to Supabase

This script tests the batch upload functionality with a small sample of data.
"""

import os
import pandas as pd
from batch_upload import batch_upload

def create_sample_csv(input_csv, output_csv, num_rows=100):
    """
    Create a sample CSV file with a subset of rows
    
    Args:
        input_csv: Path to the input CSV file
        output_csv: Path to the output CSV file
        num_rows: Number of rows to include in the sample
    """
    print(f"Creating sample CSV with {num_rows} rows...")
    
    # Read the first num_rows rows from the input CSV
    df = pd.read_csv(input_csv, nrows=num_rows)
    
    # Write to the output CSV
    df.to_csv(output_csv, index=False)
    
    print(f"Sample CSV written to {output_csv}")

def main():
    """Main function"""
    # Set input and output files
    input_csv = "dataset.csv"
    output_csv = "sample_dataset.csv"
    num_rows = 100
    
    # Create sample CSV
    create_sample_csv(input_csv, output_csv, num_rows)
    
    # Test batch upload
    batch_upload(output_csv, batch_size=10, delay_seconds=5)

if __name__ == "__main__":
    main()

