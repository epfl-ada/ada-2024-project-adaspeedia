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

# Initialize output data structures
llm_choices = []
llm_paths = []

run_id = 2  # Unique identifier for the run

print("Starting navigation...")

# Iterate over just one path in paths_finished.tsv for testing
for index, row in paths_finished.head(1).iterrows():
    path = row['path'].split(';')
    start_article = path[0]
    end_article = path[-1]

    current_article = start_article
    steps = 0
    path_taken = [current_article]

    print(f"Path: {start_article} -> {end_article}")

    while current_article != end_article:
        # Retrieve the links of the current article
        linked_articles = links_dict.get(current_article, [])

        if not linked_articles:
            print(f"No outgoing links from {current_article}.")
            break

        print(f"Step {steps}: {current_article}")
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
            print(f"Invalid choice '{choice}' made by the LLM. Selecting the first link as fallback.")
            choice = linked_articles[0]

        # Record the choice
        llm_choices.append({
            'run_id': run_id,
            'article': current_article,
            'links': linked_articles,
            'link_chosen': choice
        })

        print(f"Selected link: {choice}")

        # Update the path and step
        current_article = choice
        path_taken.append(current_article)
        steps += 1

        # To comply with OpenAI rate limits
        time.sleep(1)

    # Record the path taken
    llm_paths.append({
        'run_id': run_id,
        'steps': steps,
        'path': ';'.join(path_taken)
    })

# Convert the results to DataFrames
llm_choices_df = pd.DataFrame(llm_choices)
llm_paths_df = pd.DataFrame(llm_paths)

# Save the results to TSV files
llm_choices_df.to_csv('tests/llm_choices.tsv', sep='\t', index=False)
llm_paths_df.to_csv('tests/llm_paths.tsv', sep='\t', index=False)

print("Navigation completed.")