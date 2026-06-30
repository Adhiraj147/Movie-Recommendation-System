document.addEventListener('DOMContentLoaded', () => {
    // Search Autocomplete
    const searchInput = document.getElementById('searchInput');
    const searchSuggestions = document.getElementById('searchSuggestions');
    
    let debounceTimer;
    
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                searchSuggestions.style.display = 'none';
                return;
            }
            
            debounceTimer = setTimeout(async () => {
                try {
                    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                    const movies = await response.json();
                    
                    searchSuggestions.innerHTML = '';
                    if (movies.length > 0) {
                        movies.forEach(movie => {
                            const div = document.createElement('div');
                            div.className = 'suggestion-item';
                            div.innerHTML = `<strong>${movie.title}</strong> <span style="font-size: 0.8em; color: var(--text-secondary); float: right;">${movie.year || ''}</span>`;
                            div.addEventListener('click', () => {
                                window.location.href = `/movie/${movie.movieId}`;
                            });
                            searchSuggestions.appendChild(div);
                        });
                        searchSuggestions.style.display = 'flex';
                    } else {
                        searchSuggestions.innerHTML = '<div class="suggestion-item">No movies found.</div>';
                        searchSuggestions.style.display = 'flex';
                    }
                } catch (err) {
                    console.error("Search error", err);
                }
            }, 300);
        });
        
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !e.target.classList.contains('search-icon')) {
                searchSuggestions.style.display = 'none';
                searchInput.classList.remove('active');
            }
        });
    }

    // Navbar Scroll Effect
    window.addEventListener('scroll', () => {
        const nav = document.getElementById('navbar');
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });

    // Optional: Carousel horizontal scrolling with mousewheel
    const carousels = document.querySelectorAll('.carousel');
    carousels.forEach(carousel => {
        carousel.addEventListener('wheel', (e) => {
            if (e.deltaY !== 0) {
                e.preventDefault();
                carousel.scrollLeft += e.deltaY;
            }
        });
    });
});
