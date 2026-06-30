import os
import pickle
from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from utils.database import init_db, get_db, User, Rating, Favorite
from utils.tmdb import enhance_movies_list, enhance_movie_data

app = FastAPI(title="Movie Recommendation System")

# Ensure models are loaded
ENGINE_PATH = os.path.join(os.path.dirname(__file__), "models", "engine.pkl")
if not os.path.exists(ENGINE_PATH):
    raise RuntimeError("Models not found. Please run train_model.py first.")

print("Loading pre-trained recommendation engine...")
with open(ENGINE_PATH, 'rb') as f:
    engine = pickle.load(f)
print("Engine loaded successfully.")

# Initialize DB
init_db()

# Static and Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    trending = engine.get_trending(limit=18)
    trending = enhance_movies_list(trending)
    
    genres = set()
    for m in engine.movies['genres']:
        genres.update(m.split())
    genres = sorted([g for g in genres if g]) # Remove empty strings
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "trending": trending,
        "genres": genres
    })

@app.get("/movie/{movie_id}", response_class=HTMLResponse)
async def movie_detail(request: Request, movie_id: int):
    movie = engine.get_movie_details(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie = enhance_movie_data(movie)
    
    recommendations = engine.recommend(movie_id, top_n=12, method='hybrid')
    recommendations = enhance_movies_list(recommendations)
    
    return templates.TemplateResponse("movie.html", {
        "request": request,
        "movie": movie,
        "recommendations": recommendations
    })

@app.get("/api/search")
async def search_movies(q: str = ""):
    if not q:
        return []
    results = engine.search_movies(q, limit=8)
    results = enhance_movies_list(results)
    return results

@app.post("/api/rate")
async def rate_movie(movie_id: int = Form(...), rating: float = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == "demo_user").first()
    if not user:
        user = User(username="demo_user")
        db.add(user)
        db.commit()
        db.refresh(user)
        
    existing = db.query(Rating).filter(Rating.user_id == user.id, Rating.movie_id == movie_id).first()
    if existing:
        existing.rating = rating
    else:
        new_rating = Rating(user_id=user.id, movie_id=movie_id, rating=rating)
        db.add(new_rating)
        
    db.commit()
    return {"message": "Rating saved successfully"}

@app.post("/api/favorite")
async def favorite_movie(movie_id: int = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == "demo_user").first()
    if not user:
        user = User(username="demo_user")
        db.add(user)
        db.commit()
        db.refresh(user)
        
    existing = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.movie_id == movie_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"message": "Removed from favorites", "status": "removed"}
    else:
        new_fav = Favorite(user_id=user.id, movie_id=movie_id)
        db.add(new_fav)
        db.commit()
        return {"message": "Added to favorites", "status": "added"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
