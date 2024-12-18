import os
import pandas as pd

def merge_tsv_files(directory):
    # Initialize an empty DataFrame
    merged_df = pd.DataFrame()

    # Iterate over all the files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".tsv"):
            file_path = os.path.join(directory, filename)
            # Read the TSV file into a DataFrame
            df = pd.read_csv(file_path, sep='\t')
            # Append the data to the merged DataFrame
            merged_df = pd.concat([merged_df, df], ignore_index=True)

    # Drop duplicate rows based on 'path_id' column, keeping the first occurrence
    duplicates_count = merged_df.duplicated(subset='path_id').sum()
    merged_df.drop_duplicates(subset='path_id', keep='first', inplace=True)
    print(f"Number of duplicate rows: {duplicates_count}")

    return merged_df

# Directory containing the TSV files
directory_path = 'data/to_merge/'
merged_data = merge_tsv_files(directory_path)

# Save the merged DataFrame to a new TSV file
output_path = 'merged_output.tsv'
merged_data.to_csv(output_path, sep='\t', index=False)

print(f"Merged TSV file saved to {output_path}")