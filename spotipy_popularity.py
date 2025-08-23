"""
Script to pull album data returned from spotify_data.py and derive a composite score
"""

def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val) if max_val != min_val else 0

from datetime import datetime


def compute_album_score(popularity, listeners, playcount,
                        min_listeners, max_listeners,
                        min_playcount, max_playcount,
                        days_since_release=None):
    norm_popularity = popularity / 100 if popularity is not None else 0  # Already 0–100 from Spotify
    # If days_since_release is available and > 0, normalize listeners and playcount per day
    if listeners is not None and days_since_release and days_since_release > 0:
        listeners_per_day = listeners / days_since_release
    else:
        listeners_per_day = listeners
    if playcount is not None and days_since_release and days_since_release > 0:
        playcount_per_day = playcount / days_since_release
    else:
        playcount_per_day = playcount
    norm_listeners = normalize(listeners_per_day, min_listeners, max_listeners) if listeners_per_day is not None else 0
    norm_playcount = normalize(playcount_per_day, min_playcount, max_playcount) if playcount_per_day is not None else 0
    score = (
        0.5 * norm_popularity +
        0.3 * norm_listeners +
        0.2 * norm_playcount
    )
    return round(score * 100, 2)  # Optional: scale to 0–100

# Helper to compute days since release for a row
def get_days_since_release(row):
    today = datetime.today()
    release_date_str = row.get("release_date")
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            release_date = datetime.strptime(release_date_str, fmt)
            return max((today - release_date).days, 1)
        except Exception:
            continue
    return 1

# Add composite score to DataFrame
def add_composite_score(df):
    df['days_since_release'] = df.apply(get_days_since_release, axis=1)
    df['listeners_per_day'] = df.apply(lambda row: row['lastfm_listeners'] / row['days_since_release'] if row['lastfm_listeners'] is not None else None, axis=1)
    df['playcount_per_day'] = df.apply(lambda row: row['lastfm_playcount'] / row['days_since_release'] if row['lastfm_playcount'] is not None else None, axis=1)
    min_listeners = df['listeners_per_day'].min(skipna=True)
    max_listeners = df['listeners_per_day'].max(skipna=True)
    min_playcount = df['playcount_per_day'].min(skipna=True)
    max_playcount = df['playcount_per_day'].max(skipna=True)
    df['composite_score'] = df.apply(
        lambda row: compute_album_score(
            row.get('popularity'),
            row.get('lastfm_listeners'),
            row.get('lastfm_playcount'),
            min_listeners, max_listeners,
            min_playcount, max_playcount,
            row.get('days_since_release')
        ), axis=1)
    return df

import pandas as pd
from spotify_data import fetch_albums_2025_from_playlists, get_access_token, get_album_popularity, get_lastfm_album_stats, CLIENT_ID, CLIENT_SECRET

def get_albums_with_popularity_and_lastfm_df():
    albums = fetch_albums_2025_from_playlists()
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    albums = get_album_popularity(albums, access_token)
    albums = get_lastfm_album_stats(albums)
    df = pd.DataFrame(albums)
    return df

if __name__ == "__main__":
    df = get_albums_with_popularity_and_lastfm_df()
    df = add_composite_score(df)
    print(df.head())
