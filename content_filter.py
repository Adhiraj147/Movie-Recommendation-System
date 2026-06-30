import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

class ContentBasedRecommender:
    def __init__(self, movies_df: pd.DataFrame):
        self.movies = movies_df.reset_index(drop=True)
        self.cosine_sim = None
        # Create a reverse mapping of movieId to DataFrame index
        self.indices = pd.Series(self.movies.index, index=self.movies['movieId']).drop_duplicates()
        
    def train(self):
        """Train the TF-IDF model and compute cosine similarity matrix."""
        print("Training Content-Based Recommender...")
        tfidf = TfidfVectorizer(stop_words='english')
        self.movies['genres'] = self.movies['genres'].fillna('')
        
        # Combine genres and title for richer text features
        # (Since we lack overview/description in basic MovieLens, title + genre helps slightly)
        text_features = self.movies['genres'] + " " + self.movies['title']
        
        tfidf_matrix = tfidf.fit_transform(text_features)
        
        # Compute Cosine Similarity (linear_kernel is faster for normalized TF-IDF vectors)
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        print("Content-Based Training completed.")
        
    def get_recommendations(self, movie_id: int, top_n: int = 10) -> list:
        """Get similar movies based on content."""
        if self.cosine_sim is None:
            self.train()
            
        if movie_id not in self.indices:
            return []
            
        idx = self.indices[movie_id]
        
        # Get pairwise similarity scores
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        
        # Sort by similarity score descending
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top_n similar movies (skip the movie itself)
        sim_scores = [score for score in sim_scores if score[0] != idx][:top_n]
        
        movie_indices = [i[0] for i in sim_scores]
        scores = [i[1] for i in sim_scores]
        
        rec_movies = self.movies.iloc[movie_indices].copy()
        rec_movies['similarity_score'] = scores
        return rec_movies.to_dict('records')
