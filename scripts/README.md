# Scripts

This folder contains utility scripts for data analysis and maintenance tasks.

## Files

- **`analyze_column_utility.py`** - Analyzes dataset columns to identify useful vs unnecessary fields for ProCX scope
- **`analyze_dataset.py`** - Compares original and cleaned datasets to identify missing columns
- **`check_excel_sheets.py`** - Checks for multiple sheets in Excel files
- **`fix_unicode.py`** - Fixes Unicode character issues in test files

## Usage

These scripts are standalone utilities for dataset analysis and maintenance:

```bash
# Analyze column utility
python scripts/analyze_column_utility.py

# Analyze dataset differences
python scripts/analyze_dataset.py

# Check Excel sheets
python scripts/check_excel_sheets.py

# Fix Unicode issues
python scripts/fix_unicode.py
```

## Purpose

These scripts are **not part of the main application** - they're development/analysis tools used during:
- Dataset preparation
- Column selection
- Data quality checks
- Test file maintenance
