"""
Unit tests for the EnemyTankSpawner class.
"""
import unittest
import pygame
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.level_manager.enemy_tank_spawner import EnemyTankSpawner
from src.level_manager.map_data import MapData
from src.level_manager.map_generator import MapGenerator
from src.engine.game_engine import GameEngine


class TestEnemyTankSpawner(unittest.TestCase):
    """Test cases for the EnemyTankSpawner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a map generator
        self.map_generator = MapGenerator(20, 15)
        
        # Generate a map
        self.map_data = self.map_generator.generate_map(difficulty=1)
        self.map_data.set_cell_size(32)
        
        # Create a game engine
        self.game_engine = GameEngine(width=640, height=480, title="Test Game Engine")
        self.game_engine.initialize()
        
        # Create an enemy tank spawner
        self.spawner = EnemyTankSpawner(self.map_data)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_calculate_num_tanks(self):
        """Test that the number of tanks is calculated correctly based on level."""
        # Level 1 should have 1 tank
        self.assertEqual(self.spawner._calculate_num_tanks(1), 1)
        
        # Level 3 should have 3 tanks
        self.assertEqual(self.spawner._calculate_num_tanks(3), 3)
        
        # Level 10 should have 6 tanks (capped at 6)
        self.assertEqual(self.spawner._calculate_num_tanks(10), 6)
        
    def test_calculate_difficulties(self):
        """Test that the difficulty levels are calculated correctly."""
        # Level 1 with 1 tank should have difficulty 1
        difficulties = self.spawner._calculate_difficulties(1, 1)
        self.assertEqual(len(difficulties), 1)
        self.assertEqual(difficulties[0], 1)
        
        # Level 3 with 3 tanks should have base difficulty 3
        difficulties = self.spawner._calculate_difficulties(3, 3)
        self.assertEqual(len(difficulties), 3)
        self.assertEqual(difficulties[0], 3)  # First tank is always at base difficulty
        
        # Level 10 with 6 tanks should have base difficulty 5 (capped at 5)
        difficulties = self.spawner._calculate_difficulties(10, 6)
        self.assertEqual(len(difficulties), 6)
        self.assertEqual(difficulties[0], 5)  # First tank is always at base difficulty
        
    def test_spawn_enemy_tanks(self):
        """Test that enemy tanks are spawned correctly."""
        # Spawn tanks for level 1
        player_position = (320, 240)  # Center of the screen
        enemy_tanks = self.spawner.spawn_enemy_tanks(1, player_position, self.game_engine)
        
        # Level 1 should have 1 tank
        self.assertEqual(len(enemy_tanks), 1)
        
        # The tank should be an EnemyTank instance
        self.assertEqual(enemy_tanks[0].tag, "enemy")
        
        # The tank should have difficulty 1
        self.assertEqual(enemy_tanks[0].difficulty, 1)
        
        # The tank should be added to the game engine
        self.assertIn(enemy_tanks[0], self.game_engine.game_objects)
        
    def test_spawn_multiple_enemy_tanks(self):
        """Test that multiple enemy tanks are spawned correctly."""
        # Spawn tanks for level 3
        player_position = (320, 240)  # Center of the screen
        enemy_tanks = self.spawner.spawn_enemy_tanks(3, player_position, self.game_engine)
        
        # Level 3 should have 3 tanks
        self.assertEqual(len(enemy_tanks), 3)
        
        # All tanks should be added to the game engine
        for tank in enemy_tanks:
            self.assertIn(tank, self.game_engine.game_objects)
            
    def test_spawn_single_enemy_tank(self):
        """Test that a single enemy tank is spawned correctly."""
        # Spawn a single tank with difficulty 2
        player_position = (320, 240)  # Center of the screen
        enemy_tank = self.spawner.spawn_single_enemy_tank(2, player_position, self.game_engine)
        
        # The tank should be an EnemyTank instance
        self.assertEqual(enemy_tank.tag, "enemy")
        
        # The tank should have difficulty 2
        self.assertEqual(enemy_tank.difficulty, 2)
        
        # The tank should be added to the game engine
        self.assertIn(enemy_tank, self.game_engine.game_objects)


if __name__ == '__main__':
    unittest.main()