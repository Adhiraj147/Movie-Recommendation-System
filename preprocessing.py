import os
import urllib.request
import zipfile
import pandas as pd
from typing import Tuple

DATASET_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
DATA_DIR = os.path.join(os.path.dirname(__file__), "dataset")
ZIP_PATH = os.path.join(DATA_DIR, "ml-latest-small.zip")
EXTRACTED_DIR = os.path.join(DATA_DIR, "ml-latest-small")

def download_and_extract() -> None:
    """Download the MovieLens dataset if it doesn't exist and extract it."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(EXTRACTED_DIR):
        if not os.path.exists(ZIP_PATH):
            print(f"Downloading dataset from {DATASET_URL}...")
            urllib.request.urlretrieve(DATASET_URL, ZIP_PATH)
            print("Download complete.")
        
        print("Extracting dataset...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
        print("Extraction complete.")
    else:
        print("Dataset already exists.")

def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load movies, links, and ratings datasets into pandas DataFrames."""
    movies_path = os.path.join(EXTRACTED_DIR, "movies.csv")
    ratings_path = os.path.join(EXTRACTED_DIR, "ratings.csv")
    links_path = os.path.join(EXTRACTED_DIR, "links.csv")
    
    if not os.path.exists(movies_path) or not os.path.exists(ratings_path) or not os.path.exists(links_path):
        download_and_extract()
    
    print("Loading data...")
    movies = pd.read_csv(movies_path)
    ratings = pd.read_csv(ratings_path)
    links = pd.read_csv(links_path)
    
    # Merge links with movies to get tmdbId
    movies = pd.merge(movies, links[['movieId', 'tmdbId']], on='movieId', how='left')
    
    # Clean the dataset: Extract year from title, handle missing values
    movies['year'] = movies['title'].str.extract(r'\((\d{4})\)', expand=False)
    movies['title'] = movies['title'].str.replace(r'\(\d{4}\)', '', regex=True).str.strip()
    
    # Process genres: Replace '|' with space for TF-IDF
    movies['genres'] = movies['genres'].str.replace('|', ' ', regex=False)
    # Remove movies with no genres listed
    movies['genres'] = movies['genres'].replace('(no genres listed)', '')
    
    # Clean ratings
    # We only need userId, movieId, rating
    ratings = ratings[['userId', 'movieId', 'rating']]
    
    print(f"Loaded {len(movies)} movies and {len(ratings)} ratings.")
    return movies, ratings

if __name__ == "__main__":
    download_and_extract()
    movies, ratings = load_data()
    print("Preprocessing completed successfully.")
