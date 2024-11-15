
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
  - Is there a correlation between the distances from LLM games and the ones from LLM embeddings vectors?


### Discarded questions:
- Which semantic distance is “better,” i.e. encodes the most “common sense” as measured by crowd-workers in section 5.2 of the paper? Answering this question seemed impractical to implement, whether the ratings would be collected with human crowd-workers or with LLMs instructed to perform the same task (after verifying they give similar results).
- How does the obtained distance measure and its ratings change if we prompt the LLM to use a specific notion of distance while it is playing the game and choosing which links to pick?
- How does prompt engineering impact semantic distance measures ? This question falls out of the scope of our analysis.

## Additional datasets

We are using two additional datasets that we generate ourselves.

### Dataset 1: Games of Wikispeedia played by LLMs

We wrote a script that makes an LLM play Wikispeedia. It works by picking a starting and a goal article, and then iteratively fetching the list of outlinks of this article and asking the LLM to pick one in order
to reach the goal article, until this article is reached. Each new article leads to a new prompt with a fresh context for the LLM. By default, the LLM does not have access to the history of the path it follows. At each
iteration, we send the LLM:
 1. The title of the current article 
 2. The list of its outlinks 
 3. The title of the target article 
 4. Our prompt instructing it to pick one of the outlinks in order to reach the target.

We chose this to have faster and cheaper inference. If the LLM starts going into a loop, our scripts detects
it, stops the process, writes the incomplete path into our dataset along with an indication that this path
went into a loop and is thus incomplete.

We do this for every pair of starting and target articles encountered in `paths_finished.tsv` and we save
it in a similar format, including both articles’ titles along with the game path and its length.

The feasibility is ensured as we already finished the processing pipeline and our budget allows for a sufficient number of queries in order to make significant data analysis. 

We use this dataset to compute a measure of semantic distance, in the same way the paper does using Wikispeedia games played by humans.

We run this process with both GPT4o-mini and Mistral Large and store the results for analysis.

### Dataset 2: Pairwise article distances from an embedding model

We generate this dataset by picking all the pairs of articles encountered along the "homing in" parts of the finished
paths. We compute their respective embeddings using the pre-trained embedding model BERT, and then compute both the
cosine similarity and the Euclidean distance between each pair of vectors.

The feasibility is ensured as we already finished the processing pipeline and our embedding distances are computed in `data/article_similarities.csv`

This gives us a third measure of semantic distance, on top of the one obtained from the Wikispeedia games played by humans and the one obtained from Wikispeedia games played by LLMs.

## Methods

To compute the Wikispeedia semantic distance measures, we use the mathematical methods taken from the paper of Robert
West et al., they are documented in the notebook as we introduce them with direct reference to the paper.

Our method for each subquestion:
  1. We use our pipeline to make the LLM play Wikispeedia games and compute the distances based on the finished paths. We take the intersection of distances that were computed from human and LLM games, and describe the statistical properties of their difference, to test if the average semantic distance is higher for LLM or humans given the confidence that our number of samples allow us to have. We extract the pair of articles with a distance difference higher than the third quartile and analyse them to spot patterns, trying to answer the question: What are the articles for which humans and LLM distances differ, or agree? Do they belong to specific categories? We emit hypothesis based on this initial study and search for counter-examples, and plot the mean difference per category.
  2. We compute the mean information gain along the paths, as in Fig 2 of the paper. We check whether the distribution has the same U-shape for LLMs as it has for humans. We can do t-tests for each quantile of path distance, comparing human and LLM information gain each time.
  3. We make the LLM play the Wikispeedia game with every pair of start and goal article that was played by humans, and compare the average length of the path for humans and the LLM. We then compare the mean path length on the subset of paths that have a high difficulty rating to test if the LLM performs significantly better and reaches the goal in less step than humans on difficult tasks. 
  4. To answer this question, we need to:
    - Find associations judged sensitive by the LLM that we can study: We extract every pair of articles for which we have the distance computed from human games. To know if these pairs of articles are judged sensitive by the LLM (here we use gpt4o-mini), we can use the `omni-moderation-latest` model made available by openAI. Sensitivity scores are returned per category (e.g. violence, hate). We already implemented the function `verify_sensitivity` to ensure feasibility.
    - We can compare the difference in semantic distances between the LLM and humans by sensitivity score to test the hypothesis that the LLM introduces higher semantic distance when given a sensitive association of concepts (e.g. African Americans and Slavery) 
  5. We repeat the previous analyses but this time comparing human Wikispeedia distances to the embedding distances.
  

Limitations of our approach:
- The performance of the LLM depends on many factors: prompting strategy, keeping all the path in the context or
  starting fresh at each article along the path, telling it which heuristic to use to pick the next article, etc. 
  These might bias our results, but we chose not to cross-test all of these factors as our dataset seemed good enough,
  we have already enough questions to explore, and these seemed far from data analysis.
- For now, we do not use the same LLM for computation of embedding distances and computation of Wikispeedia distances
  extracted from LLM games, as we use BERT for embedding distances computation and GPT4o mini or Mistral Large to
  compute Wikispeedia distances extracted from LLM games.
- If we end up getting exactly the same semantic distances from LLM games and human games, then most of our questions
  would be trivial to answer, as there would be no difference. We thought this could threaten our project, but we think
  the odds of this happening are low, and if it happens we can still transpose our questions to the distances obtained
  via the embeddings models.

## Timeline and organisation after P2

Week 1: sentiment scoring of the whole dataset with different methods, visualisations will help us determine what method to keep.

Week 2: split tasks across research sub-questions (see above), make visualisations to see which questions are the most interesting, give a strong causal conclusion to each research question.

Week 3: Detailed sentiment trajectory and pattern analysis for the interesting sub questions. We'll delve into the sentiment data aligned with game paths, examining the influence of sentiments. We will try to make statistical models to answer specific questions. Predictive models can be made to help generating the user path for a random pair of articles.

Week 4: Devise a data story from the analyses such that it is aligned with our statistical findings. Begin the webpage.

Week 5: Cleaning the repository and wrapping up the data story webpage, host cohesive and interactive visualisations to display our outcome.

---

Week 1
- Initial analyses of the computed distances

Week 2
- Decide which questions seem most interesting based on the initial analyses

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

