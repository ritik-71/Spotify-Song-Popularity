# pipelines/data_validation.py
import pandas as pd
import great_expectations as ge
import sys
import os

def validate_ingested_dataset(file_path: str) -> bool:
    """
    Verifies that raw datasets align with expected types and audio metrics ranges.
    """
    if not os.path.exists(file_path):
        print(f"Data file '{file_path}' not found for validation.")
        return False
        
    print(f"Validating dataset quality at '{file_path}'...")
    df = ge.from_pandas(pd.read_csv(file_path, encoding='ISO-8859-1'))
    
    # 1. Column Checks
    df.expect_column_to_exist("Energy")
    df.expect_column_to_exist("Popularity")
    df.expect_column_to_exist("beats_per_minute")
    
    # 2. Null Checks
    df.expect_column_values_to_not_be_null("Track.Name")
    df.expect_column_values_to_not_be_null("Artist.Name")
    
    # 3. Audio Bound Checks
    df.expect_column_values_to_be_between("Energy", min_value=0, max_value=100)
    df.expect_column_values_to_be_between("Danceability", min_value=0, max_value=100)
    df.expect_column_values_to_be_between("Popularity", min_value=0, max_value=100)
    
    results = df.validate()
    success = results["success"]
    
    if success:
        print("Data Validation Successful. Schema is verified and metrics lie within target distributions.")
    else:
        print("Data Validation Failed. Issues detected in features schema or ranges.")
        
    return success

if __name__ == "__main__":
    csv_file = "top50.csv"
    if not os.path.exists(csv_file):
        csv_file = "../top50.csv"
        
    validation_status = validate_ingested_dataset(csv_file)
    sys.exit(0 if validation_status else 1)
