import pandas as pd
from content_filter import ContentBasedRecommender
from collaborative_filter import CollaborativeRecommender

class RecommendationEngine:
    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        self.movies = movies_df
        self.ratings = ratings_df
        self.content_recommender = ContentBasedRecommender(movies_df)
        self.collab_recommender = CollaborativeRecommender(ratings_df, movies_df)
        
    def train_all(self):
        """Train both content and collaborative models."""
        self.content_recommender.train()
        self.collab_recommender.train()
        
    def get_movie_details(self, movie_id: int):
        movie = self.movies[self.movies['movieId'] == movie_id]
        if movie.empty:
            return None
        return movie.iloc[0].to_dict()

    def search_movies(self, query: str, limit: int = 10):
        """Search movies by title."""
        query = query.lower()
        matches = self.movies[self.movies['title'].str.lower().str.contains(query, na=False)]
        return matches.head(limit).to_dict('records')

    def get_trending(self, limit: int = 10):
        """Get trending movies based on rating count and average rating."""
        rating_stats = self.ratings.groupby('movieId').agg(
            rating_count=('rating', 'count'),
            rating_mean=('rating', 'mean')
        ).reset_index()
        
        # Bayesian average or simple heuristic: highly rated and many ratings
        C = rating_stats['rating_mean'].mean()
        m = rating_stats['rating_count'].quantile(0.90)
        
        def weighted_rating(x, m=m, C=C):
            v = x['rating_count']
            R = x['rating_mean']
            return (v/(v+m) * R) + (m/(m+v) * C)
            
        trending = rating_stats[rating_stats['rating_count'] >= m].copy()
        trending['score'] = trending.apply(weighted_rating, axis=1)
        trending = trending.sort_values('score', ascending=False).head(limit)
        
        trending_movies = pd.merge(trending, self.movies, on='movieId')
        return trending_movies.to_dict('records')

    def recommend(self, movie_id: int, top_n: int = 10, method: str = 'hybrid'):
        """Get recommendations using specified method (content, collab_knn, collab_svd, hybrid)."""
        if method == 'content':
            recs = self.content_recommender.get_recommendations(movie_id, top_n)
            for r in recs: r['algorithm'] = 'Content-Based'
            return recs
        elif method == 'collab_knn':
            return self.collab_recommender.get_similar_movies_knn(movie_id, top_n)
        elif method == 'collab_svd':
            return self.collab_recommender.get_similar_movies_svd(movie_id, top_n)
        else:
            # Hybrid: Combine SVD and Content-Based
            content_recs = self.content_recommender.get_recommendations(movie_id, top_n=top_n*2)
            svd_recs = self.collab_recommender.get_similar_movies_svd(movie_id, top_n=top_n*2)
            
            combined = {}
            for rec in content_recs:
                rec['algorithm'] = 'Content-Based'
                combined[rec['movieId']] = rec
                
            for rec in svd_recs:
                if rec['movieId'] in combined:
                    # Boost score if found by both methods
                    combined[rec['movieId']]['similarity_score'] += rec['similarity_score']
                    combined[rec['movieId']]['algorithm'] = 'Hybrid'
                else:
                    combined[rec['movieId']] = rec
                    
            sorted_recs = sorted(combined.values(), key=lambda x: x['similarity_score'], reverse=True)
            return sorted_recs[:top_n]
