import os
import pickle
import streamlit as st
import requests

st.set_page_config(
    page_title="CineMatch | Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MOVIE_PATH = os.path.join(BASE_DIR, "model", "movie_list.pkl")
SIMILARITY_PATH = os.path.join(BASE_DIR, "model", "similarity.pkl")

try:
    with open(MOVIE_PATH, "rb") as file:
        movies = pickle.load(file)

    with open(SIMILARITY_PATH, "rb") as file:
        similarity = pickle.load(file)

except FileNotFoundError as e:
    st.error(f"Model file not found: {e.filename}")
    st.info(
        "Make sure movie_list.pkl and similarity.pkl are inside the model folder."
    )
    st.stop()


def fetch_poster(movie_id):
    API_KEY = st.secrets["TMDB_API_KEY"]

    url = (
    f"https://api.themoviedb.org/3/movie/{movie_id}"
    f"?api_key={API_KEY}"
    "&language=en-US"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"

    except requests.RequestException:
        pass

    return None


def recommend(movie):
    index = movies[movies["title"] == movie].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommendations = []

    for i in distances[1:6]:
        movie_index = i[0]
        similarity_score = i[1]

        movie_id = movies.iloc[movie_index]["movie_id"]
        movie_title = movies.iloc[movie_index]["title"]

        poster = fetch_poster(movie_id)

        recommendations.append({
            "title": movie_title,
            "poster": poster,
            "movie_id": movie_id,
            "similarity": similarity_score
        })

    return recommendations


st.markdown("""
<style>

.stApp {
    background: #080b14;
}

.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    margin-top: 10px;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #9ca3af;
    font-size: 18px;
    margin-bottom: 35px;
}

.section-title {
    font-size: 28px;
    font-weight: 700;
    margin-top: 35px;
    margin-bottom: 20px;
}

.movie-title {
    font-size: 17px;
    font-weight: 700;
    margin-top: 12px;
    min-height: 45px;
}

.movie-info {
    color: #9ca3af;
    font-size: 14px;
    margin-top: 5px;
}

.similarity {
    color: #60a5fa;
    font-weight: 700;
}

.link-button {
    display: inline-block;
    padding: 8px 12px;
    margin-top: 10px;
    border-radius: 8px;
    background: #2563eb;
    color: white !important;
    text-decoration: none;
    font-size: 13px;
    font-weight: 600;
}

.link-button:hover {
    background: #1d4ed8;
}

</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="main-title">🎬 CineMatch</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Discover movies similar to the ones you love.'
    '</div>',
    unsafe_allow_html=True
)


movie_list = movies["title"].values

selected_movie = st.selectbox(
    "🔎 Select a movie",
    movie_list
)


if st.button(
    "✨ Show Recommendations",
    use_container_width=True
):

    recommended_movies = recommend(selected_movie)

    st.markdown(
        '<div class="section-title">🍿 Recommended Movies</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(5)

    for i, movie in enumerate(recommended_movies):

        with cols[i]:

            if movie["poster"]:
                st.image(
                    movie["poster"],
                    use_container_width=True
                )
            else:
                st.info("Poster unavailable")

            st.markdown(
                f"""
                <div class="movie-title">
                    {movie["title"]}
                </div>

                <div class="movie-info">
                    🎯 Similarity:
                    <span class="similarity">
                        {movie["similarity"] * 100:.1f}%
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            movie_link = (
                "https://www.themoviedb.org/movie/"
                + str(movie["movie_id"])
            )

            st.markdown(
                f"""
                <a href="{movie_link}"
                   target="_blank"
                   class="link-button">
                    🔗 View on TMDB
                </a>
                """,
                unsafe_allow_html=True
            )