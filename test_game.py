import unittest
from game import player, running


class TestGame(unittest.TestCase):

    def test_bullet(self):
        self.assertEqual(player.bullet, 10)


if __name__ == '__main__':
    unittest.main()
