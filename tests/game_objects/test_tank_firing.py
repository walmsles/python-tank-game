"""
Unit tests for the tank firing mechanism.
"""
import unittest
import pygame
from src.game_objects.tank import Tank
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


class TestTankFiring(unittest.TestCase):
    """Test cases for the tank firing mechanism."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a tank
        self.tank = Tank(100, 200, health=100, speed=5)
        
        # Create a player tank
        self.player_tank = PlayerTank(300, 200, health=100, speed=5)
        
        # Create test sprites
        self.tank_sprite = pygame.Surface((32, 32))
        self.tank_sprite.fill((0, 128, 0))  # Green
        
        # Set sprites
        self.tank.set_sprite(self.tank_sprite)
        self.player_tank.set_sprite(self.tank_sprite)
        
        # Create a test map
        self.map_data = MapData(10, 8)
        self.map_data.set_cell_size(32)
        
        # Create a mock input handler
        self.input_handler = MockInputHandler()
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_tank_fire(self):
        """Test that a tank can fire a projectile."""
        # Set the fire cooldown to 0 to allow immediate firing
        self.tank.last_fire_time = self.tank.fire_cooldown
        
        # Fire a projectile
        projectile = self.tank.fire()
        
        # Check that a projectile was created
        self.assertIsNotNone(projectile)
        self.assertEqual(projectile.owner, self.tank)
        self.assertEqual(projectile.direction, self.tank.direction)
        
        # Check that the fire cooldown was reset
        self.assertEqual(self.tank.last_fire_time, 0)
        
        # Try to fire again immediately (should fail due to cooldown)
        projectile = self.tank.fire()
        self.assertIsNone(projectile)
        
    def test_player_tank_fire_input(self):
        """Test that the player tank fires when the fire key is pressed."""
        # Set the fire cooldown to 0 to allow immediate firing
        self.player_tank.last_fire_time = self.player_tank.fire_cooldown
        
        # Press the fire key
        self.input_handler.press_key('fire')
        
        # Update the player tank
        projectile = self.player_tank.update(1/60, self.map_data, self.input_handler)
        
        # Check that a projectile was created
        self.assertIsNotNone(projectile)
        self.assertEqual(projectile.owner, self.player_tank)
        
        # Try to fire again immediately (should fail due to cooldown)
        projectile = self.player_tank.update(1/60, self.map_data, self.input_handler)
        self.assertIsNone(projectile)
        
    def test_projectile_position(self):
        """Test that the projectile is created at the correct position."""
        # Set the fire cooldown to 0 to allow immediate firing
        self.tank.last_fire_time = self.tank.fire_cooldown
        
        # Set the tank direction
        self.tank.direction = 0  # Up
        
        # Fire a projectile
        projectile = self.tank.fire()
        
        # Check that the projectile is positioned at the end of the tank's barrel
        self.assertIsNotNone(projectile)
        
        # The projectile should be above the tank (since direction is 0, which is up)
        self.assertLess(projectile.y, self.tank.y)
        
        # Try a different direction
        self.tank.direction = 90  # Right
        self.tank.last_fire_time = self.tank.fire_cooldown
        projectile = self.tank.fire()
        
        # The projectile should be to the right of the tank
        self.assertGreater(projectile.x, self.tank.x)
        
        # The projectile should be vertically centered with the tank (approximately)
        tank_center_y = self.tank.y + self.tank.height / 2
        projectile_center_y = projectile.y + projectile.height / 2
        self.assertAlmostEqual(projectile_center_y, tank_center_y, delta=5)  # Allow some tolerance


if __name__ == '__main__':
    unittest.main()