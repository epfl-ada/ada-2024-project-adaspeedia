
# Let LLM play Wikispeedia!
## How do the semantic distances elicited from LLMs using the Wikispeedia measure of relatedness compare to the ones computed from human games?

## Abstract

Robert West et al. showcased a novel method to infer semantic distances between concepts, based on the finished paths of the Wikispeedia online game. These distances where shown to outperform recognized measures of semantic relatedness in 2007. This projects aims to make LLMs play Wikispeedia and extract semantic distance measures from the paths taken, to compare them with the distances extracted from human games. Our objective is to understand what are the differences between the two sets of distances, and which insights we can take from these differences to better understand the emergent properties of LLMs' concept associations. To deepen this study, we enrich our analysis with distances extracted from the embedding space of the considered LLMs that we compare to the distances computed from human and LLM Wikispeedia games.


## Research Questions

1. What distribution does the difference between human and LLM distances follow?

2. Do LLMs exhibit the same strategy of “getting away” and then “homing in” as the paper shows humans do?

3. Do LLMs find shorter paths than humans on average and how do they compare when it comes to finished paths rated as difficult by humans ?

4. Do we observe the same difference between distances from human games and LLMs games, and between distances from human games and LLM embeddings?

### Alternatives considered

- Which semantic distance is “better” as measured in section 5.2 of the paper? Answering this question was impractical.
- How does prompt engineering impact semantic distance measures ? This question falls out of the scope of our analysis.

## Additional datasets

We are using two additional datasets that we generate ourselves.

### Dataset 1: Games of Wikispeedia played by LLMs

We wrote a script that makes both GPT4o-mini and Mistral Large play 
Wikispeedia. For each starting and goal articles in `paths_finished.tsv`, 
the LLM picks an outlink to follow until the goal is reached.

The feasibility is ensured as we already finished the processing pipeline 
and our budget allows for a sufficient number of queries. 

We use this dataset to compute a second Wikispeedia measure of semantic 
distance.

### Dataset 2: Pairwise article distances from an embedding model

We generated this dataset by picking all the pairs of articles encountered 
along the "homing in" parts of the finished paths. We computed their 
embeddings using the pre-trained embedding model BERT, and then computed 
both the cosine similarity and the Euclidean distance between each pair of 
vectors. This gives us a third measure of semantic distance.

## Methods

We compute the Wikispeedia semantic distance measures as in the paper and as 
described in our notebook.

Our method for each question:
  1. We take the intersection of distances that were computed from human and
     LLM games. We test if the average semantic distance is higher for humans. 
     We extract the pairs of articles with a distance difference higher than 
     the third quartile and analyse them to spot patterns. We emit 
     hypothesis based on this initial study and search for counter-examples. 
     We then plot the mean difference per article category.
  2. We compute the mean information gain along the paths, then check whether 
     the distribution has the same U-shape for LLMs as it has for humans 
     (t-test).
  3. We make the LLM play the Wikispeedia game with every pair of start and goal article that was played by humans, and compare the average length of the path for humans and the LLM. We then compare the mean path length on the subset of paths that have a high difficulty rating to test if the LLM performs significantly better and reaches the goal in less step than humans on difficult tasks.
4. We repeat the previous analyses but this time comparing human Wikispeedia distances to the embedding distances.
  

Limitations of our approach:
- The LLM’s performance depends on factors like
  prompting strategy, prompting with the current path’s history in the 
  context or not. We do not optimize these as the generated was already 
  valid for analysis.
- For now, the embeddings models do not come from the same LLMs that play 
  the game.
- If human and LLM games give the same distances, we will transpose our 
  questions to the distances obtained from the embeddings.

## Contributions of the group members

Paul Madélénat:
- Built the website
- …

Ghita Tagemouati:
- Calculation of the embedding distances and articles similarities using different distance measures
- Generating the mistralai data, part on the openai data (finished and unfinished human paths)
- Description and Analysis of the data
- Analysis of the comparaison between the paths taken by human and the llm
- Analysis of the comparaison between the paths taken by openai llm and the mistralai llm
- Answered research question 3
- Writing some parts of the data story

Ahmed Elalamy:
- …

Thomas Kuntz:
- Compatation of the semantic distances
- Analyses of the difference between human and LLM semantic distances
- Explanation of the methods used to compute probabilities, entropies, information gain and distances
- Comparing the distribution of entropies for humans and for the LLM without memory
- Exploring the correlation between the path length and the semantic distance between the start and goal article, both for humans and LLM without memory
- Answered research question 1 and wrote the corresponding part of the data story
- Modularized and documented all the code from milestone 2


## Quickstart

```bash
# clone project
git clone <project link>
cd <project repo>

# [OPTIONAL] create conda environment
conda create -n <env_name> python=3.11 or ...
conda activate <env_name>

# install requirements
conda install --file requirements.txt
```


### How to use the library

Download [wikispeedia_paths-and-graph.tar.gz](https://snap.stanford.edu/data/wikispeedia/wikispeedia_paths-and-graph.tar.gz)
and uncompress it in the `data` folder to obtain the following:

```
├── data
    └── wikispeedia_paths-and-graph
        ├── articles.tsv
        ├── categories.tsv
        ├── links.tsv
        ├── paths_finished.tsv
        ├── paths_unfinished.tsv
        └── shortest-path-distance-matrix.txt
```

You can find all our analyses in the `results` notebook. We had to split it into 4 parts, otherwise it became too slow and unusable, because of the data, computations and graphics it contains.

We have pre-computed the results of the LLM games and the semantic distances and stored the results in the `data`
folder, because they were expensive to compute.


## Project Structure

```
├── data                        <- Our generated datasets, along with the Wikispeedia dataset that must be downloaded separetely
│
├── website                     <- The website directory (see the readme inside this folder to learn more about how the website is compiled and how to compile it locally
│
├── src                         <- Source code
│   ├── utils                           <- Utility directory
│   ├── scripts                         <- Python scripts to generate our datasets
│
├── results.ipynb               <- a well-structured notebook showing the results
│
├── .gitignore                  <- List of files ignored by git
├── pip_requirements.txt        <- File for installing python dependencies
└── README.md
```

## Run LLM paths
If you want to run the LLM on a given subset of the human paths, just use this command, with `--memory` or not.

```
python src/scripts/run_llm_paths.py --start_line 1000 --num_items 3 --memory
```
