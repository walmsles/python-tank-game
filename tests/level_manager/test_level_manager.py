"""
Unit tests for the LevelManager class.
"""
import unittest
import pygame
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.level_manager.level_manager import LevelManager
from src.engine.game_engine import GameEngine
from src.game_objects.player_tank import PlayerTank
from src.game_objects.enemy_tank import EnemyTank


class TestLevelManager(unittest.TestCase):
    """Test cases for the LevelManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a game engine
        self.game_engine = GameEngine(width=640, height=480, title="Test Game Engine")
        self.game_engine.initialize()
        
        # Create a player tank
        self.player_tank = PlayerTank(320, 240, health=100, speed=5)
        self.game_engine.add_game_object(self.player_tank)
        
        # Create a level manager
        self.level_manager = LevelManager(self.game_engine, map_width=20, map_height=15, max_level=5)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the level manager is initialized correctly."""
        # Initialize the level manager
        self.level_manager.initialize(self.player_tank)
        
        # Check that the current level is 1
        self.assertEqual(self.level_manager.get_current_level(), 1)
        
        # Check that the max level is 5
        self.assertEqual(self.level_manager.get_max_level(), 5)
        
        # Check that the score is 0
        self.assertEqual(self.level_manager.get_score(), 0)
        
        # Check that the level is not complete
        self.assertFalse(self.level_manager.is_level_complete())
        
        # Check that the game is not complete
        self.assertFalse(self.level_manager.is_game_complete())
        
        # Check that enemy tanks were spawned
        self.assertGreater(len(self.level_manager.enemy_tanks), 0)
        
    def test_start_level(self):
        """Test that a level can be started."""
        # Initialize the level manager
        self.level_manager.initialize(self.player_tank)
        
        # Start level 2
        result = self.level_manager.start_level(2)
        
        # Check that the level was started successfully
        self.assertTrue(result)
        
        # Check that the current level is 2
        self.assertEqual(self.level_manager.get_current_level(), 2)
        
        # Check that the game engine's current level is also 2
        self.assertEqual(self.game_engine.current_level, 2)
        
        # Check that enemy tanks were spawned
        self.assertGreater(len(self.level_manager.enemy_tanks), 0)
        
    def test_invalid_level(self):
        """Test that invalid level numbers are handled correctly."""
        # Initialize the level manager
        self.level_manager.initialize(self.player_tank)
        
        # Try to start level 0 (invalid)
        result = self.level_manager.start_level(0)
        
        # Check that the level was not started
        self.assertFalse(result)
        
        # Check that the current level is still 1
        self.assertEqual(self.level_manager.get_current_level(), 1)
        
        # Try to start level 6 (above max_level)
        result = self.level_manager.start_level(6)
        
        # Check that the level was not started
        self.assertFalse(result)
        
        # Check that the current level is still 1
        self.assertEqual(self.level_manager.get_current_level(), 1)
        
    def test_level_completion(self):
        """Test that level completion is detected correctly."""
        # Initialize the level manager
        self.level_manager.initialize(self.player_tank)
        
        # Remove all enemy tanks to simulate level completion
        for tank in self.level_manager.enemy_tanks:
            self.game_engine.remove_game_object(tank)
        self.level_manager.enemy_tanks = []
        
        # Update the level manager
        self.level_manager.update(0.1)
        
        # Check that the level is marked as complete
        self.assertTrue(self.level_manager.is_level_complete())
        
        # Check that the transition has started
        self.assertTrue(self.level_manager.transition.active)
        
    def test_game_completion(self):
        """Test that game completion is detected correctly."""
        # Initialize the level manager
        self.level_manager.initialize(self.player_tank)
        
        # Set the current level to the max level
        self.level_manager.current_level = self.level_manager.max_level
        
        # Remove all enemy tanks to simulate level completion
        for tank in self.level_manager.enemy_tanks:
            self.game_engine.remove_game_object(tank)
        self.level_manager.enemy_tanks = []
        
        # Update the level manager
        self.level_manager.update(0.1)
        
        # Check that the level is marked as complete
        self.assertTrue(self.level_manager.is_level_complete())
        
        # Check that the game is marked as complete
        self.assertTrue(self.level_manager.is_game_complete())
        
    def test_score_tracking(self):
        """Test that score tracking works correctly."""
        # Initialize the level manager
        self.level_manager.initialize(self.player_tank)
        
        # Check that the initial score is 0
        self.assertEqual(self.level_manager.get_score(), 0)
        
        # Add some points
        self.level_manager.add_score(100)
        
        # Check that the score was updated
        self.assertEqual(self.level_manager.get_score(), 100)
        
        # Simulate destroying an enemy tank
        if self.level_manager.enemy_tanks:
            enemy_tank = self.level_manager.enemy_tanks[0]
            enemy_tank.active = False
            
            # Update the level manager
            self.level_manager.update(0.1)
            
            # Check that points were awarded for destroying the tank
            self.assertGreater(self.level_manager.get_score(), 100)
            
    def test_reset(self):
        """Test that the level manager can be reset."""
        # Initialize the level manager
        self.level_manager.initialize(self.player_tank)
        
        # Start level 3
        self.level_manager.start_level(3)
        
        # Add some score
        self.level_manager.add_score(500)
        
        # Reset the level manager
        self.level_manager.reset()
        
        # Check that the current level is 1
        self.assertEqual(self.level_manager.get_current_level(), 1)
        
        # Check that the score is 0
        self.assertEqual(self.level_manager.get_score(), 0)
        
        # Check that the level is not complete
        self.assertFalse(self.level_manager.is_level_complete())
        
        # Check that the game is not complete
        self.assertFalse(self.level_manager.is_game_complete())
        
    def test_spawn_enemy_tank(self):
        """Test that an enemy tank can be spawned."""
        # Initialize the level manager
        self.level_manager.initialize(self.player_tank)
        
        # Count the initial number of enemy tanks
        initial_count = len(self.level_manager.enemy_tanks)
        
        # Spawn a new enemy tank
        enemy_tank = self.level_manager.spawn_enemy_tank(difficulty=2)
        
        # Check that an enemy tank was returned
        self.assertIsNotNone(enemy_tank)
        
        # Check that the enemy tank is an EnemyTank instance
        self.assertIsInstance(enemy_tank, EnemyTank)
        
        # Check that the enemy tank has the correct difficulty
        self.assertEqual(enemy_tank.difficulty, 2)
        
        # Check that the enemy tank was added to the level manager's list
        self.assertEqual(len(self.level_manager.enemy_tanks), initial_count + 1)
        
        # Check that the enemy tank was added to the game engine
        self.assertIn(enemy_tank, self.game_engine.game_objects)


if __name__ == '__main__':
    unittest.main()