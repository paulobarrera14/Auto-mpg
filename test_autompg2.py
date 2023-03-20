import unittest
from autompg2 import AutoMPG, AutoMPGData


class TestAutoMPG(unittest.TestCase):
    def setUp(self):
        self.car1 = AutoMPG('Subaru', 'Forester', 2018, 32.0)
        self.car2 = AutoMPG('BMW', 'M3', 2022, 23.0)
        self.car3 = AutoMPG('Subaru', 'Forester', 2018, 32.0)

    def test_init(self):
        self.assertEqual(self.car1.make, 'Subaru')
        self.assertEqual(self.car1.model, 'Forester')
        self.assertEqual(self.car1.year, 2018)
        self.assertEqual(self.car1.mpg, 32.0)

    def test_repr(self):
        self.assertEqual(repr(self.car1), 'AutoMPG("Subaru", "Forester", 2018, 32.0)')

    def test_str(self):
        self.assertEqual(str(self.car1), 'Subaru Forester (2018) - 32.0 mpg')

    def test_eq(self):
        self.assertTrue(self.car1 == self.car3)
        self.assertFalse(self.car1 == self.car2)
        self.assertFalse(self.car3 == 40)

    def test_lt(self):
        self.assertTrue(self.car2 < self.car1)
        self.assertFalse(self.car1 < self.car2)

    def test_hash(self):
        self.assertIsInstance(hash(self.car1.make), int)

    def test_autompg(self):
        car = AutoMPG('Toyota', 'Camry', 2000, 25.0)

if __name__ == '__main__':
    unittest.main()


