"""
Unit tests for the Tank class.
"""
import unittest
import pygame
import math
from src.game_objects.tank import Tank
from src.level_manager.map_data import MapData


class TestTank(unittest.TestCase):
    """Test cases for the Tank class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a tank
        self.tank = Tank(100, 200, health=100, speed=5)
        
        # Create a test sprite
        self.sprite = pygame.Surface((32, 32))
        self.sprite.fill((0, 128, 0))  # Green
        
        # Set sprite
        self.tank.set_sprite(self.sprite)
        
        # Create a test map
        self.map_data = MapData(10, 8)
        self.map_data.set_cell_size(32)
        
        # Add some obstacles to the map
        self.map_data.set_cell(3, 3, MapData.WALL)
        self.map_data.set_cell(3, 4, MapData.WALL)
        self.map_data.set_cell(3, 5, MapData.WALL)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the tank is initialized correctly."""
        self.assertEqual(self.tank.x, 100)
        self.assertEqual(self.tank.y, 200)
        self.assertEqual(self.tank.health, 100)
        self.assertEqual(self.tank.max_health, 100)
        self.assertEqual(self.tank.speed, 5)
        self.assertEqual(self.tank.direction, 0)
        self.assertEqual(self.tank.tag, "tank")
        self.assertTrue(self.tank.active)
        
    def test_take_damage(self):
        """Test taking damage."""
        # Take some damage
        destroyed = self.tank.take_damage(30)
        self.assertEqual(self.tank.health, 70)
        self.assertFalse(destroyed)
        self.assertTrue(self.tank.active)
        
        # Take fatal damage
        destroyed = self.tank.take_damage(80)
        self.assertEqual(self.tank.health, 0)
        self.assertTrue(destroyed)
        self.assertFalse(self.tank.active)
        
    def test_rotate_left(self):
        """Test rotating the tank counter-clockwise."""
        # Set direction to 10 degrees to avoid wrapping issues in the test
        self.tank.direction = 10
        initial_direction = self.tank.direction
        self.tank.rotate_left(1/60)  # 1/60 second (one frame at 60 FPS)
        self.assertLess(self.tank.direction, initial_direction)
        
    def test_rotate_right(self):
        """Test rotating the tank clockwise."""
        # Set direction to 10 degrees to avoid wrapping issues in the test
        self.tank.direction = 10
        initial_direction = self.tank.direction
        self.tank.rotate_right(1/60)  # 1/60 second (one frame at 60 FPS)
        self.assertGreater(self.tank.direction, initial_direction)
        
    def test_move_forward(self):
        """Test moving the tank forward."""
        initial_x = self.tank.x
        initial_y = self.tank.y
        
        # Move up (direction = 0)
        self.tank.direction = 0
        success = self.tank.move_forward(1/60, self.map_data)
        self.assertTrue(success)
        self.assertEqual(self.tank.x, initial_x)
        self.assertLess(self.tank.y, initial_y)  # Y decreases when moving up
        
        # Move right (direction = 90)
        self.tank.x = initial_x
        self.tank.y = initial_y
        self.tank.direction = 90
        success = self.tank.move_forward(1/60, self.map_data)
        self.assertTrue(success)
        self.assertGreater(self.tank.x, initial_x)  # X increases when moving right
        self.assertEqual(self.tank.y, initial_y)
        
    def test_move_backward(self):
        """Test moving the tank backward."""
        initial_x = self.tank.x
        initial_y = self.tank.y
        
        # Move down (direction = 0, backward = down)
        self.tank.direction = 0
        success = self.tank.move_backward(1/60, self.map_data)
        self.assertTrue(success)
        self.assertEqual(self.tank.x, initial_x)
        self.assertGreater(self.tank.y, initial_y)  # Y increases when moving down
        
        # Move left (direction = 90, backward = left)
        self.tank.x = initial_x
        self.tank.y = initial_y
        self.tank.direction = 90
        success = self.tank.move_backward(1/60, self.map_data)
        self.assertTrue(success)
        self.assertLess(self.tank.x, initial_x)  # X decreases when moving left
        self.assertEqual(self.tank.y, initial_y)
        
    def test_collision_detection(self):
        """Test collision detection with obstacles."""
        # Position the tank just above a wall
        wall_x, wall_y = 3, 4  # Wall position in grid coordinates
        pixel_x, pixel_y = self.map_data.get_pixel_position(wall_x, wall_y)
        
        # Position the tank above the wall, but far enough that the collision radius doesn't reach the wall
        self.tank.x = pixel_x
        self.tank.y = pixel_y - self.tank.height - 20
        self.tank.direction = 180  # Facing down, toward the wall
        
        # Move the tank closer to the wall until it collides
        while True:
            old_y = self.tank.y
            success = self.tank.move_forward(1/60, self.map_data)
            if not success:
                break
            # If we've moved too far without collision, fail the test
            if self.tank.y > pixel_y:
                self.fail("Tank moved through the wall without collision")
        
        # Check that the tank is close to the wall but not overlapping
        self.assertLess(self.tank.y, pixel_y)


if __name__ == '__main__':
    unittest.main()