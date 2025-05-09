import streamlit as st
import pandas as pd
import pickle
import requests

# Load data
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# TMDB API Key
API_KEY = '8265bd1679663a7ea12ac168da84d2e8'

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

def fetch_poster(movie_id):
    details = fetch_movie_details(movie_id)
    return 'https://image.tmdb.org/t/p/w500/' + details.get('poster_path', '')

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        details = fetch_movie_details(movie_id)
        recommended.append({
            'title': details.get('title', 'Unknown'),
            'poster': 'https://image.tmdb.org/t/p/w500/' + details.get('poster_path', ''),
            'overview': details.get('overview', 'No overview available.'),
            'release_date': details.get('release_date', 'Unknown'),
            'rating': details.get('vote_average', 'N/A'),
            'genres': ", ".join([genre['name'] for genre in details.get('genres', [])])
        })
    return recommended

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommendation System')

selected_movie_name = st.selectbox("Select a movie to get recommendations:", movies['title'].values)

if st.button("Recommend"):
    recommendations = recommend(selected_movie_name)
    st.subheader("Top 5 Recommendations:")

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        movie = recommendations[idx]
        with col:
            if st.button(movie['title'], key=movie['title']):
                st.session_state['selected_movie'] = movie
            st.image(movie['poster'], use_column_width=True)
            st.caption(f"Rating: ⭐ {movie['rating']}")

# Show detailed movie info if clicked
if 'selected_movie' in st.session_state:
    movie = st.session_state['selected_movie']
    st.markdown("---")
    st.header(f"Details: {movie['title']}")
    st.image(movie['poster'], width=300)
    st.write(f"**Overview:** {movie['overview']}")
    st.write(f"**Release Date:** {movie['release_date']}")
    st.write(f"**Rating:** ⭐ {movie['rating']}")
    st.write(f"**Genres:** {movie['genres']}")
