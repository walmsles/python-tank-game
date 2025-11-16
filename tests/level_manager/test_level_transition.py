"""
Unit tests for the LevelTransition class.
"""
import unittest
import pygame
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.level_manager.level_transition import LevelTransition
from src.engine.game_engine import GameEngine


class TestLevelTransition(unittest.TestCase):
    """Test cases for the LevelTransition class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for sprite testing
        pygame.init()
        
        # Create a game engine
        self.game_engine = GameEngine(width=640, height=480, title="Test Game Engine")
        self.game_engine.initialize()
        
        # Create a level transition
        self.transition = LevelTransition(self.game_engine)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the level transition is initialized correctly."""
        self.assertFalse(self.transition.active)
        self.assertEqual(self.transition.timer, 0.0)
        self.assertEqual(self.transition.current_level, 1)
        self.assertEqual(self.transition.score, 0)
        self.assertFalse(self.transition.game_complete)
        self.assertEqual(len(self.transition.particles), 0)
        
    def test_start(self):
        """Test that the level transition can be started."""
        # Start the transition
        self.transition.start(3, 500, False)
        
        # Check that the transition is active
        self.assertTrue(self.transition.active)
        self.assertEqual(self.transition.timer, 0.0)
        self.assertEqual(self.transition.current_level, 3)
        self.assertEqual(self.transition.score, 500)
        self.assertFalse(self.transition.game_complete)
        self.assertGreater(len(self.transition.particles), 0)
        
    def test_update(self):
        """Test that the level transition can be updated."""
        # Start the transition
        self.transition.start(3, 500, False)
        
        # Update the transition with a small delta time
        result = self.transition.update(0.1)
        
        # Check that the transition is still active
        self.assertTrue(self.transition.active)
        self.assertEqual(self.transition.timer, 0.1)
        self.assertFalse(result)  # Not complete yet
        
        # Update the transition with a large delta time to complete it
        result = self.transition.update(self.transition.duration)
        
        # Check that the transition is complete
        self.assertFalse(self.transition.active)
        self.assertTrue(result)  # Complete
        self.assertEqual(len(self.transition.particles), 0)  # Particles cleared
        
    def test_game_complete(self):
        """Test that the game complete state is handled correctly."""
        # Start the transition with game complete
        self.transition.start(10, 1000, True)
        
        # Check that the game complete flag is set
        self.assertTrue(self.transition.game_complete)
        
        # Update the transition to completion
        result = self.transition.update(self.transition.duration)
        
        # Check that the transition is complete
        self.assertTrue(result)
        
    def test_render(self):
        """Test that the level transition can be rendered."""
        # Start the transition
        self.transition.start(3, 500, False)
        
        # Create a surface to render on
        surface = pygame.Surface((640, 480))
        
        # Render the transition
        self.transition.render(surface)
        
        # We can't easily test the visual output, but we can check that it doesn't crash
        # and that the transition is still active
        self.assertTrue(self.transition.active)


if __name__ == '__main__':
    unittest.main()