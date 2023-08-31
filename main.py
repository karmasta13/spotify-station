from dotenv import load_dotenv
import os 
import base64
import requests
import json
import streamlit as st
from PIL import Image

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    
    query_url = url + query
    
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        st.error("No artist found with this name.")
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=AU"
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def get_artist_details(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_top_albums(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?limit=5"
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def main():
    st.title("Discover Spotify Artist Info, Top Tracks, and Albums")
    st.markdown("---")
    st.write("🎵 Enter an artist's name to explore their top tracks, albums, and info! 🎵")
    artist_name = st.text_input("Enter artist name:")
    if artist_name:
        st.markdown("---")
        token = get_token()
        result = search_for_artist(token, artist_name)
        if result:
            artist_id = result["id"]
            artist_details = get_artist_details(token, artist_id)
            st.subheader(f"🎤 {artist_details['name']} 🎤")
            st.image(artist_details['images'][0]['url'], caption='Artist Image', use_column_width=True)
            st.write(f"📊 Popularity: {artist_details['popularity']} / 100")
            st.write(f"👥 Followers: {artist_details['followers']['total']}")
            
            st.markdown("---")
            songs = get_songs_by_artist(token, artist_id)
            st.subheader(f"🎶 Top tracks by {artist_name} 🎶")
            for idx, song in enumerate(songs):
                st.write(f"{idx + 1}. {song['name']} - Popularity: {song['popularity']} / 100")
            
            st.markdown("---")
            albums = get_top_albums(token, artist_id)
            st.subheader(f"📀 Top albums by {artist_name} 📀")
            for idx, album in enumerate(albums):
                st.write(f"{idx + 1}. {album['name']} - Release Date: {album['release_date']}")

if __name__ == "__main__":
    main()
