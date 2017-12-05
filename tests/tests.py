import stats
import unittest

stats.DUMP_FILE = 'tests/test.db'


class Tests(unittest.TestCase):
    def test_last_n(self):
        res = stats.last_n(n=1, step_size=1)
        self.assertEqual(res, [{'id': 10}])

        res = stats.last_n(n=2, step_size=1)
        self.assertEqual(res, [{'id': 10}, {'id': 9}])

        res = stats.last_n(n=100, step_size=1)
        self.assertEqual(res, [
            {'id': 10},
            {'id': 9},
            {'id': 8},
            {'id': 7},
            {'id': 6},
            {'id': 5},
            {'id': 4},
            {'id': 3},
            {'id': 2},
            {'id': 1},
            {'id': 0}
        ])

    def test_step_size(self):
        res = stats.last_n(n=1, step_size=10)
        self.assertEqual(res, [{'id': 10}])

        res = stats.last_n(n=2, step_size=10)
        self.assertEqual(res, [{'id': 10}, {'id': 0}])

        res = stats.last_n(n=3, step_size=10)
        self.assertEqual(res, [{'id': 10}, {'id': 0}])

        res = stats.last_n(n=3, step_size=2)
        self.assertEqual(res, [{'id': 10}, {'id': 8}, {'id': 6}])

        res = stats.last_n(n=3, step_size=200)
        self.assertEqual(res, [{'id': 10}])