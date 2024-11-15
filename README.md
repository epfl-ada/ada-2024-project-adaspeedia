
# Ready Player LLM

## Abstract


Robert West et al. showcased a novel method to infer semantic distances between concepts, based on the finished paths of the Wikispeedia online game. These distances where shown to outperform recognized measures of semantic relatedness in 2007. This projects aims to make LLMs play Wikispeedia and extract semantic distance measures from the paths taken, to compare them with the distances extracted from human games. Our objective is to understand what are the differences between the two sets of distances, and which insights we can take from these differences to better understand the emergent properties of LLMs' concept associations. To deepen this study, we enrich our analysis with distances extracted from the embedding space of the considered LLMs that we compare to the distances computed from human and LLM Wikispeedia games.



## Research Questions

### Main question:

How do the semantic distances elicited from LLMs using the Wikispeedia measure of relatedness compare to the ones computed from human games ?


### Some subquestions we aim to answer:
1. What distribution does the difference between human and LLM distances follow?
  - What are the articles for which humans and LLM distances differ, or agree? Do they belong to specific categories?
  - Does the path length correlate with the semantic distance between the starting and goal article of the path?
  - How much difference and for which articles?


2. Do LLMs exhibit the same strategy of “getting away” and then “homing in” as the paper shows humans do? If yes, then:
  - Do we observe a different distribution for the length of the getting away phase and the length of the homing in
    phase between humans and LLMs?

3. Do LLMs find shorter paths than humans on average?

4. Politicization: Is the wikispeedia semantic distance of LLM biased when measured on two articles judged sensitive to associate by the LLM?
  - Does the underlying politicization introduce biases in the computed semantic distance from LLM games?

5. Do we observe the same difference between distances from human games and LLMs games, and between distances from human games and LLM embeddings?
  - Is there a correlation between the distances from LLM games and the ones from LLM embeddings vectors?

6. How is the difficulty rating given by human players related to the path length and the success rate of LLM games?
  - I.e. are games difficult for humans also difficult for LLMs?
  - Limitation: we don’t know if we will have enough data to answer this question, but if not we will focus on the
    other questions. We would need to have the distance data between the start and end article of many paths. And we
    need that these paths also have a difficulty rating.


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

### Dataset 2: Pairwise article distances from an embedding model

We generate this dataset by picking all the pairs of articles encountered along the "homing in" parts of the finished paths. We compute their respective embeddings using the pre-trained embedding model BERT, and then compute the distance between these two embeddings vectors.

The feasibility is ensured as we already finished the processing pipeline and our embedding distances are computed in `data/article_similarities.csv`

This gives us a third measure of semantic distance, on top of the one obtained from the Wikispeedia games played by humans and the one obtained from Wikispeedia games played by LLMs.

## Methods


todo **introduce the words hypothesis testing**


### LLM and Embeddings distances computation

### Mathematical methods for analysis and processing
todo 
Details can be found in the main notebook
### Methods for subquestions 



For now, it seems we would need to:

- [x] Select the articles for which we have a distance value in the original dataset
- [x] Write a script that makes an LLM play Wikispeedia, by, for every game:
  - Picking a starting and a target article (only pairs that already have a distance value in the original dataset)
  - Asking the LLM to pick one of the outlinks in the current article, in a loop until it reaches the target
- [x] Save the results in a dataset with a format similar to `paths_finished.tsv`
- [ ] Compute the distance between the vector embeddings for these pairs of articles that had a distance value in
  the original dataset
  - For this, we need to pick a distance metric to compute the distance between two embeddings vectors: cosine,
    Euclidean, Manhattan, etc.
- [ ] Re-implement the computation of the distance measure described in section 3 of the Wikispeedia paper
- [x] In order to filter out unrelated concepts as described in section 4 of the Wikispeedia paper,
  re-implement the splitting of paths into the “getting away” and “homing in” phases 
  - For this, we need to obtain from Robert West the neural network used to split the paths
  - Or we would have to compute the information game picture in Figure 2 of the paper and split the
   paths on the article with the lowest information gain, but it performs worse than the neural net
- [ ] Compute the distances between articles using only the “homing in” phase determined in the split
- [ ] Rate the quality of the semantic distance measure we obtain, in a similar way to section 5 of the paper
  - Either use humans on MTurk as the original study does
  - Or use an LLM to do the rating
  - Or do both and compare the results
- [ ] Analyze how well our distance measure based on LLM games of Wikispeedia is rated (by humans or by an LLM)
  against the distance measure based on the human games of Wikispeedia and against the distance measure based
  on vector embeddings
- [ ] Draw conclusions as to which method encodes the most “semantic common sense”

Limitations of the approach:
- The performance of the LLM depends on many factors: prompting strategy, keeping all the path in the context or starting fresh at each article along the path, telling it which heuristic to use to pick the next article, etc. These might bias our results, but we chose not to cross-test all of these factors as our dataset seemed good enough, we have already enough questions to explore, and these seemed far from data analysis.

- For now we do not use the same LLM for computation of embedding distances and computation of Wikispeedia distances extracted from LLM games, as we use BERT for embedding distances computation and GPT4o mini or Mistral Large to compute Wikispeedia distances extracted from LLM games.

- If we end up getting exactly the same semantic distances from LLM games and human games, then most of our questions would be trivial to answer, as there would be no difference. We thought this could threaten our project, but we think the odds of this happening are low, and if it happens we can still transpose our questions to the distances obtained via the embeddings models.

## Timeline and organisation 

Week 1: sentiment scoring of the whole dataset with different methods, visualisations will help us determine what method to keep.

Week 2: split tasks across research sub-questions (see above), make visualisations to see which questions are the most interesting, give a strong causal conclusion to each research question.

Week 3: Detailed sentiment trajectory and pattern analysis for the interesting sub questions. We'll delve into the sentiment data aligned with game paths, examining the influence of sentiments. We will try to make statistical models to answer specific questions. Predictive models can be made to help generating the user path for a random pair of articles.

Week 4: Devise a data story from the analyses such that it is aligned with our statistical findings. Begin the webpage.

Week 5: Cleaning the repository and wrapping up the data story webpage, host cohesive and interactive visualisations to display our outcome.


Nov 7th:
- Have the list of pairs of articles for which a distance exists in the original study’s dataset
- Have the dataset of LLM-played Wikispeedia games generated
- Have the dataset distances between the vector embeddings generated
- Have clarified the next deadlines

After P2:

Week 1
- Initial analyses of the computed distances

Week 2
- Decide which questions seem most interesting based on the initial analyses

## Team organization until P3


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
Tell us how the code is arranged, any explanations goes here.



## Project Structure

The directory structure of new project looks like this:

```
├── data                        <- Project data files
│
├── src                         <- Source code
│   ├── data                            <- Data directory
│   ├── models                          <- Model directory
│   ├── utils                           <- Utility directory
│   ├── scripts                         <- Shell scripts
│
├── tests                       <- Tests of any kind
│
├── results.ipynb               <- a well-structured notebook showing the results
│
├── .gitignore                  <- List of files ignored by git
├── pip_requirements.txt        <- File for installing python dependencies
└── README.md
```

