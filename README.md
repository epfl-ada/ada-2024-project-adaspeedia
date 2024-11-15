
# Ready Player LLM

## Abstract

Robert West et al. showcased a novel method to infer semantic distances between concepts, based on the finished paths of the Wikispeedia online game. These distances where shown to outperform recognized measures of semantic relatedness in 2007. This projects aims to make LLMs play Wikispeedia and extract semantic distance measures from the paths taken, to compare them with the distances extracted from human games. Our objective is to understand what are the differences between the two sets of distances, and which insights we can take from these differences to better understand the emergent properties of LLMs' concept associations. To deepen this study, we enrich our analysis with distances extracted from the embedding space of the considered LLMs that we compare to the distances computed from human and LLM Wikispeedia games.


## Research Questions

### Main question:

How do the semantic distances elicited from LLMs using the Wikispeedia measure of relatedness compare to the ones computed from human games ?


### Some subquestions we aim to answer:
1. What distribution does the difference between human and LLM distances follow?

2. Do LLMs exhibit the same strategy of “getting away” and then “homing in” as the paper shows humans do?

3. Do LLMs find shorter paths than humans on average and how do they compare when it comes to finished paths rated as difficult by humans ?

4. Does the moderation of LLMs introduce biases in the computed semantic distance from LLM games, and in particular do LLMs inflate the semantic distance when considering sensitive associations like 'Slavery' and 'African American'?

5. Do we observe the same difference between distances from human games and LLMs games, and between distances from human games and LLM embeddings?

## Additional datasets

We are using two additional datasets that we generate ourselves.

### Dataset 1: Games of Wikispeedia played by LLMs

We wrote a script that makes an LLM play Wikispeedia. For each starting 
article, it picks an outlink to follow until the goal is reached.

At each iteration, we send the LLM:
 1. The title of the current article
 2. The list of its outlinks
 3. The title of the target article
 4. Our prompt instructing it to pick one of the outlinks in order to reach the target

We chose this to have faster and cheaper inference. If the LLM starts going into a loop, our scripts detects
it, stops the process, writes the incomplete path into our dataset along with an indication that this path
went into a loop and is thus incomplete.

We do this for every pair of starting and target articles encountered in 
`paths_finished.tsv`, using both GPT4o-mini and Mistral Large.

The feasibility is ensured as we already finished the processing pipeline and our budget allows for a sufficient number of queries in order to make significant data analysis. 

We use this dataset to compute a measure of semantic distance, in the same way the paper does using Wikispeedia games played by humans.

### Dataset 2: Pairwise article distances from an embedding model

We generate this dataset by picking all the pairs of articles encountered along the "homing in" parts of the finished
paths. We compute their embeddings using the pre-trained embedding model BERT, and then compute both the
cosine similarity and the Euclidean distance between each pair of vectors.

The feasibility is ensured as we already finished the processing pipeline and our embedding distances are computed in `data/article_similarities.csv`

This gives us a third measure of semantic distance.

## Methods

To compute the Wikispeedia semantic distance measures, we use the mathematical methods taken from the paper of Robert
West et al. They are documented in the notebook as we introduce them with 
direct reference to the paper.

Our method for each subquestion:
  1. We use our pipeline to make the LLM play Wikispeedia games and compute the distances based on the finished paths. We take the intersection of distances that were computed from human and LLM games, and describe the statistical properties of their difference, to test if the average semantic distance is higher for LLM or humans given the confidence that our number of samples allow us to have. We extract the pair of articles with a distance difference higher than the third quartile and analyse them to spot patterns, trying to answer the question: What are the articles for which humans and LLM distances differ, or agree? Do they belong to specific categories? We emit hypothesis based on this initial study and search for counter-examples, and plot the mean difference per category.

  2. We compute the mean information gain along the paths, as in Fig 2 of the paper. We check whether the distribution has the same U-shape for LLMs as it has for humans. We can do t-tests for each quantile of path distance, comparing human and LLM information gain each time.

  3. We make the LLM play the Wikispeedia game with every pair of start and goal article that was played by humans, and compare the average length of the path for humans and the LLM. We then compare the mean path length on the subset of paths that have a high difficulty rating to test if the LLM performs significantly better and reaches the goal in less step than humans on difficult tasks. 

  4. To answer this question, we need to:
    - Find associations judged sensitive by the LLM that we can study: We extract every pair of articles for which we have the distance computed from human games. To know if these pairs of articles are judged sensitive by the LLM (here we use gpt4o-mini), we can use the `omni-moderation-latest` model made available by openAI. Sensitivity scores are returned per category (e.g. violence, hate). We already implemented the function `verify_sensitivity` to ensure feasibility.
    - We can compare the difference in semantic distances between the LLM and humans by sensitivity score to test the hypothesis that the LLM introduces higher semantic distance when given a sensitive association of concepts (e.g. African Americans and Slavery) 
  5. We repeat the previous analyses but this time comparing human Wikispeedia distances to the embedding distances.
  

Limitations of our approach:
- The LLM’s performance depends on factors like
  prompting strategy, prompting with the current path’s history in the 
  context or not. We do not optimize these as the generated was already 
  valid for analysis.
- For now, the embeddings models do not come from the same LLMs that play 
  the game.
- If human and LLM games give the same distances, we will transpose our 
  questions to the distances obtained from the embeddings.

## Timeline and organisation after P2

Two times per week, we will gather to share progress and have SCRUM meetings. We will use the SCRUM method to profit from new insights we gain when diving deeper into the dataset.

Week 1: Leverage our pipeline to finish building the datasets we need for each subquestion. Start analysing the dataset and visualing key statistics to refine our methods and broaden our understanding of the dataset.

Week 2: Distribute the subquestions and prioritize the most promising ones based on our initial analysis. Emit clear hypothesis for each subquestion and start building tests to challenge these hypotheses. 

Week 3: Consider the insights from the previous weeks' work. Building upon those results, consider potential new questions and insightful results that we can integrate in our data story. Finish analysis on our initial research questions and distribute the new research questions according to the current workload distribution. 

Week 4: Finish the analysis on the second round of research questions. Construct a plan for the final data story to build the website's structure, and merge the subquestions into a coherent narrative according to our main research question. 

Week 5: Two members create strong visualisations to articulate our results and the other three finalize the data story website, getting inspired from the exemples provided from previous years.


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

You can simply run the `results.ipynb` notebook, and it will do all the work: loading the data, computing probabilities
and information gain, splitting paths to get only the “homing in” phase, computing the resulting semantic distance,
computing the distances between the embedding vectors.

We have pre-computed the results of the LLM games and the semantic distances and stored the results in the `data`
folder, because they were expensive to compute.


## Project Structure

```
├── data                        <- Our generated datasets, along with the Wikispeedia dataset that must be downloaded separetely
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

