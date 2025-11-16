"""
Unit tests for the GameObject class.
"""

import unittest
import pygame
from unittest.mock import MagicMock
from src.game_objects.game_object import GameObject


class TestGameObject(unittest.TestCase):
    """Test cases for the GameObject class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()

        # Create a GameObject instance for testing
        self.game_object = GameObject(10, 20)

    def tearDown(self):
        """Tear down test fixtures."""
        pygame.quit()

    def test_init(self):
        """Test GameObject initialization."""
        self.assertEqual(self.game_object.x, 10)
        self.assertEqual(self.game_object.y, 20)
        self.assertIsNone(self.game_object.sprite)

    def test_set_position(self):
        """Test setting the position of a GameObject."""
        self.game_object.set_position(30, 40)
        self.assertEqual(self.game_object.x, 30)
        self.assertEqual(self.game_object.y, 40)

    def test_get_position(self):
        """Test getting the position of a GameObject."""
        position = self.game_object.get_position()
        self.assertEqual(position, (10, 20))

        # Test after changing position
        self.game_object.set_position(50, 60)
        position = self.game_object.get_position()
        self.assertEqual(position, (50, 60))

    def test_update(self):
        """Test the update method."""
        # The base update method doesn't do anything, so just ensure it runs without error
        self.game_object.update(0.16)  # Typical frame time for 60 FPS

    def test_render_without_sprite(self):
        """Test rendering without a sprite."""
        # Create a mock screen
        mock_screen = MagicMock()

        # Render the game object (should do nothing since sprite is None)
        self.game_object.render(mock_screen)

        # Verify that blit was not called
        mock_screen.blit.assert_not_called()

    def test_render_with_sprite(self):
        """Test rendering with a sprite."""
        # Create a mock screen and sprite
        mock_screen = MagicMock()
        mock_sprite = MagicMock()

        # Set the sprite
        self.game_object.sprite = mock_sprite

        # Render the game object
        self.game_object.render(mock_screen)

        # Verify that blit was called with the correct arguments
        mock_screen.blit.assert_called_once_with(mock_sprite, (10, 20))


if __name__ == "__main__":
    unittest.main()
