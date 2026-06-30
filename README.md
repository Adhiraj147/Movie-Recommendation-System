# 🎬 Movie Recommendation System

A complete, production-ready Movie Recommendation System featuring Content-Based and Collaborative Filtering algorithms. Built with a premium, responsive UI and a highly optimized Python FastAPI backend.

![Project Banner Placeholder](https://via.placeholder.com/1200x400.png?text=Movie+Recommendation+System)

## 🌟 Features
- **Intelligent Recommendations**: Get personalized movie suggestions based on advanced ML algorithms.
- **Hybrid Recommendation Engine**: Combines Item-Based CF (KNN), SVD Matrix Factorization, and Content-Based Filtering (TF-IDF Vectorization & Cosine Similarity) for high accuracy.
- **Modern UI/UX**: Cinematic Netflix-inspired interface with dark mode, glassmorphism, and smooth micro-animations.
- **Real-Time Search**: Autocomplete search for instant movie lookups.
- **Interactive Rating System**: Rate movies to influence your collaborative filtering recommendations.
- **High Performance**: Models are pre-trained and serialized using `pickle` for lightning-fast API responses.

## 🛠️ Tech Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy (SQLite)
- **Machine Learning**: Scikit-Learn, Pandas, NumPy, SciPy
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript, Jinja2 Templates
- **Deployment**: Docker, Uvicorn

## 📂 Project Architecture

```
movie-recommendation-system/
│
├── app.py                     # FastAPI entry point
├── preprocessing.py           # Dataset download and cleaning
├── content_filter.py          # TF-IDF & Cosine Similarity logic
├── collaborative_filter.py    # KNN & SVD logic
├── recommendation_engine.py   # Hybrid model facade
├── train_model.py             # Script to train & save models
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Python dependencies
│
├── dataset/                   # Downloaded MovieLens dataset
├── models/                    # Serialized .pkl ML models
├── utils/
│   └── database.py            # SQLite setup & models
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   └── movie.html
│
└── static/                    # CSS, JS, and Assets
    ├── css/style.css
    └── js/main.js
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation
Clone the repository:
```bash
git clone https://github.com/yourusername/movie-recommendation-system.git
cd movie-recommendation-system
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Training the Models
Before running the server, you need to download the dataset and train the ML models:
```bash
python train_model.py
```
*This will automatically download the MovieLens ml-latest-small dataset (~1MB) and create an `engine.pkl` in the `models/` folder.*

### 4. Running the Server
Start the FastAPI server:
```bash
uvicorn app:app --reload
```
Navigate to `http://127.0.0.0:8000` in your browser.

## 🔌 API Endpoints
- `GET /`: Returns the home page with trending movies and genres.
- `GET /movie/{id}`: Returns movie details and personalized recommendations.
- `GET /api/search?q={query}`: Returns search suggestions.
- `POST /api/rate`: Save a user's movie rating.
- `POST /api/favorite`: Add/remove a movie from favorites.
- `GET /health`: Health check endpoint.

## 🐳 Docker Deployment
To deploy using Docker (suitable for Render, Railway, etc.):
```bash
docker build -t movie-recommender .
docker run -p 8000:8000 movie-recommender
```

## 🔮 Future Improvements
- Implement User Authentication (JWT).
- Add Deep Learning Recommenders (Neural Collaborative Filtering).
- Integrate TMDB API to fetch real movie posters and trailers.
- Setup PostgreSQL for production data persistence.

## 📝 License
This project is licensed under the MIT License.
