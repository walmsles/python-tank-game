"""
Test module for the GameStateManager class.
"""
import unittest
import pygame
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.engine.game_state_manager import GameStateManager


class TestGameStateManager(unittest.TestCase):
    """Test cases for the GameStateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create a mock game engine
        self.mock_game_engine = MagicMock()
        self.mock_game_engine.game_objects = []
        self.mock_game_engine.level_manager = None
        
        # Create a game state manager
        self.game_state_manager = GameStateManager(self.mock_game_engine)
        
    def tearDown(self):
        """Tear down test fixtures."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the game state manager initializes correctly."""
        self.assertEqual(self.game_state_manager.score, 0)
        self.assertEqual(self.game_state_manager.high_score, 0)
        self.assertFalse(self.game_state_manager.game_over)
        self.assertFalse(self.game_state_manager.victory)
        self.assertFalse(self.game_state_manager.show_game_over_screen)
        self.assertFalse(self.game_state_manager.show_victory_screen)
        self.assertFalse(self.game_state_manager.restart_requested)
        
    def test_update_player_death(self):
        """Test that the game state manager detects player death."""
        # Create a mock player tank
        mock_player = MagicMock()
        mock_player.tag = "player"
        mock_player.active = False
        
        # Add the player to the game objects
        self.mock_game_engine.game_objects = [mock_player]
        
        # Update the game state manager
        self.game_state_manager.update(0.1)
        
        # Check that the game over flag is set
        self.assertTrue(self.game_state_manager.game_over)
        self.assertTrue(self.game_state_manager.show_game_over_screen)
        
    def test_update_victory(self):
        """Test that the game state manager detects victory."""
        # Create a mock level manager
        mock_level_manager = MagicMock()
        mock_level_manager.is_game_complete.return_value = True
        mock_level_manager.get_score.return_value = 100
        
        # Set the level manager on the game engine
        self.mock_game_engine.level_manager = mock_level_manager
        
        # Update the game state manager
        self.game_state_manager.update(0.1)
        
        # Check that the victory flag is set
        self.assertTrue(self.game_state_manager.victory)
        self.assertTrue(self.game_state_manager.show_victory_screen)
        self.assertEqual(self.game_state_manager.high_score, 100)
        
    def test_process_events_restart(self):
        """Test that the game state manager processes restart events."""
        # Set up the game state manager for restart
        self.game_state_manager.show_game_over_screen = True
        
        # Create a mock event for pressing 'R'
        mock_event = MagicMock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_r
        
        # Process the event
        result = self.game_state_manager.process_events([mock_event])
        
        # Check that restart was requested
        self.assertTrue(result)
        self.assertTrue(self.game_state_manager.restart_requested)
        
    def test_reset(self):
        """Test that the game state manager resets correctly."""
        # Set up the game state manager with some state
        self.game_state_manager.game_over = True
        self.game_state_manager.victory = True
        self.game_state_manager.show_game_over_screen = True
        self.game_state_manager.show_victory_screen = True
        self.game_state_manager.restart_requested = True
        
        # Reset the game state manager
        self.game_state_manager.reset()
        
        # Check that the state was reset
        self.assertFalse(self.game_state_manager.game_over)
        self.assertFalse(self.game_state_manager.victory)
        self.assertFalse(self.game_state_manager.show_game_over_screen)
        self.assertFalse(self.game_state_manager.show_victory_screen)
        self.assertFalse(self.game_state_manager.restart_requested)


if __name__ == "__main__":
    unittest.main()