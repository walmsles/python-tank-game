"""
Unit tests for the Projectile class.
"""
import unittest
import pygame
import math
from src.game_objects.projectile import Projectile
from src.level_manager.map_data import MapData
from src.game_objects.tank import Tank


class TestProjectile(unittest.TestCase):
    """Test cases for the Projectile class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a projectile
        self.projectile = Projectile(100, 200, direction=0, speed=10, damage=20)
        
        # Create a test sprite
        self.sprite = pygame.Surface((8, 8))
        self.sprite.fill((255, 255, 0))  # Yellow
        
        # Set sprite
        self.projectile.set_sprite(self.sprite)
        
        # Create a test map
        self.map_data = MapData(10, 8)
        self.map_data.set_cell_size(32)
        
        # Add some obstacles to the map
        self.map_data.set_cell(3, 3, MapData.WALL)
        self.map_data.set_cell(3, 4, MapData.ROCK_PILE)
        self.map_data.set_cell(3, 5, MapData.PETROL_BARREL)
        
        # Create a tank as the owner
        self.tank = Tank(50, 50, health=100, speed=5)
        self.projectile.owner = self.tank
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the projectile is initialized correctly."""
        self.assertEqual(self.projectile.x, 100)
        self.assertEqual(self.projectile.y, 200)
        self.assertEqual(self.projectile.direction, 0)
        self.assertEqual(self.projectile.speed, 10)
        self.assertEqual(self.projectile.damage, 20)
        self.assertEqual(self.projectile.owner, self.tank)
        self.assertEqual(self.projectile.tag, "projectile")
        self.assertTrue(self.projectile.active)
        self.assertEqual(self.projectile.lifetime, 3.0)
        self.assertEqual(self.projectile.time_alive, 0.0)
        
    def test_update_movement(self):
        """Test that the projectile moves correctly."""
        initial_x = self.projectile.x
        initial_y = self.projectile.y
        
        # Update the projectile (direction = 0, which is up)
        self.projectile.update(1/60, self.map_data)
        
        # Check that the projectile moved upward
        self.assertEqual(self.projectile.x, initial_x)
        self.assertLess(self.projectile.y, initial_y)
        
        # Reset position and try a different direction
        self.projectile.x = initial_x
        self.projectile.y = initial_y
        self.projectile.direction = 90  # Right
        
        # Update the projectile
        self.projectile.update(1/60, self.map_data)
        
        # Check that the projectile moved right
        self.assertGreater(self.projectile.x, initial_x)
        self.assertEqual(self.projectile.y, initial_y)
        
    def test_update_lifetime(self):
        """Test that the projectile is deactivated after its lifetime."""
        # Set the lifetime to a small value
        self.projectile.lifetime = 0.1
        
        # Update the projectile with a larger delta time
        result = self.projectile.update(0.2, self.map_data)
        
        # Check that the projectile is no longer active
        self.assertFalse(self.projectile.active)
        self.assertFalse(result)
        
    def test_collision_with_wall(self):
        """Test collision with a wall."""
        # Position the projectile just above a wall
        wall_x, wall_y = 3, 3  # Wall position in grid coordinates
        pixel_x, pixel_y = self.map_data.get_pixel_position(wall_x, wall_y)
        
        # Position the projectile above the wall
        self.projectile.x = pixel_x + self.map_data.cell_size / 2 - self.projectile.width / 2
        self.projectile.y = pixel_y - self.projectile.height - 5
        self.projectile.direction = 180  # Down
        
        # Update the projectile to move it toward the wall
        result = self.projectile.update(1/10, self.map_data)
        
        # Check that the projectile is no longer active
        self.assertFalse(self.projectile.active)
        self.assertFalse(result)
        
    def test_collision_with_destructible(self):
        """Test collision with a destructible element."""
        # Position the projectile just above a destructible element
        rock_x, rock_y = 3, 4  # Rock pile position in grid coordinates
        pixel_x, pixel_y = self.map_data.get_pixel_position(rock_x, rock_y)
        
        # Position the projectile above the rock pile
        self.projectile.x = pixel_x + self.map_data.cell_size / 2 - self.projectile.width / 2
        self.projectile.y = pixel_y - self.projectile.height - 5
        self.projectile.direction = 180  # Down
        
        # Update the projectile to move it toward the rock pile
        result = self.projectile.update(1/10, self.map_data)
        
        # Check that the projectile is no longer active
        self.assertFalse(self.projectile.active)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()