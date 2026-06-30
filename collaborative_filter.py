import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix

class CollaborativeRecommender:
    def __init__(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame):
        self.ratings = ratings_df
        self.movies = movies_df
        self.movie_idx_map = {}
        self.idx_movie_map = {}
        self.movie_user_matrix_sparse = None
        self.knn_model = None
        self.svd_model = None
        self.latent_matrix = None
        
    def train(self):
        """Train KNN and SVD models on user-item interactions."""
        print("Training Collaborative Recommender...")
        
        # Filter out movies with very few ratings to reduce noise
        ratings_count = self.ratings.groupby('movieId').size()
        popular_movies = ratings_count[ratings_count > 5].index
        filtered_ratings = self.ratings[self.ratings['movieId'].isin(popular_movies)]
        
        # Create User-Item Matrix (Movies as rows, Users as columns)
        user_item_df = filtered_ratings.pivot(index='movieId', columns='userId', values='rating').fillna(0)
        
        self.movie_idx_map = {movie_id: i for i, movie_id in enumerate(user_item_df.index)}
        self.idx_movie_map = {i: movie_id for i, movie_id in enumerate(user_item_df.index)}
        
        self.movie_user_matrix_sparse = csr_matrix(user_item_df.values)
        
        # 1. KNN Model (Item-Based CF)
        self.knn_model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
        self.knn_model.fit(self.movie_user_matrix_sparse)
        
        # 2. SVD Matrix Factorization
        n_components = min(50, self.movie_user_matrix_sparse.shape[1] - 1)
        self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
        self.latent_matrix = self.svd_model.fit_transform(self.movie_user_matrix_sparse)
        
        print("Collaborative Training completed.")
        
    def get_similar_movies_knn(self, movie_id: int, top_n: int = 10) -> list:
        """Get similar movies using KNN based on user ratings."""
        if self.knn_model is None:
            self.train()
            
        if movie_id not in self.movie_idx_map:
            return []
            
        idx = self.movie_idx_map[movie_id]
        distances, indices = self.knn_model.kneighbors(
            self.movie_user_matrix_sparse[idx], 
            n_neighbors=top_n + 1
        )
        
        indices = indices.flatten()[1:]
        distances = distances.flatten()[1:]
        
        rec_movies = []
        for i, neighbor_idx in enumerate(indices):
            m_id = self.idx_movie_map[neighbor_idx]
            movie_data = self.movies[self.movies['movieId'] == m_id].iloc[0].copy().to_dict()
            movie_data['similarity_score'] = round(1 - distances[i], 4)
            movie_data['algorithm'] = 'Collaborative (KNN)'
            rec_movies.append(movie_data)
            
        return rec_movies

    def get_similar_movies_svd(self, movie_id: int, top_n: int = 10) -> list:
        """Get similar movies using SVD latent features."""
        if self.svd_model is None:
            self.train()
            
        if movie_id not in self.movie_idx_map:
            return []
            
        idx = self.movie_idx_map[movie_id]
        
        # Compute cosine similarity between the target movie's latent vector and all others
        target_vec = self.latent_matrix[idx].reshape(1, -1)
        from sklearn.metrics.pairwise import cosine_similarity
        sim_scores = cosine_similarity(target_vec, self.latent_matrix).flatten()
        
        # Sort and get top N (skip index 0 which is the movie itself)
        related_indices = sim_scores.argsort()[::-1][1:top_n+1]
        
        rec_movies = []
        for neighbor_idx in related_indices:
            m_id = self.idx_movie_map[neighbor_idx]
            movie_data = self.movies[self.movies['movieId'] == m_id].iloc[0].copy().to_dict()
            movie_data['similarity_score'] = round(sim_scores[neighbor_idx], 4)
            movie_data['algorithm'] = 'Collaborative (SVD)'
            rec_movies.append(movie_data)
            
        return rec_movies
