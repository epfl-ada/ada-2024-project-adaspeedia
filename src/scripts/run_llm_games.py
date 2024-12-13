import argparse
from dotenv import load_dotenv
import pandas as pd
from openai import OpenAI
import time
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

DATA_FOLDER = 'data/wikispeedia_paths-and-graph/'

# Read the data files
links = pd.read_csv(DATA_FOLDER + 'links.tsv', sep='\t', skiprows=11, names=['linkSource', 'linkTarget'])

#Changes 13.12: paths_finished now refers to the section of paths_finished where there were loops. 
paths_finished = pd.read_csv('data/paths_finished_unique.tsv', sep='\t', skiprows=1, names=['path_id', 'hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'rating'])
paths_finished_llm = pd.read_csv('data/llm_paths_all_gpt4omini_no_memory.tsv', sep='\t', skiprows=1, names=['path_id', 'steps', 'path'])
mask_loops = (paths_finished_llm['path'].apply(lambda s: s.split(';')[-1] == 'LOOP_DETECTED'))
#quick fix car nous n'avons pas encore compute tous les llm paths (il y en a 28718 à compute au total et non 27501). Nous les computerons avec le reste des loops.
mask_loops = pd.concat([mask_loops, pd.Series(True, index=range(27501,28718))], axis = 0)
paths_finished = paths_finished[mask_loops]

# Prepare the links dictionary for fast lookup
links_dict = links.groupby('linkSource')['linkTarget'].apply(list).to_dict()

# Load or initialize output data structures
paths_file = 'data/llm_paths.tsv'
llm_paths_df = pd.read_csv(paths_file, sep='\t') if os.path.exists(paths_file) else pd.DataFrame(columns=['path_id', 'steps', 'path'])

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Navigate Wikipedia paths using an LLM.')
parser.add_argument('--start_line', type=int, default=0, help='Starting line in paths_finished')
parser.add_argument('--num_items', type=int, default=10, help='Number of items to process')
parser.add_argument('--verbose', action='store_true', default=False, help='Print verbose output')
parser.add_argument('--memory', action='store_true', default=False, help='Include visited history in LLM prompt')
args = parser.parse_args()

start_line = args.start_line
num_items = args.num_items

print("Starting navigation...")

# Keep track of processed paths and skipped items
processed_count = 0

# Iterate over the specified range of paths
for index, row in paths_finished.iloc[start_line:].iterrows():
    if processed_count >= num_items:
        break  # Stop after processing the specified number of items

    path_id = row['path_id']
    path = row['path'].split(';')
    start_article = path[0]
    end_article = path[-1]

    current_article = start_article
    steps = 0
    path_taken = [current_article]
    visited_articles = set([current_article])  # Track visited articles to detect loops

    print(f"\nPath {path_id}: {start_article} -> {end_article}")

    while current_article != end_article:
        # Retrieve the links of the current article
        linked_articles = links_dict.get(current_article, [])

        if not linked_articles:
            print(f"No outgoing links from {current_article}. Appending NO_LINK.")
            path_taken.append('NO_LINK')
            steps = 0  # Set steps to 0 for unfinished path
            break

        print(f"Step {steps}: {current_article}")
        if args.verbose:
            print(f"Available links: {', '.join(linked_articles)}")

        # Prepare the prompt for the LLM
        if args.memory:
            prompt = f"You are navigating Wikipedia from '{start_article}' to '{end_article}'.\n" \
                     f"Path taken so far: {' -> '.join(path_taken)}.\n" \
                     f"Currently at '{current_article}'.\n" \
                     f"Available links: {', '.join(linked_articles)}.\n" \
                     f"Which article would you like to visit next? Respond only with the article name."
        else:
            prompt = f"You are navigating Wikipedia from '{start_article}' to '{end_article}'.\n" \
                     f"Currently at '{current_article}'.\n" \
                     f"Available links: {', '.join(linked_articles)}.\n" \
                     f"Which article would you like to visit next? Respond only with the article name."

        # Call the OpenAI API
        chat_completion = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0,
            n=1
        )

        # Extract the LLM's choice
        choice = chat_completion.choices[0].message.content

        # Validate the choice
        if choice not in linked_articles:
            print(f"Invalid choice '{choice}' made by the LLM. Appending WRONG_ANSWER.")
            path_taken.append('WRONG_ANSWER')
            steps = 0  # Set steps to 0 for invalid choice
            break

        print(f"Selected link: {choice}")

        # Update the path and step
        current_article = choice
        path_taken.append(current_article)
        steps += 1

        # Check for loops
        if current_article in visited_articles:
            print(f"Loop detected at {current_article}. Marking as LOOP_DETECTED.")
            path_taken.append('LOOP_DETECTED')
            steps = 0  # Set steps to 0 for unfinished path
            break
        visited_articles.add(current_article)

        # To comply with OpenAI rate limits
        time.sleep(1)

    # Record the path taken
    llm_paths_df = pd.concat([llm_paths_df, pd.DataFrame({
        'path_id': [path_id],
        'steps': [steps],
        'path': [';'.join(path_taken)]
    })])

    # Increment processed_count
    processed_count += 1

# Save the results to TSV files, appending new rows
llm_paths_df.to_csv(paths_file, sep='\t', index=False, mode='w', header=True)

# Log summary
total_lines = processed_count
print(f"\nNavigation completed.")
print(f"Processed items: {processed_count}")
print(f"So next time, start at line: {processed_count + start_line}")