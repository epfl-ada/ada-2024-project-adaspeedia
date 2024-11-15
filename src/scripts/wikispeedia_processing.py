# Process data
import pandas as pd

DATA_FOLDER = '../../data/wikispeedia_paths-and-graph/'
paths_finished = pd.read_csv(DATA_FOLDER + 'paths_finished.tsv', sep='\t', skiprows=15, names = ['hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'rating'])[['hashedIpAddress', 'path', 'rating']]

# First, replace the NaN values in the rating column with the median
paths_finished.fillna(paths_finished['rating'].median(), inplace=True)
paths_finished.to_csv('../../data/paths_finished_cleaned.tsv', sep='\t', index=False)


paths_finished['path'] = paths_finished['path'].apply(lambda x: x.split(';'))

# TODO: add a column for the semantic distance between the start and end articles

links = pd.read_csv(DATA_FOLDER + 'links.tsv', sep='\t', skiprows=11, names=['linkSource', 'linkTarget'])
links = links.groupby('linkSource').agg(lambda x: x.tolist())

def create_choices_dataframe(paths, links):
    rows = []
    for i, row in enumerate(paths.iterrows()):
        path = row[1]['path']
        # first rewrite the path to deal with '<'
        l = 0
        clean_path = []
        stack = []
        while l < len(path):
            if path[l] != '<':
                stack.append(path[l])
            else:
                clean_path.append('<')
                stack.pop()
            clean_path.append(stack[-1]) # add next article or '<' and previous article 
            l += 1
        
        path = clean_path

        for j in range(len(path) - 1):
            if path[j] not in links.index:
                continue
            dict_row = {'run_id': i, 'article': path[j], 'links': links.loc[path[j]]['linkTarget'] if path[j] in links.index else [], 'link_chosen': path[j+1]}
            rows.append(dict_row)
    return pd.DataFrame(rows)

# Create dataframe without filtering the '<' lines
wikispeedia_choices = create_choices_dataframe(paths_finished, links)

# Now we filter lines with '<' in the path then create the dataframe
paths_finished_no_back = paths_finished[paths_finished['path'].apply(lambda x: '<' not in x)]
wikispeedia_choices_no_back = create_choices_dataframe(paths_finished_no_back, links)

# Save both dataframes in tsv files
wikispeedia_choices.to_csv('../../data/wikispeedia_choices.tsv', sep='\t', index=False)
wikispeedia_choices_no_back.to_csv('../../data/wikispeedia_choices_no_back.tsv', sep='\t', index=False)
