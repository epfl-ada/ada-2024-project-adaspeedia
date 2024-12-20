import argparse
import pandas as pd
from openai import OpenAI
import time
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
# Retrieve the API key from environment variables
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)


DATA_FOLDER = 'data/wikispeedia_paths-and-graph/'

# Read the data files
links = pd.read_csv(DATA_FOLDER + 'links.tsv', sep='\t', skiprows=11, names=['linkSource', 'linkTarget'])
paths_unfinished = pd.read_csv('data/paths_unfinished_unique_filtered.tsv', sep='\t', skiprows=1, names=[ 'hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'taget', 'type', 'pair'])


# Prepare the links dictionary for fast lookup
links_dict = links.groupby('linkSource')['linkTarget'].apply(list).to_dict()

# Load or initialize output data structures
paths_file = 'data/llm_paths_unfinished.tsv'
llm_paths_df = pd.read_csv(paths_file, sep='\t') if os.path.exists(paths_file) else pd.DataFrame(columns=['path_id', 'steps', 'path'])

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Navigate Wikipedia paths using an LLM.')
parser.add_argument('--start_line', type=int, default=0, help='Starting line in paths_unfinished')
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
for index, row in paths_unfinished.iloc[start_line:].iterrows():
    if processed_count >= num_items:
        break  # Stop after processing the specified number of items
    path_id = index
    path = row['pair'].split(' -> ')
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
llm_paths_df.to_csv(paths_file, sep='\t', index=False, mode='a', header=not os.path.exists(paths_file))

# Log summary
total_lines = processed_count
print(f"\nNavigation completed.")
print(f"Processed items: {processed_count}")
print(f"So next time, start at line: {processed_count + start_line}")