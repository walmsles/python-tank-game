"""
Integration tests for game engine-map data synchronization.
"""
import unittest
from unittest.mock import Mock, patch
import pygame
from src.engine.game_engine import GameEngine
from src.game_objects.rock_pile import RockPile
from src.game_objects.petrol_barrel import PetrolBarrel
from src.game_objects.projectile import Projectile
from src.level_manager.map_data import MapData
from src.level_manager.level_manager import LevelManager


class TestGameEngineMapDataSync(unittest.TestCase):
    """Integration tests for game engine-map data synchronization."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize pygame
        pygame.init()
        
        # Create a game engine
        self.game_engine = GameEngine(width=640, height=480, title="Test Game")
        
        # Create a map data object
        self.map_data = MapData(20, 20)
        self.map_data.cell_size = 32
        
        # Create a mock level manager
        self.level_manager = Mock()
        self.level_manager.map_data = self.map_data
        
        # Set the level manager on the game engine
        self.game_engine.level_manager = self.level_manager
        
        # Create a rock pile
        self.rock_pile = RockPile(160, 160, health=75)
        self.rock_pile.width = 32
        self.rock_pile.height = 32
        
        # Create a petrol barrel
        self.petrol_barrel = PetrolBarrel(320, 320, health=50)
        self.petrol_barrel.width = 32
        self.petrol_barrel.height = 32
        
        # Set up the map data
        self.map_data.set_cell(5, 5, MapData.ROCK_PILE)  # Rock pile at (160, 160)
        self.map_data.set_cell(10, 10, MapData.PETROL_BARREL)  # Petrol barrel at (320, 320)
        
        # Add game objects to the game engine
        self.game_engine.add_game_object(self.rock_pile)
        self.game_engine.add_game_object(self.petrol_barrel)
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_game_engine_passes_map_data_to_game_objects(self):
        """Test that game engine correctly passes map data to game objects."""
        # Create a test projectile that needs map_data
        projectile = Projectile(128, 160, 90, speed=10, damage=30)
        projectile.width = 8
        projectile.height = 8
        
        # Add projectile to game objects
        self.game_engine.add_game_object(projectile)
        
        # Mock the projectile's update method to check if map_data is passed
        original_update = projectile.update
        
        def mock_update(delta_time, map_data=None):
            # Assert that map_data is passed
            self.assertIsNotNone(map_data)
            # Assert that it's the correct map_data
            self.assertEqual(map_data, self.map_data)
            # Call the original update method
            return original_update(delta_time, map_data)
        
        projectile.update = mock_update
        
        # Update the game engine
        self.game_engine.update()
    
    def test_game_engine_removes_destroyed_elements(self):
        """Test that game engine correctly removes destroyed elements from game objects list."""
        # Destroy the rock pile
        self.rock_pile.active = False
        
        # Update the game engine
        self.game_engine.update()
        
        # Assert that the rock pile was removed from game objects
        self.assertNotIn(self.rock_pile, self.game_engine.game_objects)
        # Assert that the petrol barrel is still in game objects
        self.assertIn(self.petrol_barrel, self.game_engine.game_objects)
    
    def test_projectile_destroys_element_and_updates_map_data(self):
        """Test that projectile correctly destroys element and updates map data through game engine."""
        # Create a projectile aimed at the rock pile with high damage
        projectile = Projectile(128, 160, 90, speed=10, damage=100)
        projectile.width = 8
        projectile.height = 8
        
        # Add projectile to game objects
        self.game_engine.add_game_object(projectile)
        
        # Update the game engine for several frames
        for _ in range(10):
            # Update the game engine
            self.game_engine.update()
            
            # Check if projectile is still active
            if not projectile.active:
                break
        
        # Assert that the projectile is no longer active (hit something)
        self.assertFalse(projectile.active)
        # Assert that the rock pile was destroyed
        self.assertFalse(self.rock_pile.active)
        # Assert that the rock pile was removed from game objects
        self.assertNotIn(self.rock_pile, self.game_engine.game_objects)
        # Assert that the map data was updated
        self.assertEqual(self.map_data.get_cell(5, 5), MapData.EMPTY)


if __name__ == '__main__':
    unittest.main()