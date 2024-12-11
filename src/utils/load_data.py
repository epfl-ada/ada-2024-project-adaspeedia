import pandas as pd
import urllib.parse


def load_data():
    # Load all the data from the tsv files, skipping the headers and specifying column names
    DATA_FOLDER = 'data/wikispeedia_paths-and-graph/'
    articles = pd.read_csv(DATA_FOLDER + 'articles.tsv', sep='\t', skiprows=12, names=['article'])
    categories = pd.read_csv(DATA_FOLDER + 'categories.tsv', sep='\t', skiprows=12, names=['article', 'category'])
    links = pd.read_csv(DATA_FOLDER + 'links.tsv', sep='\t', skiprows=11, names=['linkSource', 'linkTarget'])
    paths_finished = pd.read_csv(DATA_FOLDER + 'paths_finished.tsv', sep='\t', skiprows=15, names=['hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'rating'])
    paths_unfinished = pd.read_csv(DATA_FOLDER + 'paths_unfinished.tsv', sep='\t', skiprows=16, names=['hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'target', 'type'])

    # Decode the URL-encoded article titles
    articles = articles.map(urllib.parse.unquote)
    categories = categories.map(urllib.parse.unquote)
    links = links.map(urllib.parse.unquote)
    paths_finished['path'] = paths_finished['path'].map(urllib.parse.unquote)
    paths_unfinished['path'] = paths_unfinished['path'].map(urllib.parse.unquote)

    # Turn the paths into an array of article titles
    paths_finished['path'] = paths_finished['path'].str.split(';')
    paths_unfinished['path'] = paths_unfinished['path'].str.split(';')

    # Filter out the paths that have only one article, because they don’t seem to mean anything
    paths_finished = paths_finished[paths_finished['path'].apply(len) > 1]

    # Articles is a 1-column DataFrame, so convert it to a Series
    articles = pd.Series(articles['article'])

    # llm_paths_gpt4omini = pd.read_csv('data/llm_paths.tsv', sep='\t')
    # llm_paths_misrtal_large = pd.read_csv('data/llm_paths_mistral_1.tsv', sep='\t')

    return articles, categories, links, paths_finished, paths_unfinished