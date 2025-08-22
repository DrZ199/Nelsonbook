# Nelson Pediatrics Structured Parser

This tool parses the Nelson Textbook of Pediatrics text files into structured data formats.

## Overview

The structured parser extracts information from the Nelson Textbook of Pediatrics text files and organizes it into the following structured data types:

1. **Chapters** - Basic chapter information
2. **Sections** - Sections within chapters
3. **Content Blocks** - Text content within sections
4. **Medical Conditions** - Extracted medical conditions
5. **Drugs** - Medication information
6. **Drug Dosages** - Dosage information for medications

## Data Structure

The parser uses Python dataclasses to define the structure of the extracted data:

### Chapter
- `chapter_id`: Unique identifier
- `part_number`: Part number in the textbook
- `chapter_number`: Chapter number
- `title`: Chapter title
- `title_tsv`: Tokenized and sorted chapter title for search

### Section
- `section_id`: Unique identifier
- `chapter_id`: Reference to parent chapter
- `section_number`: Section number
- `title`: Section title
- `title_tsv`: Tokenized and sorted section title for search

### ContentBlock
- `block_id`: Unique identifier
- `section_id`: Reference to parent section
- `content`: Text content
- `content_tsv`: Tokenized and sorted content for search

### MedicalCondition
- `condition_id`: Unique identifier
- `section_id`: Reference to parent section
- `name`: Condition name
- `name_tsv`: Tokenized and sorted name for search
- `clinical_manifestations`: Clinical manifestations (optional)
- `epidemiology`: Epidemiological information (optional)

### Drug
- `drug_id`: Unique identifier
- `drug_name`: Drug name
- `name_tsv`: Tokenized and sorted name for search
- `brand_names`: List of brand names (optional)
- `indications`: Drug indications (optional)

### DrugDosage
- `dosage_id`: Unique identifier
- `drug_id`: Reference to parent drug
- `route`: Administration route
- `dosage`: Dosage information
- `age_group`: Target age group (optional)

## Usage

To use the parser:

```bash
./structured_parser.py
```

The parser will:
1. Read all `.txt` files in the current directory
2. Parse them into structured data
3. Export the data to CSV files in the `structured_output` directory
4. Print a summary of the parsed data

## Output

The parser generates the following CSV files in the `structured_output` directory:

- `chapters.csv` - Chapter information
- `sections.csv` - Section information
- `content_blocks.csv` - Content blocks
- `medical_conditions.csv` - Medical conditions
- `drugs.csv` - Drug information
- `drug_dosages.csv` - Drug dosage information

## Current Results

The current parsing results:
- 2,213 chapters identified
- 1,502 sections processed
- 3,475 content blocks created
- 0 medical conditions detected
- 1 drug detected
- 0 drug dosages detected

## Future Improvements

The parser could be improved in the following ways:

1. Enhanced pattern matching for medical conditions
2. Better drug and dosage detection
3. Extraction of additional metadata
4. Improved section detection
5. Relationship mapping between entities
6. Advanced text processing for better content extraction

