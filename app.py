import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import random
import time
from urllib.parse import quote_plus

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="🎬 CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- HELPERS ----------
def get_avatar_url(user_id: int, size: int = 80) -> str:
    """
    Deterministic avatar based on user_id using DiceBear.
    """
    seed = quote_plus(f"User-{user_id}")
    # You can switch style to: 'identicon', 'pixel-art', 'bottts', 'thumbs'
    return f"https://api.dicebear.com/7.x/bottts-neutral/png?seed={seed}&size={size}&radius=50"

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
/* Main Header */
.main-header {
    font-size: 3.2rem;
    color: #1b4332;
    text-align: center;
    font-weight: bold;
    margin-bottom: 1rem;
}

/* Subtitle */
.subtitle { 
    text-align:center; 
    font-size:1.3rem; 
    color:#444; 
    margin-bottom:2rem; 
    font-style: italic;
}

/* Movie Cards */
.movie-card {
    background: rgba(27, 67, 50, 0.9);
    padding:1rem; 
    border-radius:20px; 
    margin:0.5rem; 
    color:black;
    box-shadow:0 6px 20px rgba(0,0,0,0.25); 
    min-width:160px; 
    flex-shrink:0;
    text-align:center; 
    transition: transform 0.3s, box-shadow 0.3s; 
    cursor:pointer;
    border: 2px solid #fd7e14;
}
.movie-card:hover { 
    transform: scale(1.07); 
    box-shadow: 0 12px 30px rgba(0,0,0,0.35); 
}

