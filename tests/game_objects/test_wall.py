"""
Unit tests for the Wall class.
"""
import unittest
import pygame
from src.game_objects.wall import Wall


class TestWall(unittest.TestCase):
    """Test cases for the Wall class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a wall
        self.wall = Wall(100, 200)
        
        # Create test sprite
        self.wall_sprite = pygame.Surface((32, 32))
        self.wall_sprite.fill((128, 128, 128))  # Gray
        
        # Set sprite
        self.wall.set_sprite(self.wall_sprite)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the wall is initialized correctly."""
        self.assertEqual(self.wall.x, 100)
        self.assertEqual(self.wall.y, 200)
        self.assertFalse(self.wall.destructible)
        self.assertEqual(self.wall.tag, "wall")
        self.assertTrue(self.wall.active)
        
    def test_take_damage(self):
        """Test that walls cannot take damage."""
        # Walls should not take damage
        destroyed = self.wall.take_damage(100)
        self.assertFalse(destroyed)
        self.assertTrue(self.wall.active)
        
        # Try with different damage amounts
        destroyed = self.wall.take_damage(1000)
        self.assertFalse(destroyed)
        self.assertTrue(self.wall.active)
        
    def test_blocks_movement(self):
        """Test that walls block movement."""
        self.assertTrue(self.wall.blocks_movement())
        
    def test_blocks_projectiles(self):
        """Test that walls block projectiles."""
        self.assertTrue(self.wall.blocks_projectiles())
        
    def test_indestructible_property(self):
        """Test that walls are marked as indestructible."""
        self.assertFalse(self.wall.destructible)
        
    def test_render_when_active(self):
        """Test that wall renders when active."""
        # Create a test screen
        screen = pygame.Surface((800, 600))
        
        # Wall should render when active
        self.wall.active = True
        # This should not raise an exception
        self.wall.render(screen)
        
    def test_render_when_inactive(self):
        """Test that wall doesn't render when inactive."""
        # Create a test screen
        screen = pygame.Surface((800, 600))
        
        # Wall should not render when inactive
        self.wall.active = False
        # This should not raise an exception
        self.wall.render(screen)


if __name__ == '__main__':
    unittest.main()