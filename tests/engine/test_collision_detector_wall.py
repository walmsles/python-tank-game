"""
Unit tests for collision detection with Wall obstacles.
"""
import unittest
import pygame
from src.engine.collision_detector import CollisionDetector
from src.game_objects.wall import Wall
from src.game_objects.projectile import Projectile
from src.game_objects.tank import Tank


class TestCollisionDetectorWall(unittest.TestCase):
    """Test cases for collision detection with Wall obstacles."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create test objects
        self.wall = Wall(100, 100)
        self.projectile = Projectile(90, 100, 0, 10, 25, None)
        self.tank = Tank(80, 100, 100, 5)
        
        # Set up sprites
        wall_sprite = pygame.Surface((32, 32))
        wall_sprite.fill((128, 128, 128))
        self.wall.set_sprite(wall_sprite)
        
        projectile_sprite = pygame.Surface((8, 8))
        projectile_sprite.fill((255, 255, 0))
        self.projectile.set_sprite(projectile_sprite)
        
        tank_sprite = pygame.Surface((32, 32))
        tank_sprite.fill((0, 128, 0))
        self.tank.set_sprite(tank_sprite)
        
        # Create collision detector
        self.collision_detector = CollisionDetector()
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_projectile_wall_collision_detection(self):
        """Test that projectile-wall collisions are detected correctly."""
        # Position projectile to collide with wall
        self.projectile.x = 100
        self.projectile.y = 100
        
        game_objects = [self.wall, self.projectile]
        self.collision_detector.set_game_objects(game_objects)
        
        # Check if collision is detected
        self.assertTrue(self.collision_detector._is_projectile_wall_collision(self.projectile, self.wall))
        self.assertTrue(self.collision_detector._is_projectile_wall_collision(self.wall, self.projectile))
        
    def test_tank_wall_collision_detection(self):
        """Test that tank-wall collisions are detected correctly."""
        # Set tank tag
        self.tank.tag = "player_tank"
        
        # Position tank to collide with wall
        self.tank.x = 100
        self.tank.y = 100
        
        game_objects = [self.wall, self.tank]
        self.collision_detector.set_game_objects(game_objects)
        
        # Check if collision is detected
        self.assertTrue(self.collision_detector._is_tank_wall_collision(self.tank, self.wall))
        self.assertTrue(self.collision_detector._is_tank_wall_collision(self.wall, self.tank))
        
    def test_projectile_wall_collision_handling(self):
        """Test that projectile-wall collisions are handled correctly."""
        # Position projectile to collide with wall
        self.projectile.x = 100
        self.projectile.y = 100
        
        # Projectile should be active initially
        self.assertTrue(self.projectile.active)
        
        # Handle collision
        self.collision_detector._handle_projectile_wall_collision(self.projectile, self.wall)
        
        # Projectile should be deactivated
        self.assertFalse(self.projectile.active)
        
        # Wall should remain active (indestructible)
        self.assertTrue(self.wall.active)
        
    def test_wall_blocks_projectile(self):
        """Test that walls block projectiles."""
        self.assertTrue(self.wall.blocks_projectiles())
        
    def test_wall_blocks_movement(self):
        """Test that walls block movement."""
        self.assertTrue(self.wall.blocks_movement())


if __name__ == '__main__':
    unittest.main()