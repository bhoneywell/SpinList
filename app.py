def rating_bar(score: int, label="Composite Score"):
    # Clamp between 0 and 100
    score = max(0, min(int(score), 100)) if score is not None else 0
    st.markdown(f"""
    <div style="margin-bottom: 10px;">
        <div style="font-size: 14px; color: #ccc; margin-bottom: 4px;">{label}</div>
        <div style="background-color: #333; border-radius: 4px; height: 16px; width: 100%;">
            <div style="
                background-color: #3dbb3d;
                width: {score}%;
                height: 100%;
                border-radius: 4px;
                text-align: right;
                padding-right: 5px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                line-height: 16px;
            ">{score}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)




# --- Begin logic for pulling 2025 albums from playlists ---
from datetime import datetime
import streamlit as st
# Import the DataFrame generator from spotipy_popularity
from spotipy_popularity import get_albums_with_popularity_and_lastfm_df, add_composite_score
# --- End logic ---

def main():
    st.title("2025 Spotify Albums Grid (from Playlists)")
    st.write("Browse 2025 albums pulled from selected Spotify playlists.")


    # Show progress messages for each step
    status = st.empty()
    status.info("Fetching albums from Spotify playlists...")
    df = get_albums_with_popularity_and_lastfm_df()
    status.info("Calculating composite scores...")
    df = add_composite_score(df)
    status.success("All data loaded!")

    # Defensive: parse release date
    def parse_release_date(row):
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                return datetime.strptime(row["release_date"], fmt)
            except:
                continue
        return datetime(2025, 1, 1)
    df["release_date_obj"] = df.apply(parse_release_date, axis=1)

    album_types = sorted(df['album_type'].dropna().unique())
    selected_album_type = st.sidebar.selectbox("Filter by album type", ["All"] + album_types)

    sort_by = st.sidebar.selectbox("Sort by", ["Release Date (Newest)", "Release Date (Oldest)", "Album Name", "Composite Score"])

    filtered_df = df.copy()
    if selected_album_type != "All":
        filtered_df = filtered_df[filtered_df['album_type'] == selected_album_type]

    if sort_by == "Release Date (Newest)":
        filtered_df = filtered_df.sort_values("release_date_obj", ascending=False)
    elif sort_by == "Release Date (Oldest)":
        filtered_df = filtered_df.sort_values("release_date_obj", ascending=True)
    elif sort_by == "Album Name":
        filtered_df = filtered_df.sort_values("name", key=lambda x: x.str.lower())
    elif sort_by == "Composite Score":
        filtered_df = filtered_df.sort_values("composite_score", ascending=False)

    # Grid view (4 per row)
    for i in range(0, len(filtered_df), 4):
        cols = st.columns(4)
        for j, (_, album) in enumerate(filtered_df.iloc[i:i+4].iterrows()):
            with cols[j]:
                name = album["name"]
                artists = ", ".join(album["artists"])
                release_date = album["release_date"]
                url = album["external_url"]
                image_url = album.get("image_url")
                album_type = album.get("album_type", "unknown")
                composite_score = album.get("composite_score")
                if image_url:
                    st.image(image_url, width=180)
                st.markdown(f"**[{name}]({url})**")
                st.markdown(f"*{artists}*")
                st.markdown(f"Released: {release_date}")
                st.markdown(f"Type: {album_type}")
                if composite_score is not None:
                    rating_bar(composite_score, label="Composite Score")

if __name__ == '__main__':
    main()
