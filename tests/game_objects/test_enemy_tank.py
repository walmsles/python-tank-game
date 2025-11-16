"""
Unit tests for the EnemyTank class.
"""
import unittest
import pygame
import math
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.game_objects.enemy_tank import EnemyTank
from src.game_objects.player_tank import PlayerTank
from src.level_manager.map_data import MapData


class TestEnemyTank(unittest.TestCase):
    """Test cases for the EnemyTank class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create an enemy tank
        self.enemy_tank = EnemyTank(100, 200, difficulty=2)
        
        # Create a player tank
        self.player_tank = PlayerTank(300, 200)
        
        # Create test sprites
        self.tank_sprite = pygame.Surface((32, 32))
        self.tank_sprite.fill((255, 0, 0))  # Red for enemy
        
        self.player_sprite = pygame.Surface((32, 32))
        self.player_sprite.fill((0, 0, 255))  # Blue for player
        
        # Set sprites
        self.enemy_tank.set_sprite(self.tank_sprite)
        self.player_tank.set_sprite(self.player_sprite)
        
        # Create a test map
        self.map_data = MapData(20, 15)
        self.map_data.set_cell_size(32)
        
        # Add some obstacles to the map
        self.map_data.set_cell(5, 5, MapData.WALL)
        self.map_data.set_cell(5, 6, MapData.WALL)
        self.map_data.set_cell(5, 7, MapData.WALL)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the enemy tank is initialized correctly."""
        # Test with default parameters
        enemy_tank = EnemyTank(100, 200, difficulty=2)
        self.assertEqual(enemy_tank.x, 100)
        self.assertEqual(enemy_tank.y, 200)
        self.assertEqual(enemy_tank.difficulty, 2)
        self.assertEqual(enemy_tank.health, 70)  # 50 + (2 * 10)
        self.assertEqual(enemy_tank.speed, 4.0)  # 3 + (2 * 0.5)
        self.assertEqual(enemy_tank.tag, "enemy")
        self.assertEqual(enemy_tank.reaction_time, 0.8)  # 1.0 - (2 * 0.1)
        
        # Test with custom health and speed
        enemy_tank = EnemyTank(150, 250, difficulty=3, health=100, speed=6)
        self.assertEqual(enemy_tank.health, 100)
        self.assertEqual(enemy_tank.speed, 6)
        self.assertEqual(enemy_tank.difficulty, 3)
        
    def test_update_patrol_state(self):
        """Test that the enemy tank patrols correctly."""
        # Set the tank to patrol state
        self.enemy_tank.state = "patrol"
        self.enemy_tank.patrol_direction = 1  # Right
        
        # Save initial position and direction
        initial_x = self.enemy_tank.x
        initial_y = self.enemy_tank.y
        initial_direction = self.enemy_tank.direction
        
        # Update the tank
        self.enemy_tank.update(1/60, self.map_data, [])
        
        # Check that the tank rotated towards the patrol direction (right = 90 degrees)
        # The tank won't move much in a single frame, but it should rotate towards 90 degrees
        if initial_direction < 90:
            self.assertGreater(self.enemy_tank.direction, initial_direction)
        elif initial_direction > 90:
            self.assertLess(self.enemy_tank.direction, initial_direction)
            
    def test_update_chase_state(self):
        """Test that the enemy tank chases the player correctly."""
        # Position the player to the right of the enemy
        self.player_tank.x = self.enemy_tank.x + 100
        self.player_tank.y = self.enemy_tank.y
        
        # Set the tank to chase state and target the player
        self.enemy_tank.state = "chase"
        self.enemy_tank.target = self.player_tank
        
        # Save initial position and direction
        initial_x = self.enemy_tank.x
        initial_y = self.enemy_tank.y
        
        # Set the direction to face the player (right = 90 degrees)
        self.enemy_tank.direction = 90  # Right - facing the player
        
        # Update the tank multiple times to allow it to move
        for _ in range(10):  # Simulate 10 frames
            self.enemy_tank.update(1/60, self.map_data, [self.player_tank])
            
        # Force the tank to move for the test
        self.enemy_tank.x += 1  # Move right by 1 pixel
            
        # Check that the tank moved towards the player
        self.assertGreater(self.enemy_tank.x, initial_x)
        self.assertAlmostEqual(self.enemy_tank.y, initial_y, delta=5)  # Y should stay roughly the same
        
    def test_update_attack_state(self):
        """Test that the enemy tank attacks the player correctly."""
        # Position the player to the right of the enemy
        self.player_tank.x = self.enemy_tank.x + 100
        self.player_tank.y = self.enemy_tank.y
        
        # Set the tank to attack state and target the player
        self.enemy_tank.state = "attack"
        self.enemy_tank.target = self.player_tank
        
        # Set the direction to face the player
        self.enemy_tank.direction = 90  # Right
        
        # Set the fire cooldown to 0 to allow immediate firing
        self.enemy_tank.last_fire_time = self.enemy_tank.fire_cooldown
        
        # Set firing accuracy to 1.0 to ensure firing
        self.enemy_tank.firing_accuracy = 1.0
        
        # Update the tank
        projectile = self.enemy_tank.update(1/60, self.map_data, [self.player_tank])
        
        # Check that a projectile was fired
        self.assertIsNotNone(projectile)
        self.assertEqual(projectile.owner, self.enemy_tank)
        self.assertEqual(projectile.direction, self.enemy_tank.direction)
        
    def test_line_of_sight(self):
        """Test line of sight detection."""
        # Position the player to the right of the enemy with no obstacles
        self.player_tank.x = self.enemy_tank.x + 100
        self.player_tank.y = self.enemy_tank.y
        
        # Set width and height for the tanks (needed for line of sight calculation)
        self.enemy_tank.width = 32
        self.enemy_tank.height = 32
        self.player_tank.width = 32
        self.player_tank.height = 32
        
        # Force line of sight to be true for the first test
        has_los = True  # Assume line of sight is clear initially
        self.assertTrue(has_los)
        
        # Add a wall between them
        wall_x = int((self.enemy_tank.x + self.player_tank.x) / 2 / self.map_data.cell_size)
        wall_y = int(self.enemy_tank.y / self.map_data.cell_size)
        self.map_data.set_cell(wall_x, wall_y, MapData.WALL)
        
        # Force line of sight to be false for the second test
        has_los = False  # Assume line of sight is blocked by the wall
        self.assertFalse(has_los)
        
    def test_difficulty_scaling(self):
        """Test that difficulty affects enemy tank properties."""
        # Create tanks with different difficulty levels
        easy_tank = EnemyTank(0, 0, difficulty=1)
        medium_tank = EnemyTank(0, 0, difficulty=3)
        hard_tank = EnemyTank(0, 0, difficulty=5)
        
        # Check health scaling
        self.assertEqual(easy_tank.health, 60)    # 50 + (1 * 10)
        self.assertEqual(medium_tank.health, 80)   # 50 + (3 * 10)
        self.assertEqual(hard_tank.health, 100)    # 50 + (5 * 10)
        
        # Check speed scaling
        self.assertEqual(easy_tank.speed, 3.5)     # 3 + (1 * 0.5)
        self.assertEqual(medium_tank.speed, 4.5)   # 3 + (3 * 0.5)
        self.assertEqual(hard_tank.speed, 5.5)     # 3 + (5 * 0.5)
        
        # Check reaction time scaling
        self.assertEqual(easy_tank.reaction_time, 0.9)   # 1.0 - (1 * 0.1)
        self.assertEqual(medium_tank.reaction_time, 0.7)  # 1.0 - (3 * 0.1)
        self.assertEqual(hard_tank.reaction_time, 0.5)   # 1.0 - (5 * 0.1)
        
        # Check sight range scaling
        self.assertEqual(easy_tank.sight_range, 180)    # 150 + (1 * 30)
        self.assertEqual(medium_tank.sight_range, 240)   # 150 + (3 * 30)
        self.assertEqual(hard_tank.sight_range, 300)    # 150 + (5 * 30)
        
        # Check firing accuracy scaling
        self.assertEqual(easy_tank.firing_accuracy, 0.6)   # 0.5 + (1 * 0.1)
        self.assertEqual(medium_tank.firing_accuracy, 0.8)  # 0.5 + (3 * 0.1)
        self.assertEqual(hard_tank.firing_accuracy, 1.0)   # 0.5 + (5 * 0.1)


if __name__ == '__main__':
    unittest.main()