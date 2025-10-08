import os
import pandas as pd

# Input and output directories
input_dir = "../data/transactions/"
output_dir = "../data/transactions_stmt/"



# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Columns to keep
columns_to_keep = [
    "timestamp",
    "amount",
    "transaction_type",
    "currency",
    "description_raw",
    "user_id",
]

# Iterate over all CSV files in input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".csv"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        try:
            # Read CSV
            df = pd.read_csv(input_path)

            # Select only required columns
            df_filtered = df[columns_to_keep]

            # Save to output folder with same name
            df_filtered.to_csv(output_path, index=False)

            print(f"Processed {filename} -> {output_path}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")



personas_dir = "../data/"
# Columns to keep
columns_to_keep = [
    "full_name",
    "age",
    "gender",
    "location",
    "ethnicity",
    "user_id"
]
input_path = os.path.join(personas_dir, "personas.csv")
output_path = os.path.join(personas_dir, "personas_stmt.csv")

try:
    df = pd.read_csv(input_path)
    df_filtered = df[columns_to_keep]
    df_filtered.to_csv(output_path, index=False)
    print(f"Processed personas.csv -> {output_path}")
except Exception as e:
    print(f"Error processing personas.csv: {e}")

