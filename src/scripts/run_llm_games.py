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
paths_finished = pd.read_csv(DATA_FOLDER + 'paths_finished.tsv', sep='\t', skiprows=15, names=['hashedIpAddress', 'timestamp', 'durationInSec', 'path', 'rating'])

# Prepare the links dictionary for fast lookup
links_dict = links.groupby('linkSource')['linkTarget'].apply(list).to_dict()

# Load or initialize output data structures
choices_file = '../../data/llm_choices.tsv'
paths_file = '../../data/llm_paths.tsv'

llm_choices_df = pd.read_csv(choices_file, sep='\t') if os.path.exists(choices_file) else pd.DataFrame(columns=['run_id', 'article', 'links', 'link_chosen'])
llm_paths_df = pd.read_csv(paths_file, sep='\t') if os.path.exists(paths_file) else pd.DataFrame(columns=['run_id', 'steps', 'path'])

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Navigate Wikipedia paths using an LLM.')
parser.add_argument('--start_line', type=int, default=0, help='Starting line in paths_finished')
parser.add_argument('--num_items', type=int, default=10, help='Number of items to process')
parser.add_argument('--start_run_id', type=int, default=0, help='Starting run_id (default: 0)')
parser.add_argument('--verbose', action='store_true', default=False, help='Print verbose output')
args = parser.parse_args()

start_line = args.start_line
num_items = args.num_items
run_id = args.start_run_id

print("Starting navigation...")

# Keep track of processed paths and skipped items
processed_paths = set()
skipped_count = 0
processed_count = 0

# Iterate over the specified range of paths in paths_finished.tsv
for index, row in paths_finished.iloc[start_line:].iterrows():
    if processed_count >= num_items:
        break  # Stop after processing the specified number of items

    path = row['path'].split(';')
    start_article = path[0]
    end_article = path[-1]

    # Check if we've already processed this start-end path
    path_key = (start_article, end_article)
    if path_key in processed_paths:
        print(f"Skipping duplicate path: {start_article} -> {end_article}")
        skipped_count += 1
        continue

    # Mark this path as processed
    processed_paths.add(path_key)
    current_article = start_article
    steps = 0
    path_taken = [current_article]
    visited_articles = set([current_article])  # Track visited articles to detect loops

    print(f"\nPath {run_id}: {start_article} -> {end_article}")

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

        # Record the choice
        llm_choices_df = pd.concat([llm_choices_df, pd.DataFrame({
            'run_id': [run_id],
            'article': [current_article],
            'links': [linked_articles],
            'link_chosen': [choice]
        })])

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
        'run_id': [run_id],
        'steps': [steps],
        'path': [';'.join(path_taken)]
    })])

    # Increment run_id and processed_count
    run_id += 1
    processed_count += 1

# Save the results to TSV files, appending new rows
llm_choices_df.to_csv(choices_file, sep='\t', index=False, mode='a', header=not os.path.exists(choices_file))
llm_paths_df.to_csv(paths_file, sep='\t', index=False, mode='a', header=not os.path.exists(paths_file))

# Log summary
total_lines = processed_count + skipped_count
print(f"\nNavigation completed.")
print(f"Processed items: {processed_count}")
print(f"Skipped items: {skipped_count}")
print(f"Total lines handled: {processed_count + skipped_count}")
print(f"So next time, start at line: {processed_count + skipped_count + start_line}")
print(f"With run_id: {run_id + 1}")