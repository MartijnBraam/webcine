from unittest import TestCase
from webcine.utils.nameparser import parse_episode_number


class TestParse_episode_number(TestCase):
    def test_parse_episode_number(self):
        dataset = [
            ('S01E01.mkv', 1, 1),
            ('Sherlock.s02e03.avi', 2, 3),
            ('Finale.211.mp4', 2, 11),
            ('Episode 720p h264 101.mp4', 1, 1)
        ]
        for data, season, episode in dataset:
            result = parse_episode_number(data)
            self.assertEqual(result[0], season, 'Season number incorrect')
            self.assertEqual(result[1], episode, 'Episode number incorrect')
