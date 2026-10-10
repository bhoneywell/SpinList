import unittest
from datetime import datetime

from spotify_data import get_release_window, release_date_in_window


class ReleaseWindowTest(unittest.TestCase):
    def test_first_half_year_includes_previous_july_through_current_year(self):
        start_date, label = get_release_window(datetime(2026, 3, 15))

        self.assertEqual(start_date, datetime(2025, 7, 1))
        self.assertEqual(label, "July 2025-present")
        self.assertTrue(release_date_in_window("2025-07-01", start_date))
        self.assertTrue(release_date_in_window("2026-03-15", start_date))
        self.assertFalse(release_date_in_window("2025-06-30", start_date))

    def test_second_half_year_includes_current_calendar_year(self):
        start_date, label = get_release_window(datetime(2026, 10, 10))

        self.assertEqual(start_date, datetime(2026, 1, 1))
        self.assertEqual(label, "2026")
        self.assertTrue(release_date_in_window("2026-01-01", start_date))
        self.assertFalse(release_date_in_window("2025-12-31", start_date))


if __name__ == "__main__":
    unittest.main()
