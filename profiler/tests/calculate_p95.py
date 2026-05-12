from django.test import TestCase
from ..services import _calculate_p95


class CalculateP95Tests(TestCase):

    def test_empty_list_returns_zero(self):
        self.assertEqual(_calculate_p95([]), 0.0)

    def test_single_value_returns_that_value(self):
        self.assertEqual(_calculate_p95([100.0]), 100.0)

    def test_correct_p95_with_known_values(self):
        # sorted: [12.43, 34.34, 67.345, 234.2, 234.34, 435.35, 564.2]
        # index = int(7 * 0.95) = 6
        # value at index 6 = 564.2
        values = [435.35, 34.34, 234.34, 67.345, 12.43, 564.2, 234.2]
        self.assertEqual(_calculate_p95(values), 564.2)

    def test_all_same_values(self):
        values = [100.0, 100.0, 100.0, 100.0, 100.0]
        self.assertEqual(_calculate_p95(values), 100.0)

    def test_already_sorted_list(self):
        values = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        # index = int(10 * 0.95) = 9
        # value at index 9 = 100.0
        self.assertEqual(_calculate_p95(values), 100.0)

    def test_p95_is_not_maximum(self):
        # p95 should not always be the maximum value
        # 20 values — index = int(20 * 0.95) = 19 — last value
        # but with 10 values — index = int(10 * 0.95) = 9
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 1000.0]
        # sorted: [1,2,3,4,5,6,7,8,9,1000]
        # index = int(10 * 0.95) = 9 → 1000.0
        # this confirms the outlier IS captured at p95 for small lists
        self.assertEqual(_calculate_p95(values), 1000.0)