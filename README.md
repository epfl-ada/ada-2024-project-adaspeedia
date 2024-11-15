
# Ready Player LLM

## Abstract

This projects aims to make LLMs play Wikspeedia and extract semantic distance measures from the paths taken.
We will compare this distance measure with the one obtained with human paths.
We will also try to prompt the LLM to navigate the links using different heuristics (geographical similarity,
cultural similarity, temporal similarity, etc.) to see what effect it has on the distance measure obtained.

If we still have time, we will on top of this try to:
- Extract a semantic distance measure from an embedding model used by an LLM
- Make an LLM rate the resulting similarity rankings in the same way the Wikispeedia paper does,
  and compare the LLM’s ratings to the humans’ ratings

## Research Questions

The main question:
- What notion of semantic distance do LLMs have
- Eliciting semantic distances from LLMs
- Comparing semantic distances elicited form LLMs and from humans
- How do LLMs play wikispeedia


Sub-questions:
- Politization: Is the wikispeedia semantic distance of LLM biased when measured on two articles judged sensitive to associate by the LLM?
  Does the underlying politization introduce biases in the computed semantic distance (from LLM games)?
- What distribution does the difference between human and LLM distances follow?
  - What are the articles for which humans and LLM distances differ, or agree? Do they belong to specific categories?
  - How much difference and for which articles?
- Do we observe the same difference between distances from human games and LLMs games, and between distances from human
  games and LLM embeddings?
- Is there a correlation between the distances from LLM games and the ones from LLM embeddings vectors?
- Do LLMs exhibit the same strategy of “getting away” and then “homing in” as the paper shows humans do? If yes, then:
  - Do we observe a different distribution for the length of the getting away phase and the length of the homing in
    phase between humans and LLMs?
- How is the difficulty rating given by human players related to 1) path length and 2) success rate of LLM games?
  - I.e. are games difficult for humans also difficult for LLMs?
  - Limitation: we don’t know if we will have enough data to answer this question, but if not we will focus on the
    other questions. We would need to have the distance data between the start and end article of many paths. And we
    need that these paths also have a difficulty rating.
- Do LLMs find shorter paths than humans in average?

Potential additional sub-questions:
- Does the path length correlate with the semantic distance between the starting and goal article of the path?
- Is there a difference in the frequency of categories visited by humans and LLMs?

Discarded questions:
- Which semantic distance is “better,” i.e. encodes the most “common sense” as measured by crowd-workers in section
  5.2 of the paper? Answering this question seemed impractical to implement, whether the ratings would be collected
  with human crowd-workers or with LLMs instructed to perform the same task (after verifying they give similar results).
- How does the obtained distance measure and its ratings change if we prompt the LLM to use a specific
  notion of distance while it is playing the game and choosing which links to pick?
- prompt engineering

Limitations of the approach (methods):
- The performance of the LLM depends on many factors: prompting strategy, keeping all the path in the context or
  starting fresh at each article along the path, telling it which heuristic to use to pick the next article, etc.
  These might bias our results, but we chose not to cross-test all of these factors as our dataset seemed good
  enough, we have already enough questions to explore, and these seemed far from data analysis.
- If we end up getting exactly the same semantic distances from LLM games and human games, then most of our questions
  would be trivial to answer, as there would be no difference. We thought this could threaten our project, but we think
  the odds of this happening are low, and if it happens we can still transpose our questions to the distances obtained
  via the embeddings models.

## Additional datasets

We are using two additional datasets that we generate ourselves.

### Dataset 1: Games of Wikispeedia played by LLMs

We wrote a script that makes an LLM play Wikispeedia. It works by picking a starting and a goal article,
and then iteratively fetching the list of outlinks of this article and asking the LLM to pick one in order
to reach the goal article, until this article is reached. Each new article leas to a new prompt with a fresh
context for the LLM, we do not keep previous choices made along the path in the LLM’s context. So at each
iteration, we send the LLM 1) the title of the current article 2) the list of its outlinks 3) the title of
the target article 4) our prompt instructing it to pick one of the outlinks in order to reach the target.
We chose this to have faster and cheaper inference. If the LLM starts going into a loop, our scripts detects
it, stops the process, writes the incomplete path into our dataset along with an indication that this path
went into a loop and is thus incomplete.

We do this for every pair of starting and target articles encountered in `paths_finished.tsv` and we save
it in a similar format, including both articles’ titles along with the game path and its length.

We use this dataset to compute a measure of semantic distance, exactly the same way the paper does using
Wikispeedia games played by humans.

### Dataset 2: Pairwise article distances from an embedding model

We generate this dataset by picking the pairs of starting and goal articles we encounter in the original
dataset, by computing their respective embeddings using a pre-trained embedding model (TODO which one),
and computing the distance between these two embeddings vectors.

This gives us a third measure of semantic distance, on top of the one obtained from the Wikispeedia games
played by humans and the one obtained from Wikispeedia games played by LLMs.

## Methods

**hypothesis testing**

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

## Proposed Timeline

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

