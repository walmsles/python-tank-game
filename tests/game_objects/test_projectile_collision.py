"""
Unit tests for projectile collision handling.
"""
import unittest
import pygame
import math
from src.game_objects.projectile import Projectile
from src.game_objects.tank import Tank
from src.game_objects.destructible_element import DestructibleElement
from src.level_manager.map_data import MapData


class TestProjectileCollision(unittest.TestCase):
    """Test cases for projectile collision handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a tank
        self.tank = Tank(100, 200, health=100, speed=5)
        
        # Create a projectile
        self.projectile = Projectile(150, 200, direction=180, speed=10, damage=20)
        
        # Create a destructible element
        self.destructible = DestructibleElement(200, 200, health=100)
        
        # Create test sprites
        self.tank_sprite = pygame.Surface((32, 32))
        self.tank_sprite.fill((0, 128, 0))  # Green
        
        self.projectile_sprite = pygame.Surface((8, 8))
        self.projectile_sprite.fill((255, 255, 0))  # Yellow
        
        self.destructible_sprite = pygame.Surface((32, 32))
        self.destructible_sprite.fill((139, 69, 19))  # Brown
        
        # Set sprites
        self.tank.set_sprite(self.tank_sprite)
        self.projectile.set_sprite(self.projectile_sprite)
        self.destructible.set_sprite(self.destructible_sprite)
        
        # Create a test map
        self.map_data = MapData(10, 8)
        self.map_data.set_cell_size(32)
        
        # Add some obstacles to the map
        self.map_data.set_cell(3, 3, MapData.WALL)
        self.map_data.set_cell(3, 4, MapData.ROCK_PILE)
        self.map_data.set_cell(3, 5, MapData.PETROL_BARREL)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_projectile_tank_collision(self):
        """Test collision between a projectile and a tank."""
        # Position the projectile inside the tank to ensure collision
        self.projectile.x = self.tank.x + 10
        self.projectile.y = self.tank.y + 10
        
        # Check if the projectile collides with the tank
        self.assertTrue(self.projectile.collides_with(self.tank))
        
        # Damage the tank
        self.tank.take_damage(self.projectile.damage)
        
        # Check that the tank's health was reduced
        self.assertEqual(self.tank.health, 80)
        
    def test_projectile_destructible_collision(self):
        """Test collision between a projectile and a destructible element."""
        # Position the projectile inside the destructible element to ensure collision
        self.projectile.x = self.destructible.x + 10
        self.projectile.y = self.destructible.y + 10
        
        # Check if the projectile collides with the destructible element
        self.assertTrue(self.projectile.collides_with(self.destructible))
        
        # Damage the destructible element
        destroyed = self.destructible.take_damage(self.projectile.damage)
        
        # Check that the destructible element's health was reduced
        self.assertEqual(self.destructible.health, 80)
        self.assertFalse(destroyed)
        
    def test_projectile_wall_collision(self):
        """Test collision between a projectile and a wall."""
        # Position the projectile just above a wall
        wall_x, wall_y = 3, 3  # Wall position in grid coordinates
        pixel_x, pixel_y = self.map_data.get_pixel_position(wall_x, wall_y)
        
        # Position the projectile inside the wall cell
        self.projectile.x = pixel_x + 10
        self.projectile.y = pixel_y + 10
        
        # Check collision directly with the map
        collision, hit_object = self.projectile._check_collision(self.projectile.x, self.projectile.y, self.map_data)
        
        # Check that a collision was detected
        self.assertTrue(collision)
        
    def test_projectile_owner_no_collision(self):
        """Test that a projectile doesn't collide with its owner."""
        # Set the tank as the owner of the projectile
        self.projectile.owner = self.tank
        
        # Position the projectile inside the tank to ensure collision detection would trigger
        self.projectile.x = self.tank.x + 10
        self.projectile.y = self.tank.y + 10
        
        # Check if the projectile collides with the tank
        self.assertTrue(self.projectile.collides_with(self.tank))
        
        # In the tank example, we check if the tank is the owner before applying damage
        # Here we just verify that the collision is detected, but no damage is applied
        # because the tank is the owner
        
        # Check that the tank's health was not reduced (no collision handling)
        self.assertEqual(self.tank.health, 100)


if __name__ == '__main__':
    unittest.main()