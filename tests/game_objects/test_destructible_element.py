"""
Unit tests for the DestructibleElement class.
"""
import unittest
import pygame
from src.game_objects.destructible_element import DestructibleElement


class TestDestructibleElement(unittest.TestCase):
    """Test cases for the DestructibleElement class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a destructible element
        self.element = DestructibleElement(100, 200, health=100)
        
        # Create test sprites
        self.normal_sprite = pygame.Surface((32, 32))
        self.normal_sprite.fill((139, 69, 19))  # Brown
        
        self.damaged_sprite = pygame.Surface((32, 32))
        self.damaged_sprite.fill((160, 82, 45))  # Lighter brown
        
        # Set sprites
        self.element.set_sprite(self.normal_sprite)
        self.element.set_damaged_sprite(self.damaged_sprite)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the destructible element is initialized correctly."""
        self.assertEqual(self.element.x, 100)
        self.assertEqual(self.element.y, 200)
        self.assertEqual(self.element.health, 100)
        self.assertEqual(self.element.max_health, 100)
        self.assertTrue(self.element.destructible)
        self.assertEqual(self.element.tag, "destructible")
        self.assertTrue(self.element.active)
        
    def test_take_damage(self):
        """Test taking damage."""
        # Take some damage
        destroyed = self.element.take_damage(30)
        self.assertEqual(self.element.health, 70)
        self.assertFalse(destroyed)
        self.assertTrue(self.element.active)
        
        # Take more damage to trigger sprite change
        destroyed = self.element.take_damage(30)
        self.assertEqual(self.element.health, 40)
        self.assertFalse(destroyed)
        self.assertTrue(self.element.active)
        self.assertEqual(self.element.sprite, self.damaged_sprite)
        
        # Take fatal damage
        destroyed = self.element.take_damage(50)
        self.assertEqual(self.element.health, -10)
        self.assertTrue(destroyed)
        self.assertFalse(self.element.active)
        
    def test_set_damaged_sprite(self):
        """Test setting the damaged sprite."""
        new_sprite = pygame.Surface((32, 32))
        new_sprite.fill((200, 100, 50))
        
        self.element.set_damaged_sprite(new_sprite)
        self.assertEqual(self.element.damaged_sprite, new_sprite)


if __name__ == '__main__':
    unittest.main()