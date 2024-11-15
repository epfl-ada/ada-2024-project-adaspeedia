import ast
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean

def get_embeddings_distances(all_articles, all_distance_pairs, file_path):
    """
    Get the data from the .csv file if it’s there, otherwise run the long computation

    Parameters:
        all_articles (set): set of all articles
        all_distance_pairs (set): set of all distance pairs we consider
        file_path (string): path to the csv file

    Returns:
        Pandas DataFrame with columns ['pair', 'cosine_similarity', 'euclidean_distance', 'sbert_cosine_similarity']
    """
    try:
        return pd.read_csv(file_path, converters={'pair': ast.literal_eval})
    except FileNotFoundError:
        generate_embeddings_distances(all_articles, all_distance_pairs, file_path)

def generate_embeddings_distances(all_articles, all_distance_pairs, file_path):
    """
    Run all the computations to get the distances between the pairs of articles we consider

    Parameters:
        all_articles (set): set of all articles
        all_distance_pairs (set): set of all distance pairs we consider
        file_path (string): path to the csv file

    Returns:
        Pandas DataFrame with columns ['pair', 'cosine_similarity', 'euclidean_distance', 'sbert_cosine_similarity']
    """
    model_name = "bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    def get_embedding(text):
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad(): # we are not training the model, so we don't need gradients
            outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embedding

    # calculate the cosine similarity between two embeddings
    def calculate_cosine_similarity(emb_title1, emb_title2):
        emb_title1 = emb_title1.reshape(1, -1)
        emb_title2 = emb_title2.reshape(1, -1)

        similarity = cosine_similarity(emb_title1, emb_title2)[0][0]
        return similarity

    # get the embeddings of all articles and store them in a dictionary
    article_embeddings = {}
    for article in all_articles:
        article_embeddings[article] = get_embedding(article)

    # calculate the cosine similarity between all pairs of articles
    similarities = {}
    for pair in all_distance_pairs:
        title1 = pair[0]
        title2 = pair[1]
        embedding1 = article_embeddings[title1]
        embedding2 = article_embeddings[title2]
        similarities[(title1, title2)] = calculate_cosine_similarity(embedding1, embedding2)

    # convert the cosine similarities to a dataframe
    similarities = pd.DataFrame(similarities.items(), columns=['pair', 'cosine_similarity'])

    # we now try a SBERT model to calculate the similarity between two articles
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer('all-MiniLM-L6-v2')

    def calculate_sbert_similarity(title1, title2):
        # Get embeddings
        embedding1 = model.encode(title1, convert_to_tensor=True)
        embedding2 = model.encode(title2, convert_to_tensor=True)
        # Calculate cosine similarity using SBERT's util function
        similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
        return similarity


    # Calculate SBERT similarities for all pairs
    sbert_similarities = {}
    for pair in all_distance_pairs:
        title1 = pair[0]
        title2 = pair[1]
        similarity = calculate_sbert_similarity(title1, title2)
        sbert_similarities[(title1, title2)] = similarity

    # add a new column to the dataframe with the SBERT cosine similarities
    similarities['sbert_cosine_similarity'] = similarities['pair'].apply(lambda x: sbert_similarities[x])

    # now compute the Euclidean distances

    # Load pre-trained model and tokenizer
    model_name = "bert-base-uncased"  # You can use any suitable model here
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    def get_embedding(text):
        # Tokenize the text and get embeddings
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        # Pool the output to get a single vector representation of the text
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embedding

    def calculate_euclidean_distance(title1, title2):
        # Get embeddings
        embedding1 = get_embedding(title1)
        embedding2 = get_embedding(title2)
        # Convert to numpy arrays for distance calculation
        embedding1_np = embedding1.numpy()
        embedding2_np = embedding2.numpy()
        # Calculate Euclidean distance
        distance = euclidean(embedding1_np, embedding2_np)
        return distance

    # add a column to the dataframe similarities that contains the Euclidean distance between the embeddings of the articles in each pair
    similarities['euclidean_distance'] = similarities['pair'].apply(lambda x: calculate_euclidean_distance(x[0], x[1]))

    # save the dataframe to a csv file
    similarities.to_csv(file_path, index=False)