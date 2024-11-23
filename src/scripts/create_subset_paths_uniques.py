import pandas as pd

# Set the data folder and input file path
DATA_FOLDER = 'data/wikispeedia_paths-and-graph/'  # Replace with your actual path

# Read the original file into a pandas DataFrame
paths_finished = pd.read_csv(DATA_FOLDER + 'paths_finished.tsv', sep='\t', skiprows=15,
                             names=['hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'rating'])

# Helper function to extract the start and end article of the path
def get_start_end(path):
    # The path is a semicolon-separated list of articles
    articles = path.split(';')
    start_article = articles[0]
    end_article = articles[-1]
    return start_article, end_article

# Apply the helper function to get the start and end articles for each path
paths_finished[['start_article', 'end_article']] = paths_finished['path'].apply(
    lambda x: pd.Series(get_start_end(x)))

# Drop duplicates based on start_article and end_article
unique_paths = paths_finished.drop_duplicates(subset=['start_article', 'end_article'])

# Sort the unique paths based on start and end articles to maintain consistency
unique_paths = unique_paths.sort_values(by=['start_article', 'end_article']).reset_index(drop=True)

# Assign sequential path_id from 0 to N-1
unique_paths['path_id'] = unique_paths.index

# Reorder the columns to match the desired output format
unique_paths = unique_paths[['path_id', 'hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'rating']]

# Save the cleaned data to a new .tsv file
output_file = DATA_FOLDER + 'paths_finished_unique.tsv'
unique_paths.to_csv(output_file, sep='\t', index=False)

print(f"Processed file saved to {output_file}")