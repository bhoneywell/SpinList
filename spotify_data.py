"""
spotify_data.py
Logic for pulling album data from Spotify (access token, playlist tracks, etc).
"""
import requests
import streamlit as st
import time

CLIENT_ID = st.secrets["spotify"]["client_id"]
CLIENT_SECRET = st.secrets["spotify"]["client_secret"]
API_KEY = st.secrets["lastfm"]["api_key"]
PLAYLIST_IDS = ['4Bop6Q5jk57ULKkcbC5i8b','7Lo6reW7mdip1PPmxNuxe7']
TOKEN_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1'

def get_access_token(client_id, client_secret):
    response = requests.post(
        TOKEN_URL,
        data={'grant_type': 'client_credentials'},
        auth=(client_id, client_secret)
    )
    response.raise_for_status()
    return response.json()['access_token']

def get_playlist_tracks(playlist_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    albums = {}
    url = f'{BASE_URL}/playlists/{playlist_id}/tracks'
    params = {'limit': 100, 'offset': 0}
    try:
        while url:
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code != 200:
                st.error(f"Error fetching playlist {playlist_id}: {resp.status_code} {resp.reason}\n{resp.text}")
                return []
            data = resp.json()
            for item in data['items']:
                track = item.get('track')
                if track and track.get('album'):
                    album = track['album']
                    album_id = album['id']
                    image_url = album['images'][0]['url'] if album.get('images') and len(album['images']) > 0 else None
                    album_type = album.get('album_type', 'unknown')
                    if album_id not in albums:
                        albums[album_id] = {
                            'name': album['name'],
                            'artists': [artist['name'] for artist in album['artists']],
                            'release_date': album['release_date'],
                            'total_tracks': album['total_tracks'],
                            'external_url': album['external_urls']['spotify'],
                            'image_url': image_url,
                            'album_type': album_type
                        }
            url = data['next']
            params = None  # Only needed for the first request
    except requests.exceptions.RequestException as e:
        st.error(f"Exception fetching playlist {playlist_id}: {e}")
        return []
    return list(albums.values())

def fetch_albums_2025_from_playlists():
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    all_albums = {}
    for pid in PLAYLIST_IDS:
        albums = get_playlist_tracks(pid, access_token)
        for album in albums:
            album_id = album['external_url'].split('/')[-1]
            if album_id not in all_albums:
                all_albums[album_id] = album
    albums_2025 = [album for album in all_albums.values() if album['release_date'].startswith('2025')]
    return albums_2025

def get_album_popularity(albums, access_token):
    """
    Given a list of album dicts (with 'external_url' containing the Spotify album ID), fetch popularity for each album from Spotify.
    """
    headers = {'Authorization': f'Bearer {access_token}'}
    results = []
    for album in albums:
        album_url = album.get('external_url', '')
        album_id = album_url.split('/')[-1] if album_url else None
        if not album_id:
            album['popularity'] = None
            results.append(album)
            continue
        try:
            resp = requests.get(f'https://api.spotify.com/v1/albums/{album_id}', headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                popularity = data.get('popularity')
                album['popularity'] = popularity
            else:
                album['popularity'] = None
        except Exception:
            album['popularity'] = None
        results.append(album)
    return results

def get_lastfm_album_stats(albums):
    """
    Given a list of album dicts (with 'name' and 'artists'), fetch listeners and playcount from the Last.fm API.
    Always uses the API_KEY variable for the Last.fm API key.
    Adds 'lastfm_listeners' and 'lastfm_playcount' to each album dict.
    """
    base_url = 'http://ws.audioscrobbler.com/2.0/'
    for album in albums:
        name = album.get('name')
        artist = album['artists'][0] if album.get('artists') else None
        params = {
            'method': 'album.getinfo',
            'api_key': API_KEY,
            'artist': artist,
            'album': name,
            'format': 'json'
        }
        try:
            resp = requests.get(base_url, params=params)
            if resp.status_code == 200:
                data = resp.json().get('album', {})
                album['lastfm_listeners'] = int(data.get('listeners')) if data.get('listeners') else None
                album['lastfm_playcount'] = int(data.get('playcount')) if data.get('playcount') else None
            else:
                album['lastfm_listeners'] = None
                album['lastfm_playcount'] = None
        except Exception:
            album['lastfm_listeners'] = None
            album['lastfm_playcount'] = None
        time.sleep(0.25)  # Be gentle to the API
    return albums

