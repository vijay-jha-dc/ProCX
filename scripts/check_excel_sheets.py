"""
Check for multiple sheets in Excel files
"""
import pandas as pd

def check_excel_sheets():
    """Check all sheets in the Excel files."""
    
    files = [
        'data/AgentMAX_CX_dataset.xlsx',
        'data/AgentMAX_CX_dataset_cleaned.xlsx',
        'data/AgentMAX_CX_dataset_optimized.xlsx'
    ]
    
    for file_path in files:
        try:
            print("="*70)
            print(f"FILE: {file_path}")
            print("="*70)
            
            xl = pd.ExcelFile(file_path)
            
            print(f"\nTotal sheets: {len(xl.sheet_names)}")
            print("\nSheet names:")
            for i, sheet in enumerate(xl.sheet_names, 1):
                print(f"  {i}. {sheet}")
            
            print("\n" + "-"*70)
            print("SHEET DETAILS:")
            print("-"*70)
            
            for sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet)
                print(f"\n📊 Sheet: '{sheet}'")
                print(f"   Rows: {len(df)}")
                print(f"   Columns: {len(df.columns)}")
                print(f"   Column names: {list(df.columns)[:5]}{'...' if len(df.columns) > 5 else ''}")
                
                # Show first few rows
                if len(df) > 0:
                    print(f"\n   First 3 rows preview:")
                    print(df.head(3).to_string(max_cols=5))
            
            print("\n")
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}\n")
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}\n")

if __name__ == '__main__':
    check_excel_sheets()
