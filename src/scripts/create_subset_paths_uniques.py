import pandas as pd

DATA_FOLDER = 'data/wikispeedia_paths-and-graph/'  # Replace with your actual path
paths_finished = pd.read_csv(DATA_FOLDER + 'paths_finished.tsv', sep='\t', skiprows=15,
                             names=['hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'rating'])

# Helper function to extract the start and end article of the path
def get_start_end(path):
    articles = path.split(';')
    start_article = articles[0]
    end_article = articles[-1]
    return start_article, end_article

paths_finished[['start_article', 'end_article']] = paths_finished['path'].apply(
    lambda x: pd.Series(get_start_end(x)))
unique_paths = paths_finished.drop_duplicates(subset=['start_article', 'end_article'])
unique_paths = unique_paths.sort_values(by=['start_article', 'end_article']).reset_index(drop=True)
unique_paths['path_id'] = unique_paths.index
unique_paths = unique_paths[['path_id', 'hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'rating']]
output_file = DATA_FOLDER + 'paths_finished_unique.tsv'
unique_paths.to_csv(output_file, sep='\t', index=False)

print(f"Processed file saved to {output_file}")