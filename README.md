
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

The main questions:
- Would we obtain a different semantic distance measure if an LLM played the Wikispeedia game instead
  of humans?
- How much difference? (quantitative) Of which kind? (qualitative)
- Which measure would be preferred, either by humans or by LLMs? I.e. which measure would give related
  concepts that make the most sense?
- Can we extract another measure of semantic distance from the *embeddings models* used by LLMs,
  and compare it to the previous ones?

The optional questions, to address only if we have the time:
- How does the obtained distance measure and its ratings change if we prompt the LLM to use a specific
  notion of distance while it is playing the game and choosing which links to pick?

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

## Team organization until P3

TODO

## Quickstart

```bash
# clone project
git clone <project link>
cd <project repo>

# [OPTIONAL] create conda environment
conda create -n <env_name> python=3.11 or ...
conda activate <env_name>


# install requirements
pip install -r pip_requirements.txt
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

