import pickle
import os
from preprocessing import load_data
from recommendation_engine import RecommendationEngine

def train_and_save():
    print("Loading data...")
    movies, ratings = load_data()
    
    print("Initializing Recommendation Engine...")
    engine = RecommendationEngine(movies, ratings)
    
    print("Training models...")
    engine.train_all()
    
    print("Saving models to disk...")
    os.makedirs('models', exist_ok=True)
    with open('models/engine.pkl', 'wb') as f:
        pickle.dump(engine, f)
    print("Models saved successfully to models/engine.pkl")

if __name__ == "__main__":
    train_and_save()
