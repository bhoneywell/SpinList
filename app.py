


# --- Begin logic for pulling 2025 albums from playlists ---
import requests
from datetime import datetime
import streamlit as st

CLIENT_ID = '3659c895507648258ca03b9317bed338'
CLIENT_SECRET = 'bb2035910d2d42dd8423631728395619'
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
    status = st.empty()
    for idx, pid in enumerate(PLAYLIST_IDS):
        status.info(f"Pulling albums from playlist {idx+1}/{len(PLAYLIST_IDS)}: {pid}")
        albums = get_playlist_tracks(pid, access_token)
        for album in albums:
            album_id = album['external_url'].split('/')[-1]
            if album_id not in all_albums:
                all_albums[album_id] = album
    status.success("API pull complete!")
    albums_2025 = [album for album in all_albums.values() if album['release_date'].startswith('2025')]
    return albums_2025
# --- End logic ---

def main():
    st.title("2025 Spotify Albums Grid (from Playlists)")
    st.write("Browse 2025 albums pulled from selected Spotify playlists.")

    albums = fetch_albums_2025_from_playlists()

    # Defensive: parse release date
    for album in albums:
        try:
            album["release_date_obj"] = datetime.strptime(album["release_date"], "%Y-%m-%d")
        except:
            try:
                album["release_date_obj"] = datetime.strptime(album["release_date"], "%Y-%m")
            except:
                try:
                    album["release_date_obj"] = datetime.strptime(album["release_date"], "%Y")
                except:
                    album["release_date_obj"] = datetime(2025, 1, 1)

    album_types = sorted({a['album_type'] for a in albums})
    selected_album_type = st.sidebar.selectbox("Filter by album type", ["All"] + album_types)

    sort_by = st.sidebar.selectbox("Sort by", ["Release Date (Newest)", "Release Date (Oldest)", "Album Name"])

    filtered_albums = albums
    if selected_album_type != "All":
        filtered_albums = [a for a in albums if a['album_type'] == selected_album_type]

    if sort_by == "Release Date (Newest)":
        filtered_albums = sorted(filtered_albums, key=lambda a: a["release_date_obj"], reverse=True)
    elif sort_by == "Release Date (Oldest)":
        filtered_albums = sorted(filtered_albums, key=lambda a: a["release_date_obj"])
    elif sort_by == "Album Name":
        filtered_albums = sorted(filtered_albums, key=lambda a: a["name"].lower())

    # Grid view (4 per row)
    for i in range(0, len(filtered_albums), 4):
        cols = st.columns(4)
        for j, album in enumerate(filtered_albums[i:i+4]):
            with cols[j]:
                name = album["name"]
                artists = ", ".join(album["artists"])
                release_date = album["release_date"]
                url = album["external_url"]
                image_url = album.get("image_url")
                album_type = album.get("album_type", "unknown")
                if image_url:
                    st.image(image_url, width=180)
                st.markdown(f"**[{name}]({url})**")
                st.markdown(f"*{artists}*")
                st.markdown(f"Released: {release_date}")
                st.markdown(f"Type: {album_type}")

if __name__ == '__main__':
    main()
