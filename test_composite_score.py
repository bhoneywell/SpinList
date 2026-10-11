import unittest

import pandas as pd

from spotipy_popularity import add_composite_score


class CompositeScoreTest(unittest.TestCase):
    def test_score_ranks_per_day_per_track_values(self):
        df = pd.DataFrame([
            {
                "name": "Reference Min",
                "release_date": "2026-10-09",
                "total_tracks": 1,
                "popularity": 0,
                "lastfm_listeners": 0,
                "lastfm_playcount": 0,
            },
            {
                "name": "Reference Max",
                "release_date": "2026-10-09",
                "total_tracks": 1,
                "popularity": 0,
                "lastfm_listeners": 100,
                "lastfm_playcount": 100,
            },
            {
                "name": "Multi Track Album",
                "release_date": "2026-10-09",
                "total_tracks": 10,
                "popularity": 0,
                "lastfm_listeners": 100,
                "lastfm_playcount": 100,
            },
        ])

        scored = add_composite_score(df)
        album_score = scored.loc[
            scored["name"] == "Multi Track Album",
            "composite_score"
        ].iloc[0]

        self.assertEqual(album_score, 46.67)

    def test_score_uses_percentile_rank_for_lastfm_components(self):
        df = pd.DataFrame([
            {
                "name": "Lowest",
                "release_date": "2026-10-09",
                "total_tracks": 1,
                "popularity": 0,
                "lastfm_listeners": 0,
                "lastfm_playcount": 0,
            },
            {
                "name": "Middle",
                "release_date": "2026-10-09",
                "total_tracks": 1,
                "popularity": 0,
                "lastfm_listeners": 50,
                "lastfm_playcount": 50,
            },
            {
                "name": "Highest",
                "release_date": "2026-10-09",
                "total_tracks": 1,
                "popularity": 0,
                "lastfm_listeners": 100000,
                "lastfm_playcount": 100000,
            },
        ])

        scored = add_composite_score(df)
        middle_score = scored.loc[
            scored["name"] == "Middle",
            "composite_score"
        ].iloc[0]

        self.assertEqual(middle_score, 46.67)


if __name__ == "__main__":
    unittest.main()
