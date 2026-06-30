import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p"

def get_movie_images(tmdb_id):
    if not TMDB_API_KEY or not tmdb_id or str(tmdb_id).lower() == 'nan':
        return None
        
    try:
        url = f"{TMDB_BASE_URL}/movie/{int(float(tmdb_id))}?api_key={TMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path')
            backdrop_path = data.get('backdrop_path')
            overview = data.get('overview')
            return {
                'poster_url': f"{TMDB_IMAGE_BASE_URL}/w500{poster_path}" if poster_path else None,
                'backdrop_url': f"{TMDB_IMAGE_BASE_URL}/original{backdrop_path}" if backdrop_path else None,
                'overview': overview
            }
    except Exception as e:
        print(f"Error fetching TMDB images for {tmdb_id}: {e}")
    return None

def enhance_movie_data(movie):
    """Adds TMDB poster, backdrop and overview to movie dict"""
    if not movie:
        return movie
        
    tmdb_data = get_movie_images(movie.get('tmdbId'))
    if tmdb_data:
        movie['poster_url'] = tmdb_data.get('poster_url')
        movie['backdrop_url'] = tmdb_data.get('backdrop_url')
        movie['overview'] = tmdb_data.get('overview')
    return movie

def enhance_movies_list(movies):
    """Adds TMDB data to a list of movies (optimally we should batch, but for now loop)"""
    return [enhance_movie_data(m) for m in movies]
