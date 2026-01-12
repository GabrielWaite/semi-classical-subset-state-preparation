import unittest
from utils.grover_rudolph_angles import GroverRudolphAngles as gra


class TestGroverRudolphAngles(unittest.TestCase):

    def test_multi_controlled_prefixes(self):
        angles_one, angles_two = gra(6), gra(3)
        expected_prefixes_one, expected_prefixes_two = ['0', '1', '00', '01'], ['0']
        self.assertEqual(angles_one.multi_control_prefixes, expected_prefixes_one)
        self.assertEqual(angles_two.multi_control_prefixes, expected_prefixes_two)
         # We expect ValueError for cardinality 2
        with self.assertRaises(ValueError):
            angles_three = gra(2)
            angles_three.multi_control_prefixes

if __name__ == '__main__':
    unittest.main()