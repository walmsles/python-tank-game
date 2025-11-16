"""
Unit tests for the MapRenderer class.
"""
import unittest
import pygame
from src.renderers.map_renderer import MapRenderer
from src.renderers.renderer import Renderer
from src.level_manager.map_data import MapData


class TestMapRenderer(unittest.TestCase):
    """Test cases for the MapRenderer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame
        pygame.init()
        
        # Create a test screen
        self.screen = pygame.Surface((800, 600))
        
        # Create a renderer
        self.renderer = Renderer(self.screen)
        
        # Create a map renderer
        self.map_renderer = MapRenderer(self.renderer)
        
        # Create a test map
        self.map_data = MapData(10, 8)
        self.map_data.set_cell_size(32)
        
        # Set up some test cells
        self.map_data.set_cell(1, 1, MapData.WALL)  # Wall
        self.map_data.set_cell(2, 2, MapData.ROCK_PILE)  # Rock pile
        self.map_data.set_cell(3, 3, MapData.PETROL_BARREL)  # Petrol barrel
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_initialization(self):
        """Test that the map renderer is initialized correctly."""
        self.assertIsNotNone(self.map_renderer.wall_sprite)
        self.assertIsNotNone(self.map_renderer.rock_pile_sprite)
        self.assertIsNotNone(self.map_renderer.rock_pile_damaged_sprite)
        self.assertIsNotNone(self.map_renderer.petrol_barrel_sprite)
        self.assertIsNotNone(self.map_renderer.petrol_barrel_damaged_sprite)
        self.assertIsNotNone(self.map_renderer.ground_sprite)
        self.assertEqual(self.map_renderer.cell_size, 32)
        
    def test_set_cell_size(self):
        """Test setting the cell size."""
        self.map_renderer.set_cell_size(64)
        self.assertEqual(self.map_renderer.cell_size, 64)
        self.assertEqual(self.map_renderer.wall_sprite.get_width(), 64)
        self.assertEqual(self.map_renderer.wall_sprite.get_height(), 64)
        
    def test_set_wall_sprite(self):
        """Test setting the wall sprite."""
        new_sprite = pygame.Surface((32, 32))
        new_sprite.fill((50, 50, 50))
        
        self.map_renderer.set_wall_sprite(new_sprite)
        self.assertEqual(self.map_renderer.wall_sprite, new_sprite)
        
    def test_set_rock_pile_sprite(self):
        """Test setting the rock pile sprite."""
        new_sprite = pygame.Surface((32, 32))
        new_sprite.fill((100, 50, 0))
        
        damaged_sprite = pygame.Surface((32, 32))
        damaged_sprite.fill((120, 60, 10))
        
        self.map_renderer.set_rock_pile_sprite(new_sprite, damaged_sprite)
        self.assertEqual(self.map_renderer.rock_pile_sprite, new_sprite)
        self.assertEqual(self.map_renderer.rock_pile_damaged_sprite, damaged_sprite)
        
    def test_set_petrol_barrel_sprite(self):
        """Test setting the petrol barrel sprite."""
        new_sprite = pygame.Surface((32, 32))
        new_sprite.fill((150, 0, 0))
        
        damaged_sprite = pygame.Surface((32, 32))
        damaged_sprite.fill((180, 30, 30))
        
        self.map_renderer.set_petrol_barrel_sprite(new_sprite, damaged_sprite)
        self.assertEqual(self.map_renderer.petrol_barrel_sprite, new_sprite)
        self.assertEqual(self.map_renderer.petrol_barrel_damaged_sprite, damaged_sprite)
        
    def test_set_ground_sprite(self):
        """Test setting the ground sprite."""
        new_sprite = pygame.Surface((32, 32))
        new_sprite.fill((200, 200, 100))
        
        self.map_renderer.set_ground_sprite(new_sprite)
        self.assertEqual(self.map_renderer.ground_sprite, new_sprite)
        
    def test_render_map(self):
        """Test rendering the map."""
        # This is a visual test, so we just check that it doesn't raise exceptions
        try:
            self.map_renderer.render_map(self.screen, self.map_data)
            # If we got here, the test passed
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_map raised {type(e).__name__} unexpectedly!")
            
    def test_render_rock_pile(self):
        """Test rendering a rock pile."""
        # Test with full health
        try:
            self.map_renderer.render_rock_pile(self.screen, 100, 100, 100, 100)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_rock_pile raised {type(e).__name__} unexpectedly!")
            
        # Test with damaged state
        try:
            self.map_renderer.render_rock_pile(self.screen, 100, 100, 40, 100)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_rock_pile raised {type(e).__name__} unexpectedly!")
            
    def test_render_petrol_barrel(self):
        """Test rendering a petrol barrel."""
        # Test with full health
        try:
            self.map_renderer.render_petrol_barrel(self.screen, 100, 100, 100, 100)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_petrol_barrel raised {type(e).__name__} unexpectedly!")
            
        # Test with damaged state
        try:
            self.map_renderer.render_petrol_barrel(self.screen, 100, 100, 40, 100)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_petrol_barrel raised {type(e).__name__} unexpectedly!")


if __name__ == '__main__':
    unittest.main()