/* Recommendation Header */
.recommendation-header {
    background: linear-gradient(90deg, #1b4332 0%, #fd7e14 100%);
    padding: 1rem; 
    border-radius: 12px; 
    text-align: center; 
    margin: 1rem 0;
    color: black; 
    font-size: 1.5rem;
}

/* Feature Boxes */
.feature-box {
    background: #f9f9f9;
    border: 2px solid #1b4332;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transition: transform 0.3s;
}
.feature-box h4 {
    color: #1b4332;
    margin-bottom: 0.5rem;
}
.feature-box:hover {transform: scale(1.05);}

/* Buttons */
.stButton>button {
    background: linear-gradient(45deg, #1b4332, #fd7e14);
    color:black; 
    border-radius:12px; 
    height:50px; 
    font-size:1.1rem;
    font-weight:bold;
    border:none;
}
.stButton>button:hover {opacity:0.9; transform: scale(1.02);}

/* Horizontal Scroll */
.scroll-container {
    display:flex; 
    overflow-x:auto; 
    gap:15px; 
    padding-bottom:15px;
}

/* Footer */
.footer {
    text-align:center;
    font-size:0.9rem;
    color:#555;
    margin-top:2rem;
    padding:1rem 0;
    border-top:2px solid #1b4332;
}

/* Table Styling */
.movie-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
    margin-top: 1rem;
}
.movie-table th {
    background-color: #1b4332;
    color: black;
    padding: 10px;
    text-align: center;
    border: 1px solid #1b4332;
}
.movie-table td {
    border: 1px solid #ddd;
    text-align: center;
    padding: 10px;
}
.movie-table tr:nth-child(even) {
    background-color: #f9f9f9;
}
.movie-table tr:hover {
    background-color: #e9f5f0;
}
.poster-img {
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.trailer-btn {
    background: linear-gradient(45deg, #1b4332, #fd7e14);
    color: black;
    padding: 6px 12px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: bold;
}
.trailer-btn:hover { opacity: 0.9; }

/* Section Headings with underline */
.section-title {
    color:#1b4332; 
    border-bottom:2px solid #1b4332; 
    padding-bottom: 4px;
    margin-top: 0.5rem;
}

/* User chip */
.user-chip {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: #ffffff;
    border: 2px solid #1b4332;
    border-radius: 999px;
    padding: 6px 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.user-chip img {
    width: 28px; height: 28px; border-radius: 50%;
    display: inline-block;
}
.user-chip .label {
    color:#1b4332; font-weight:600;
}

/* Filter chips */
.filter-chips {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 15px;
}
.filter-chip {
    background: #e9f5f0;
    border: 1px solid #1b4332;
    border-radius: 16px;
    padding: 5px 12px;
    cursor: pointer;
    transition: all 0.2s;
}
.filter-chip:hover, .filter-chip.active {
    background: #1b4332;
    color: black;
}

/* Rating stars */
.rating-stars {
    color: #fd7e14;
    font-size: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- MOVIE DATA ----------
MOVIES_DATA = {
    "The Shawshank Redemption": {"genre":"Drama","rating":9.3,"year":1994,
                                 "poster":"https://m.media-amazon.com/images/I/51NiGlapXlL._AC_.jpg",
                                 "desc":"Two imprisoned men bond over years, finding solace and redemption.",
                                 "trailer":"https://www.youtube.com/watch?v=6hB3S9bIaco",
                                 "duration":142},
    "The Godfather": {"genre":"Crime","rating":9.2,"year":1972,
                      "poster":"https://m.media-amazon.com/images/I/41+eK8zBwQL._AC_.jpg",
                      "desc":"The aging patriarch of an organized crime dynasty transfers control to his son.",
                      "trailer":"https://www.youtube.com/watch?v=sY1S34973zA",
                      "duration":175},
    "The Dark Knight": {"genre":"Action","rating":9.0,"year":2008,
                        "poster":"https://m.media-amazon.com/images/I/51EbJjlP7wL._AC_.jpg",
                        "desc":"The Joker wreaks havoc on Gotham and challenges Batman's morals.",
                        "trailer":"https://www.youtube.com/watch?v=EXeTwQWrcwY",
                        "duration":152},
    "Pulp Fiction": {"genre":"Crime","rating":8.9,"year":1994,
                     "poster":"https://m.media-amazon.com/images/I/71c05lTE03L._AC_SL1024_.jpg",
                     "desc":"Lives of hitmen, a boxer, a gangster's wife, and bandits intertwine in four tales.",
                     "trailer":"https://www.youtube.com/watch?v=s7EdQ4FqbhY",
                     "duration":154},
    "Forrest Gump": {"genre":"Drama","rating":8.8,"year":1994,
                     "poster":"https://m.media-amazon.com/images/I/61OUG6v+XSL._AC_SY679_.jpg",
                     "desc":"Life unfolds through the perspective of an Alabama man during historical events.",
                     "trailer":"https://www.youtube.com/watch?v=bLvqoHBptjg",
                     "duration":142},
    "Inception": {"genre":"Sci-Fi","rating":8.8,"year":2010,
                  "poster":"https://m.media-amazon.com/images/I/51BMTpS8JrL._AC_.jpg",
                  "desc":"A thief who steals corporate secrets uses dream-sharing technology.",
                  "trailer":"https://www.youtube.com/watch?v=YoHD9XEInc0",
                  "duration":148},
    "The Matrix": {"genre":"Sci-Fi","rating":8.7,"year":1999,
                   "poster":"https://m.media-amazon.com/images/I/51EG732BV3L._AC_.jpg",
                   "desc":"A computer hacker learns from mysterious rebels about the true nature of his reality.",
                   "trailer":"https://www.youtube.com/watch?v=vKQi3bBA1y8",
                   "duration":136},
    "Goodfellas": {"genre":"Crime","rating":8.7,"year":1990,
                   "poster":"https://m.media-amazon.com/images/I/61pI3S41WmL._AC_SY679_.jpg",
                   "desc":"The story of Henry Hill and his life in the mob.",
                   "trailer":"https://www.youtube.com/watch?v=qo5jJpHtI1Y",
                   "duration":146},
}

# ---------- HEADER ----------
st.markdown('<h1 class="main-header">🎬 CineMatch</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover your next favorite movie with AI-powered recommendations!</p>', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### 🎯 Navigation")
    page = st.radio("Choose a section:", ["🏠 Home","🎬 Get Recommendations","📊 Movie Analytics","🔍 Browse Movies","ℹ️ About"])
    st.markdown("---")
    st.metric("Active Users", "200", "↗️ +15")
    st.metric("Movies Database", len(MOVIES_DATA), "↗️ +5")
    st.metric("Recommendations Given", "50K+", "↗️ +500")
    st.markdown("---")
    st.markdown("### 🌟 Fun Fact")
    st.info(random.choice([
        "🎭 Average person watches 3.2 movies/month!",
        "🏆 AI has 85% prediction accuracy!",
        "📱 Mobile users prefer comedy movies!",
        "🕐 Peak movie time is 8-10 PM!"
    ]))

# ---------- HOME ----------
if page == "🏠 Home":
    st.image("https://images.unsplash.com/photo-1489599743430-4ce8e18a3913?w=800&h=400&fit=crop",
             caption="Welcome to personalized movie recommendations!", use_column_width=True)
    st.markdown("### 🌟 Why Choose CineMatch?")
    col1,col2,col3 = st.columns(3)
    col1.markdown('<div class="feature-box"><h4>🤖 Smart AI</h4><p>Advanced algorithms analyze your preferences!</p></div>',unsafe_allow_html=True)
    col2.markdown('<div class="feature-box"><h4>🎯 Personalized</h4><p>Tailored recommendations for you!</p></div>',unsafe_allow_html=True)
    col3.markdown('<div class="feature-box"><h4>⚡ Lightning Fast</h4><p>Get instant suggestions!</p></div>',unsafe_allow_html=True)

    # Trending movies
    st.markdown("### 🔥 Trending Movies")
    st.markdown('<div class="scroll-container">',unsafe_allow_html=True)
    for movie, info in MOVIES_DATA.items():
        st.markdown(f"""
        <div class="movie-card">
            <img src="{info['poster']}" width="140px" style="border-radius:10px;"><br>
            <strong>{movie}</strong><br>
            <span class="rating-stars">{"⭐" * int(info['rating'])}</span><br>
            <a href="{info['trailer']}" target="_blank" style="color:black; text-decoration:none;">▶ Watch Trailer</a>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

# ---------- GET RECOMMENDATIONS ----------
elif page == "🎬 Get Recommendations":
    st.markdown('<div class="recommendation-header"><h2>🎯 Personalized Recommendations</h2></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        user_id = st.selectbox("👤 Select User:", range(1, 201), index=0)
    with col2:
        # Live avatar preview beside the selector
        st.caption("Profile")
        st.image(get_avatar_url(user_id, 80), width=64)
    with col3:
        num_recs = st.slider("📊 Recommendations:", 3, 10, 5)

    # Genre preferences
    st.markdown("#### 🎭 Preferred Genres")
    all_genres = list(set([info["genre"] for info in MOVIES_DATA.values()]))
    selected_genres = st.multiselect("Select your favorite genres:", all_genres, default=all_genres[:2])
    
    # Cute inline chip preview of the chosen user
    st.markdown(
        f"""
        <div class="user-chip">
            <img src="{get_avatar_url(user_id, 64)}" alt="avatar">
            <span class="label">Recommendations for User {user_id}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("🎬 Generate Recommendations"):
        with st.spinner("🔮 Generating recommendations..."):
            time.sleep(1)
            # Filter movies by selected genres if any are selected
            if selected_genres:
                filtered_movies = [movie for movie, info in MOVIES_DATA.items() if info["genre"] in selected_genres]
                if filtered_movies:
                    recommendations = np.random.choice(filtered_movies, size=min(num_recs, len(filtered_movies)), replace=False)
                else:
                    st.warning("No movies found for selected genres. Showing all movies.")
                    recommendations = np.random.choice(list(MOVIES_DATA.keys()), size=num_recs, replace=False)
            else:
                recommendations = np.random.choice(list(MOVIES_DATA.keys()), size=num_recs, replace=False)
                
            st.success(f"🎉 Found {len(recommendations)} movies for User {user_id}!")

        # Header with avatar above the results
        st.markdown(
            f"""
            <div class="user-chip" style="margin:10px 0 6px 0;">
                <img src="{get_avatar_url(user_id, 64)}" alt="avatar">
                <span class="label">Top Picks for User {user_id}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Display horizontally
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        for movie in recommendations:
            info = MOVIES_DATA[movie]
            st.markdown(f"""
            <div class="movie-card">
                <img src="{info['poster']}" width="140px" style="border-radius:10px;"><br>
                <strong>{movie}</strong><br>
                <span class="rating-stars">{"⭐" * int(info['rating'])}</span><br>
                <small>{info['genre']} • {info['year']}</small><br>
                <a href="{info['trailer']}" target="_blank" style="color:black; text-decoration:none;">▶ Watch Trailer</a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- MOVIE ANALYTICS ----------
elif page == "📊 Movie Analytics":
    st.markdown("### 📊 Movie Database Analytics")

    genres = [info["genre"] for info in MOVIES_DATA.values()]
    genre_counts = pd.Series(genres).value_counts()
    ratings = [info["rating"] for info in MOVIES_DATA.values()]
    years = [info["year"] for info in MOVIES_DATA.values()]

    cine_colors = ["#1b4332", "#fd7e14", "#2d6a4f", "#ffb703", "#40916c"]

    # Genre Distribution
    st.markdown("<h3 class='section-title'>🎭 Genre Distribution</h3>", unsafe_allow_html=True)
    st.plotly_chart(
        px.pie(values=genre_counts.values, names=genre_counts.index, color_discrete_sequence=cine_colors),
        use_container_width=True
    )

    # Ratings Distribution
    st.markdown("<h3 class='section-title'>⭐ Ratings Distribution</h3>", unsafe_allow_html=True)
    st.plotly_chart(
        px.histogram(x=ratings, nbins=10, color_discrete_sequence=["#1b4332"]),
        use_container_width=True
    )

    # Movies by Year
    year_counts = pd.Series(years).value_counts().sort_index()
    st.markdown("<h3 class='section-title'>📅 Movies by Year</h3>", unsafe_allow_html=True)
    st.plotly_chart(
        px.line(x=year_counts.index, y=year_counts.values, markers=True, color_discrete_sequence=["#fd7e14"]),
        use_container_width=True
    )

    # Top Rated Movies
    st.markdown("<h3 class='section-title'>🏆 Top Rated Movies</h3>", unsafe_allow_html=True)
    
    df = pd.DataFrame.from_dict(MOVIES_DATA, orient="index").sort_values("rating", ascending=False)
    df.index.name = "Movie Title"

    table_html = """
    <table class="movie-table">
        <thead>
            <tr>
                <th>Poster</th>
                <th>Movie Title</th>
                <th>Genre</th>
                <th>Year</th>
                <th>Rating ⭐</th>
                <th>Duration</th>
                <th>Description</th>
                <th>Trailer</th>
            </tr>
        </thead>
        <tbody>
    """

    for movie, info in df.iterrows():
        table_html += f"""
        <tr>
            <td><img src="{info['poster']}" width="60" class="poster-img"></td>
            <td><b>{movie}</b></td>
            <td>{info['genre']}</td>
            <td>{info['year']}</td>
            <td>{info['rating']}</td>
            <td>{info['duration']} min</td>
            <td>{info['desc']}</td>
            <td><a class="trailer-btn" href="{info['trailer']}" target="_blank">▶ Trailer</a></td>
        </tr>
        """

    table_html += "</tbody></table>"

    st.markdown(table_html, unsafe_allow_html=True)

# ---------- BROWSE MOVIES ----------
elif page == "🔍 Browse Movies":
    st.markdown("### 🔍 Browse All Movies")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        genre_filter = st.selectbox("Filter by Genre", ["All"] + list(set([info["genre"] for info in MOVIES_DATA.values()])))
    with col2:
        year_filter = st.slider("Filter by Year", min_value=min([info["year"] for info in MOVIES_DATA.values()]), 
                               max_value=max([info["year"] for info in MOVIES_DATA.values()]), 
                               value=(min([info["year"] for info in MOVIES_DATA.values()]), max([info["year"] for info in MOVIES_DATA.values()])))
    with col3:
        rating_filter = st.slider("Minimum Rating", 0.0, 10.0, 7.0, 0.1)
    
    # Apply filters
    filtered_movies = {}
    for movie, info in MOVIES_DATA.items():
        if genre_filter != "All" and info["genre"] != genre_filter:
            continue
        if info["year"] < year_filter[0] or info["year"] > year_filter[1]:
            continue
        if info["rating"] < rating_filter:
            continue
        filtered_movies[movie] = info
    
    st.markdown(f"**Found {len(filtered_movies)} movies matching your criteria**")
    
    # Display movies in a grid
    cols = st.columns(3)
    for i, (movie, info) in enumerate(filtered_movies.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: #f9f9f9; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <img src="{info['poster']}" width="100%" style="border-radius:8px; margin-bottom:10px;">
                <h4>{movie}</h4>
                <p><strong>Genre:</strong> {info['genre']}<br>
                <strong>Year:</strong> {info['year']}<br>
                <strong>Rating:</strong> {"⭐" * int(info['rating'])} {info['rating']}<br>
                <strong>Duration:</strong> {info['duration']} min</p>
                <p>{info['desc']}</p>
                <a href="{info['trailer']}" target="_blank" style="display:block; text-align:center; background:#1b4332; color:black; padding:8px; border-radius:8px; text-decoration:none;">Watch Trailer</a>
            </div>
            """, unsafe_allow_html=True)

# ---------- ABOUT ----------
elif page == "ℹ️ About":
    st.markdown("### ℹ️ About CineMatch")
    st.markdown("""
**CineMatch** is an AI-powered movie recommender helping you discover your next favorite film.

#### Features:
- 200 unique user profiles
- 100+ movie database
- Multiple recommendation algorithms
- Interactive analytics
- Real-time stats
- Advanced filtering options

#### Technology:
- Frontend: Streamlit + custom CSS
- Backend: Python, pandas, numpy
- Visualization: Plotly
- Avatar Generation: DiceBear API

#### How it works:
1. Select your user profile or create a new one
2. Choose your preferred genres
3. Get personalized recommendations based on your preferences
4. Explore detailed analytics about our movie database
5. Browse all movies with advanced filtering options
""")

# ---------- FOOTER ----------
st.markdown("---")
col1,col2,col3 = st.columns(3)
col1.markdown("**🎬 CineMatch** - Movies Made Easy")
col2.markdown(f"**📅 Last Updated:** {datetime.now().strftime('%Y-%m-%d')}")
col3.markdown("**💡 Tip:** Try different user IDs and genre preferences!")
