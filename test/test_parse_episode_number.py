from unittest import TestCase
from webcine.utils.indexer import parse_episode_number


class TestParse_episode_number(TestCase):
    def test_parse_episode_number(self):
        dataset = [
            ('S01E01', 1, 1),
            ('Sherlock.s02e03', 2, 3)
        ]
        for data, season, episode in dataset:
            result = parse_episode_number(data)
            self.assertSame(result[0], season)
            self.assertSame(result[1], episode)