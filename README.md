# Nelson Pediatrics Database

This repository contains scripts for parsing the Nelson Textbook of Pediatrics content and uploading it to a Supabase database.

## Overview

The Nelson Textbook of Pediatrics is a comprehensive resource for pediatric healthcare professionals. This project extracts structured data from the textbook and makes it available in a searchable database format.

## Features

- Parses the Nelson textbook content into structured data
- Creates a comprehensive database schema
- Uploads the data to Supabase
- Provides scripts for batch processing with rate limiting
- Includes SQL generation tools for manual uploads

## Dataset

The dataset contains 115,402 rows of structured content from the Nelson Textbook of Pediatrics, including:

- Hierarchical structure (chapters, sections, subsections)
- Core medical content (epidemiology, clinical presentation, etc.)
- Drug and dosage information
- Procedure details
- Reference information

## Scripts

- `batch_upload.py`: Uploads the data to Supabase in batches with rate limiting
- `generate_insert_sql.py`: Generates SQL INSERT statements for manual upload
- `split_sql.py`: Splits the SQL file into smaller chunks for manual upload
- `create_table_supabase.py`: Creates the table using the Supabase client
- `test_supabase.py`: Tests the connection to Supabase

## Setup

See the [Setup Instructions](setup_instructions.md) for detailed instructions on setting up the database.

## Usage

To upload the data to Supabase:

```bash
# Set environment variables
export SUPABASE_URL="your-supabase-url"
export SUPABASE_SERVICE_KEY="your-service-key"
export SUPABASE_ANON_KEY="your-anon-key"

# Run the batch upload script
python batch_upload.py --batch-size 50 --delay-seconds 2
```

## License

This project is for educational and research purposes only. The Nelson Textbook of Pediatrics content is copyrighted by Elsevier.

