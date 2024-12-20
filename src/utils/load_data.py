import pandas as pd
import urllib.parse


def load_data():
    # Load all the data from the tsv files, skipping the headers and specifying column names
    DATA_FOLDER = 'data/wikispeedia_paths-and-graph/'
    articles = pd.read_csv(DATA_FOLDER + 'articles.tsv', sep='\t', skiprows=12, names=['article'])
    categories = pd.read_csv(DATA_FOLDER + 'categories.tsv', sep='\t', skiprows=12, names=['article', 'category'])
    links = pd.read_csv(DATA_FOLDER + 'links.tsv', sep='\t', skiprows=11, names=['linkSource', 'linkTarget'])
    paths_finished_humans = pd.read_csv(DATA_FOLDER + 'paths_finished.tsv', sep='\t', skiprows=15, names=['hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'rating'])
    paths_finished_llm_no_memory = pd.read_csv('data/llm_paths_all_gpt4omini_no_memory.tsv', sep='\t', skiprows=1, names=['path_id', 'steps', 'path'])
    paths_finished_llm_memory = pd.read_csv('data/llm_paths_all_gpt4omini_memory.tsv', sep='\t', skiprows=1, names=['path_id', 'steps', 'path'])
    paths_unfinished_humans = pd.read_csv(DATA_FOLDER + 'paths_unfinished.tsv', sep='\t', skiprows=16, names=['hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'target', 'type'])

    # Decode the URL-encoded article titles
    articles = articles.map(urllib.parse.unquote)
    categories = categories.map(urllib.parse.unquote)
    links = links.map(urllib.parse.unquote)
    paths_finished_humans['path'] = paths_finished_humans['path'].map(urllib.parse.unquote)
    paths_finished_llm_no_memory['path'] = paths_finished_llm_no_memory['path'].map(urllib.parse.unquote)
    paths_finished_llm_memory['path'] = paths_finished_llm_memory['path'].map(urllib.parse.unquote)
    paths_unfinished_humans['path'] = paths_unfinished_humans['path'].map(urllib.parse.unquote)

    # Turn the paths into an array of article titles
    paths_finished_humans['path'] = paths_finished_humans['path'].str.split(';')
    paths_finished_llm_no_memory['path'] = paths_finished_llm_no_memory['path'].str.split(';')
    paths_finished_llm_memory['path'] = paths_finished_llm_memory['path'].str.split(';')
    paths_unfinished_humans['path'] = paths_unfinished_humans['path'].str.split(';')

    # Filter out the paths that have only one article, because they don’t seem to mean anything
    paths_finished_humans = paths_finished_humans[paths_finished_humans['path'].apply(len) > 1]
    paths_finished_llm_no_memory = paths_finished_llm_no_memory[paths_finished_llm_no_memory['path'].apply(len) > 1]
    paths_finished_llm_memory = paths_finished_llm_memory[paths_finished_llm_memory['path'].apply(len) > 1]

    # Remove loops and wrong answers from llm data
    def get_mask(paths_finished_llm):
        mask_loops = (paths_finished_llm['path'].apply(lambda s: s[-1] == 'LOOP_DETECTED'))
        mask_wrong_answers = (paths_finished_llm['path'].apply(lambda s: s[-1] == 'WRONG_ANSWER'))
        mask_no_link = (paths_finished_llm['path'].apply(lambda s: s[-1] == 'NO_LINK'))
        mask_valid_finished_paths = ~(mask_loops | mask_wrong_answers | mask_no_link)
        return mask_valid_finished_paths

    valid_finished_paths_llm_no_memory = get_mask(paths_finished_llm_no_memory)
    valid_finished_paths_llm_memory = get_mask(paths_finished_llm_memory)
    paths_finished_llm_no_memory = paths_finished_llm_no_memory[valid_finished_paths_llm_no_memory]['path']
    paths_finished_llm_memory = paths_finished_llm_memory[valid_finished_paths_llm_memory]['path']
    # we need to keep the path_id to identify the starting and goal articles.
    paths_unfinished_llm_no_memory = paths_finished_llm_no_memory[~valid_finished_paths_llm_no_memory]
    paths_unfinished_llm_memory = paths_finished_llm_memory[~valid_finished_paths_llm_memory]

    # Articles is a 1-column DataFrame, so convert it to a Series
    articles = pd.Series(articles['article'])

    return articles, categories, links, paths_finished_humans, paths_finished_llm_no_memory, paths_finished_llm_memory, paths_unfinished_humans, paths_unfinished_llm_no_memory, paths_unfinished_llm_memory