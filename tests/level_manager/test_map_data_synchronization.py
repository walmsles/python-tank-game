"""
Unit tests for map data synchronization with destructible elements.
"""
import unittest
from unittest.mock import Mock, patch
from src.game_objects.destructible_element import DestructibleElement
from src.game_objects.rock_pile import RockPile
from src.game_objects.petrol_barrel import PetrolBarrel
from src.game_objects.projectile import Projectile
from src.level_manager.map_data import MapData
from src.engine.collision_detector import CollisionDetector


class TestMapDataSynchronization(unittest.TestCase):
    """Test cases for map data synchronization with destructible elements."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a map data object
        self.map_data = MapData(10, 10)
        self.map_data.cell_size = 32
        
        # Create a rock pile
        self.rock_pile = RockPile(64, 64, health=75)
        self.rock_pile.width = 32
        self.rock_pile.height = 32
        
        # Create a petrol barrel
        self.petrol_barrel = PetrolBarrel(128, 128, health=50)
        self.petrol_barrel.width = 32
        self.petrol_barrel.height = 32
        
        # Create a projectile
        self.projectile = Projectile(32, 32, 0, speed=5, damage=100)  # High damage to ensure destruction
        self.projectile.width = 8
        self.projectile.height = 8
        
        # Set up the map data
        self.map_data.set_cell(2, 2, MapData.ROCK_PILE)  # Rock pile at (64, 64)
        self.map_data.set_cell(4, 4, MapData.PETROL_BARREL)  # Petrol barrel at (128, 128)
        
        # Create a collision detector
        self.game_objects = [self.rock_pile, self.petrol_barrel, self.projectile]
        self.collision_detector = CollisionDetector(self.game_objects)
    
    def test_map_data_update_after_rock_pile_destruction(self):
        """Test that map data is updated after rock pile is destroyed."""
        # Set up game objects list
        game_objects = [self.projectile, self.rock_pile]
        
        # Call handle_collision with rock pile cell coordinates
        self.projectile.handle_collision((2, 2), game_objects, self.map_data)
        
        # Assert that the rock pile was destroyed
        self.assertFalse(self.rock_pile.active)
        # Assert that the map data was updated
        self.assertEqual(self.map_data.get_cell(2, 2), MapData.EMPTY)
    
    def test_map_data_update_after_petrol_barrel_destruction(self):
        """Test that map data is updated after petrol barrel is destroyed."""
        # Set up game objects list
        game_objects = [self.projectile, self.petrol_barrel]
        
        # Call handle_collision with petrol barrel cell coordinates
        self.projectile.handle_collision((4, 4), game_objects, self.map_data)
        
        # Assert that the petrol barrel was destroyed
        self.assertFalse(self.petrol_barrel.active)
        # Assert that the map data was updated
        self.assertEqual(self.map_data.get_cell(4, 4), MapData.EMPTY)
    
    def test_collision_detector_updates_map_data(self):
        """Test that collision detector updates map data when destructible element is destroyed."""
        # Create a mock map_data attribute for the collision detector
        self.collision_detector.map_data = self.map_data
        
        # Handle collision between projectile and rock pile
        self.collision_detector._handle_projectile_destructible_collision(self.projectile, self.rock_pile)
        
        # Assert that the rock pile was destroyed
        self.assertFalse(self.rock_pile.active)
        # Assert that the map data was updated
        self.assertEqual(self.map_data.get_cell(2, 2), MapData.EMPTY)
    
    def test_is_obstacle_at_after_destruction(self):
        """Test that is_obstacle_at returns False after destructible element is destroyed."""
        # Destroy the rock pile and update map data
        self.rock_pile.active = False
        self.rock_pile.update_map_data(self.map_data)
        
        # Assert that is_obstacle_at returns False
        self.assertFalse(self.map_data.is_obstacle_at(2, 2))
    
    def test_is_destructible_at_after_destruction(self):
        """Test that is_destructible_at returns False after destructible element is destroyed."""
        # Destroy the rock pile and update map data
        self.rock_pile.active = False
        self.rock_pile.update_map_data(self.map_data)
        
        # Assert that is_destructible_at returns False
        self.assertFalse(self.map_data.is_destructible_at(2, 2))
    
    def test_projectile_movement_through_destroyed_element(self):
        """Test that projectile can move through space where destructible element was destroyed."""
        # Destroy the rock pile and update map data
        self.rock_pile.active = False
        self.rock_pile.update_map_data(self.map_data)
        
        # Check collision at rock pile position
        collision, hit_object = self.projectile._check_collision(64, 64, self.map_data)
        
        # Assert that no collision is detected
        self.assertFalse(collision)
        # Assert that hit_object is None
        self.assertIsNone(hit_object)


if __name__ == '__main__':
    unittest.main()