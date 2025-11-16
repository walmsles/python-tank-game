"""
Unit tests for the TankRenderer class.
"""
import unittest
import pygame
from src.renderers.tank_renderer import TankRenderer
from src.renderers.renderer import Renderer
from src.game_objects.player_tank import PlayerTank
from src.game_objects.tank import Tank


class TestTankRenderer(unittest.TestCase):
    """Test cases for the TankRenderer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame
        pygame.init()
        
        # Create a test screen
        self.screen = pygame.Surface((800, 600))
        
        # Create a renderer
        self.renderer = Renderer(self.screen)
        
        # Create a tank renderer
        self.tank_renderer = TankRenderer(self.renderer)
        
        # Create a player tank
        self.player_tank = PlayerTank(100, 200, health=100, speed=5)
        
        # Create an enemy tank
        self.enemy_tank = Tank(300, 200, health=80, speed=4)
        self.enemy_tank.tag = "enemy"
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the tank renderer is initialized correctly."""
        self.assertIsNotNone(self.tank_renderer.player_tank_sprite)
        self.assertIsNotNone(self.tank_renderer.enemy_tank_sprite)
        
    def test_set_player_tank_sprite(self):
        """Test setting the player tank sprite."""
        new_sprite = pygame.Surface((32, 32))
        new_sprite.fill((0, 255, 0))
        
        self.tank_renderer.set_player_tank_sprite(new_sprite)
        self.assertEqual(self.tank_renderer.player_tank_sprite, new_sprite)
        
    def test_set_enemy_tank_sprite(self):
        """Test setting the enemy tank sprite."""
        new_sprite = pygame.Surface((32, 32))
        new_sprite.fill((255, 255, 0))
        
        self.tank_renderer.set_enemy_tank_sprite(new_sprite)
        self.assertEqual(self.tank_renderer.enemy_tank_sprite, new_sprite)
        
    def test_render_player_tank(self):
        """Test rendering a player tank."""
        # This is a visual test, so we just check that it doesn't raise exceptions
        try:
            self.tank_renderer.render_tank(self.screen, self.player_tank)
            # If we got here, the test passed
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_tank raised {type(e).__name__} unexpectedly!")
            
    def test_render_enemy_tank(self):
        """Test rendering an enemy tank."""
        # This is a visual test, so we just check that it doesn't raise exceptions
        try:
            self.tank_renderer.render_tank(self.screen, self.enemy_tank)
            # If we got here, the test passed
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_tank raised {type(e).__name__} unexpectedly!")
            
    def test_render_damaged_tank(self):
        """Test rendering a damaged tank."""
        # Damage the tank
        self.player_tank.take_damage(60)
        
        # This is a visual test, so we just check that it doesn't raise exceptions
        try:
            self.tank_renderer.render_tank(self.screen, self.player_tank)
            # If we got here, the test passed
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_tank raised {type(e).__name__} unexpectedly!")


if __name__ == '__main__':
    unittest.main()