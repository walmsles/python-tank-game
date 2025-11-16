"""
Unit tests for the DifficultyManager class.
"""
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.level_manager.difficulty_manager import DifficultyManager


class TestDifficultyManager(unittest.TestCase):
    """Test cases for the DifficultyManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.difficulty_manager = DifficultyManager(max_difficulty=5)
        
    def test_get_map_difficulty(self):
        """Test that map difficulty is calculated correctly."""
        # Level 1 should have difficulty 1
        self.assertEqual(self.difficulty_manager.get_map_difficulty(1), 1)
        
        # Level 3 should have difficulty 3
        self.assertEqual(self.difficulty_manager.get_map_difficulty(3), 3)
        
        # Level 10 should have difficulty 5 (capped at max_difficulty)
        self.assertEqual(self.difficulty_manager.get_map_difficulty(10), 5)
        
    def test_get_num_enemy_tanks(self):
        """Test that the number of enemy tanks is calculated correctly."""
        # Level 1 should have 1 tank
        self.assertEqual(self.difficulty_manager.get_num_enemy_tanks(1), 1)
        
        # Level 3 should have 3 tanks
        self.assertEqual(self.difficulty_manager.get_num_enemy_tanks(3), 3)
        
        # Level 10 should have 6 tanks (capped at 6)
        self.assertEqual(self.difficulty_manager.get_num_enemy_tanks(10), 6)
        
    def test_get_enemy_tank_difficulties(self):
        """Test that enemy tank difficulties are calculated correctly."""
        # Level 1 with 1 tank should have difficulty 1
        difficulties = self.difficulty_manager.get_enemy_tank_difficulties(1, 1)
        self.assertEqual(len(difficulties), 1)
        self.assertEqual(difficulties[0], 1)
        
        # Level 3 with 3 tanks should have base difficulty 3
        difficulties = self.difficulty_manager.get_enemy_tank_difficulties(3, 3)
        self.assertEqual(len(difficulties), 3)
        self.assertEqual(difficulties[0], 3)  # First tank is always at base difficulty
        
        # All difficulties should be within range 1-5
        for difficulty in difficulties:
            self.assertGreaterEqual(difficulty, 1)
            self.assertLessEqual(difficulty, 5)
            
    def test_get_enemy_spawn_params(self):
        """Test that enemy spawn parameters are calculated correctly."""
        # Level 1 should have base parameters
        params = self.difficulty_manager.get_enemy_spawn_params(1)
        self.assertEqual(params['min_distance_between_tanks'], 5)
        self.assertEqual(params['min_distance_from_player'], 8)
        self.assertEqual(params['spawn_attempts'], 50)
        
        # Level 3 should have adjusted parameters
        params = self.difficulty_manager.get_enemy_spawn_params(3)
        self.assertEqual(params['min_distance_between_tanks'], 4)
        self.assertEqual(params['min_distance_from_player'], 8)
        self.assertEqual(params['spawn_attempts'], 50)
        
        # Level 5 should have further adjusted parameters
        params = self.difficulty_manager.get_enemy_spawn_params(5)
        self.assertEqual(params['min_distance_between_tanks'], 4)
        self.assertEqual(params['min_distance_from_player'], 6)
        self.assertEqual(params['spawn_attempts'], 50)
        
    def test_get_score_multiplier(self):
        """Test that score multiplier is calculated correctly."""
        # Level 1, difficulty 1 should have multiplier 100
        self.assertEqual(self.difficulty_manager.get_score_multiplier(1, 1), 100)
        
        # Level 2, difficulty 2 should have multiplier 400
        self.assertEqual(self.difficulty_manager.get_score_multiplier(2, 2), 400)
        
        # Level 3, difficulty 1 should have multiplier 300
        self.assertEqual(self.difficulty_manager.get_score_multiplier(3, 1), 300)
        
    def test_get_player_params(self):
        """Test that player parameters are calculated correctly."""
        # Level 1 should have base parameters
        params = self.difficulty_manager.get_player_params(1)
        self.assertEqual(params['health'], 100)
        self.assertEqual(params['speed'], 5)
        self.assertEqual(params['fire_cooldown'], 0.5)
        
        # Level 4 should have adjusted parameters
        params = self.difficulty_manager.get_player_params(4)
        self.assertEqual(params['health'], 120)
        self.assertEqual(params['speed'], 5)
        self.assertEqual(params['fire_cooldown'], 0.5)
        
        # Level 7 should have further adjusted parameters
        params = self.difficulty_manager.get_player_params(7)
        self.assertEqual(params['health'], 120)
        self.assertEqual(params['speed'], 5)
        self.assertEqual(params['fire_cooldown'], 0.4)


if __name__ == '__main__':
    unittest.main()