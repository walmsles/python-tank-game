"""
Unit tests for the RockPile class.
"""
import unittest
import pygame
from src.game_objects.rock_pile import RockPile


class TestRockPile(unittest.TestCase):
    """Test cases for the RockPile class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a rock pile with default health
        self.rock_pile = RockPile(100, 200)
        
        # Create test sprites
        self.normal_sprite = pygame.Surface((32, 32))
        self.normal_sprite.fill((139, 69, 19))  # Brown
        
        self.damaged_sprite = pygame.Surface((32, 32))
        self.damaged_sprite.fill((160, 82, 45))  # Lighter brown
        
        # Set sprites
        self.rock_pile.set_sprite(self.normal_sprite)
        self.rock_pile.set_damaged_sprite(self.damaged_sprite)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the rock pile is initialized correctly."""
        self.assertEqual(self.rock_pile.x, 100)
        self.assertEqual(self.rock_pile.y, 200)
        self.assertEqual(self.rock_pile.health, 75)  # Default health
        self.assertEqual(self.rock_pile.max_health, 75)
        self.assertTrue(self.rock_pile.destructible)
        self.assertEqual(self.rock_pile.tag, "rock_pile")
        self.assertTrue(self.rock_pile.active)
        
    def test_initialization_with_custom_health(self):
        """Test initialization with custom health value."""
        custom_rock_pile = RockPile(50, 100, health=100)
        self.assertEqual(custom_rock_pile.health, 100)
        self.assertEqual(custom_rock_pile.max_health, 100)
        
    def test_blocks_movement_when_active(self):
        """Test that rock pile blocks movement when active."""
        self.assertTrue(self.rock_pile.blocks_movement())
        
    def test_blocks_projectiles_when_active(self):
        """Test that rock pile blocks projectiles when active."""
        self.assertTrue(self.rock_pile.blocks_projectiles())
        
    def test_blocks_movement_when_destroyed(self):
        """Test that rock pile doesn't block movement when destroyed."""
        # Destroy the rock pile
        self.rock_pile.take_damage(100)
        self.assertFalse(self.rock_pile.blocks_movement())
        
    def test_blocks_projectiles_when_destroyed(self):
        """Test that rock pile doesn't block projectiles when destroyed."""
        # Destroy the rock pile
        self.rock_pile.take_damage(100)
        self.assertFalse(self.rock_pile.blocks_projectiles())
        
    def test_take_damage_light(self):
        """Test taking light damage (should not change sprite)."""
        initial_health = self.rock_pile.health
        destroyed = self.rock_pile.take_damage(20)
        
        self.assertEqual(self.rock_pile.health, initial_health - 20)
        self.assertFalse(destroyed)
        self.assertTrue(self.rock_pile.active)
        self.assertEqual(self.rock_pile.sprite, self.normal_sprite)
        
    def test_take_damage_heavy(self):
        """Test taking heavy damage (should change to damaged sprite)."""
        # Take damage to get below 50% health (75 * 0.5 = 37.5)
        destroyed = self.rock_pile.take_damage(40)
        
        self.assertEqual(self.rock_pile.health, 35)
        self.assertFalse(destroyed)
        self.assertTrue(self.rock_pile.active)
        self.assertEqual(self.rock_pile.sprite, self.damaged_sprite)
        
    def test_take_damage_fatal(self):
        """Test taking fatal damage (should destroy rock pile)."""
        destroyed = self.rock_pile.take_damage(100)
        
        self.assertTrue(destroyed)
        self.assertFalse(self.rock_pile.active)
        self.assertLessEqual(self.rock_pile.health, 0)
        
    def test_damage_state_intact(self):
        """Test damage state when rock pile is intact."""
        self.assertEqual(self.rock_pile.get_damage_state(), "intact")
        
        # Take light damage, should still be intact
        self.rock_pile.take_damage(20)
        self.assertEqual(self.rock_pile.get_damage_state(), "intact")
        
    def test_damage_state_damaged(self):
        """Test damage state when rock pile is damaged."""
        # Take damage to get below 50% health
        self.rock_pile.take_damage(40)
        self.assertEqual(self.rock_pile.get_damage_state(), "damaged")
        
    def test_damage_state_destroyed(self):
        """Test damage state when rock pile is destroyed."""
        # Destroy the rock pile
        self.rock_pile.take_damage(100)
        self.assertEqual(self.rock_pile.get_damage_state(), "destroyed")
        
    def test_visual_damage_indicators(self):
        """Test that visual damage indicators work correctly."""
        # Initially should use normal sprite
        self.assertEqual(self.rock_pile.sprite, self.normal_sprite)
        
        # After heavy damage, should use damaged sprite
        self.rock_pile.take_damage(40)  # Health goes to 35 (< 37.5)
        self.assertEqual(self.rock_pile.sprite, self.damaged_sprite)
        
    def test_destructible_property(self):
        """Test that rock piles are marked as destructible."""
        self.assertTrue(self.rock_pile.destructible)
        
    def test_render_when_active(self):
        """Test that rock pile renders when active."""
        # Create a test screen
        screen = pygame.Surface((800, 600))
        
        # Rock pile should render when active
        self.rock_pile.active = True
        # This should not raise an exception
        self.rock_pile.render(screen)
        
    def test_render_when_inactive(self):
        """Test that rock pile doesn't render when inactive."""
        # Create a test screen
        screen = pygame.Surface((800, 600))
        
        # Rock pile should not render when inactive
        self.rock_pile.active = False
        # This should not raise an exception
        self.rock_pile.render(screen)
        
    def test_multiple_damage_instances(self):
        """Test multiple damage instances and state transitions."""
        # Start with intact state
        self.assertEqual(self.rock_pile.get_damage_state(), "intact")
        
        # Take some damage, still intact
        self.rock_pile.take_damage(20)
        self.assertEqual(self.rock_pile.get_damage_state(), "intact")
        self.assertEqual(self.rock_pile.health, 55)
        
        # Take more damage, now damaged
        self.rock_pile.take_damage(20)
        self.assertEqual(self.rock_pile.get_damage_state(), "damaged")
        self.assertEqual(self.rock_pile.health, 35)
        
        # Take final damage, now destroyed
        self.rock_pile.take_damage(40)
        self.assertEqual(self.rock_pile.get_damage_state(), "destroyed")
        self.assertFalse(self.rock_pile.active)


if __name__ == '__main__':
    unittest.main()