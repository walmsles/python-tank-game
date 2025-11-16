"""
Unit tests for the PlayerTank class.
"""
import unittest
import pygame
from src.game_objects.player_tank import PlayerTank
from src.level_manager.map_data import MapData


class MockInputHandler:
    """Mock input handler for testing."""
    
    def __init__(self):
        """Initialize the mock input handler."""
        self.key_states = {}
        self.previous_key_states = {}
        
    def is_key_pressed(self, key):
        """
        Check if a key is pressed.
        
        Args:
            key: Key name to check
            
        Returns:
            bool: True if the key is pressed, False otherwise
        """
        return self.key_states.get(key, False)
        
    def is_key_just_pressed(self, key):
        """
        Check if a key was just pressed this frame.
        
        Args:
            key: Key name to check
            
        Returns:
            bool: True if the key was just pressed, False otherwise
        """
        return self.key_states.get(key, False) and not self.previous_key_states.get(key, False)
        
    def press_key(self, key):
        """
        Press a key.
        
        Args:
            key: Key name to press
        """
        self.key_states[key] = True
        
    def release_key(self, key):
        """
        Release a key.
        
        Args:
            key: Key name to release
        """
        self.key_states[key] = False
            
    def clear_keys(self):
        """Clear all pressed keys."""
        self.key_states = {}


class TestPlayerTank(unittest.TestCase):
    """Test cases for the PlayerTank class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a player tank
        self.player_tank = PlayerTank(100, 200, health=100, speed=5)
        
        # Create a test sprite
        self.sprite = pygame.Surface((32, 32))
        self.sprite.fill((0, 0, 255))  # Blue
        
        # Set sprite
        self.player_tank.set_sprite(self.sprite)
        
        # Create a test map
        self.map_data = MapData(10, 8)
        self.map_data.set_cell_size(32)
        
        # Add some obstacles to the map
        self.map_data.set_cell(3, 3, MapData.WALL)
        self.map_data.set_cell(3, 4, MapData.WALL)
        self.map_data.set_cell(3, 5, MapData.WALL)
        
        # Create a mock input handler
        self.input_handler = MockInputHandler()
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the player tank is initialized correctly."""
        self.assertEqual(self.player_tank.x, 100)
        self.assertEqual(self.player_tank.y, 200)
        self.assertEqual(self.player_tank.health, 100)
        self.assertEqual(self.player_tank.max_health, 100)
        self.assertEqual(self.player_tank.speed, 5)
        self.assertEqual(self.player_tank.direction, 0)
        self.assertEqual(self.player_tank.tag, "player")
        self.assertTrue(self.player_tank.active)
        
    def test_handle_movement_forward(self):
        """Test handling forward movement input."""
        initial_y = self.player_tank.y
        
        # Press the up key
        self.input_handler.press_key('up')
        
        # Update the player tank
        self.player_tank.update(1/60, self.map_data, self.input_handler)
        
        # Check that the tank moved forward (upward)
        self.assertEqual(self.player_tank.x, 100)  # X should not change
        self.assertLess(self.player_tank.y, initial_y)  # Y should decrease (moving up)
        
    def test_handle_movement_backward(self):
        """Test handling backward movement input."""
        initial_y = self.player_tank.y
        
        # Press the down key
        self.input_handler.press_key('down')
        
        # Update the player tank
        self.player_tank.update(1/60, self.map_data, self.input_handler)
        
        # Check that the tank moved backward (downward)
        self.assertEqual(self.player_tank.x, 100)  # X should not change
        self.assertGreater(self.player_tank.y, initial_y)  # Y should increase (moving down)
        
    def test_handle_rotation_left(self):
        """Test handling left rotation input."""
        # Set direction to 10 degrees to avoid wrapping issues in the test
        self.player_tank.direction = 10
        initial_direction = self.player_tank.direction
        
        # Press the left key
        self.input_handler.press_key('left')
        
        # Update the player tank
        self.player_tank.update(1/60, self.map_data, self.input_handler)
        
        # Check that the tank rotated left (counter-clockwise)
        self.assertLess(self.player_tank.direction, initial_direction)
        
    def test_handle_rotation_right(self):
        """Test handling right rotation input."""
        # Set direction to 10 degrees to avoid wrapping issues in the test
        self.player_tank.direction = 10
        initial_direction = self.player_tank.direction
        
        # Press the right key
        self.input_handler.press_key('right')
        
        # Update the player tank
        self.player_tank.update(1/60, self.map_data, self.input_handler)
        
        # Check that the tank rotated right (clockwise)
        self.assertGreater(self.player_tank.direction, initial_direction)
        
    def test_handle_firing(self):
        """Test handling firing input."""
        # Since we don't have a Projectile class yet, we just check that the cooldown works
        
        # Reset the fire cooldown to a value past the cooldown time
        self.player_tank.last_fire_time = 1.0
        
        # Press the fire key
        self.input_handler.press_key('fire')
        
        # Update the player tank
        self.player_tank.update(1/60, self.map_data, self.input_handler)
        
        # Check that the fire cooldown was reset
        self.assertEqual(self.player_tank.last_fire_time, 0)
        
        # Update again (cooldown should prevent firing)
        self.player_tank.update(1/60, self.map_data, self.input_handler)
        
        # Check that the fire cooldown was not reset again
        self.assertGreater(self.player_tank.last_fire_time, 0)


if __name__ == '__main__':
    unittest.main()