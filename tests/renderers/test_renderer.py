"""
Tests for the renderer module.
"""
import unittest
import pygame
from src.renderers import Renderer, SpriteManager
from src.engine.game_object import GameObject


class TestRenderer(unittest.TestCase):
    """Test cases for the Renderer class."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.renderer = Renderer(self.screen, 60)
        
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
        
    def test_clear_screen(self):
        """Test clearing the screen."""
        # Set background color to red
        self.renderer.set_background_color((255, 0, 0))
        self.renderer.clear_screen()
        
        # Check if the screen is filled with red
        self.assertEqual(self.screen.get_at((0, 0)), (255, 0, 0, 255))
        self.assertEqual(self.screen.get_at((400, 300)), (255, 0, 0, 255))
        
    def test_create_simple_sprite(self):
        """Test creating a simple sprite."""
        sprite = self.renderer.create_simple_sprite("test_sprite", 32, 32, (0, 255, 0))
        
        # Check if the sprite has the correct size and color
        self.assertEqual(sprite.get_width(), 32)
        self.assertEqual(sprite.get_height(), 32)
        self.assertEqual(sprite.get_at((16, 16)), (0, 255, 0, 255))
        
    def test_render_game_objects(self):
        """Test rendering game objects."""
        # Create a test game object
        game_object = GameObject(100, 100)
        sprite = self.renderer.create_simple_sprite("test_sprite", 32, 32, (0, 0, 255))
        game_object.set_sprite(sprite)
        
        # Render the game object
        self.renderer.clear_screen()
        self.renderer.render_game_objects([game_object])
        
        # Check if the game object was rendered at the correct position
        self.assertEqual(self.screen.get_at((100, 100)), (0, 0, 255, 255))
        
    def test_render_text(self):
        """Test rendering text."""
        self.renderer.clear_screen()
        self.renderer.render_text("Test Text", None, 24, (255, 255, 255), 100, 100)
        
        # Since text rendering is complex and depends on the font,
        # we'll just verify that the method doesn't raise an exception
        # This is a simple smoke test
        self.assertTrue(True)
        
    def test_rotate_sprite(self):
        """Test rotating a sprite."""
        sprite = self.renderer.create_simple_sprite("test_sprite", 32, 32, (255, 0, 0))
        rotated_sprite = self.renderer.rotate_sprite(sprite, 90)
        
        # Check if the rotated sprite has the same dimensions
        self.assertEqual(rotated_sprite.get_width(), 32)
        self.assertEqual(rotated_sprite.get_height(), 32)
        
    def test_scale_sprite(self):
        """Test scaling a sprite."""
        sprite = self.renderer.create_simple_sprite("test_sprite", 32, 32, (255, 0, 0))
        scaled_sprite = self.renderer.scale_sprite(sprite, 64, 48)
        
        # Check if the scaled sprite has the correct dimensions
        self.assertEqual(scaled_sprite.get_width(), 64)
        self.assertEqual(scaled_sprite.get_height(), 48)


if __name__ == "__main__":
    unittest.main()