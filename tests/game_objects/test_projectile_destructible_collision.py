"""
Unit tests for projectile collision detection with destructible elements.
"""
import unittest
from unittest.mock import Mock
from src.game_objects.projectile import Projectile
from src.game_objects.rock_pile import RockPile
from src.game_objects.petrol_barrel import PetrolBarrel
from src.level_manager.map_data import MapData


class TestProjectileDestructibleCollision(unittest.TestCase):
    """Test cases for projectile collision detection with destructible elements."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a map data object
        self.map_data = MapData(10, 10)
        self.map_data.cell_size = 32
        
        # Create a projectile
        self.projectile = Projectile(32, 32, 0, speed=5, damage=20)
        self.projectile.width = 8
        self.projectile.height = 8
        
        # Create a rock pile
        self.rock_pile = RockPile(64, 64, health=75)
        self.rock_pile.width = 32
        self.rock_pile.height = 32
        
        # Create a petrol barrel
        self.petrol_barrel = PetrolBarrel(128, 128, health=50)
        self.petrol_barrel.width = 32
        self.petrol_barrel.height = 32
        
        # Set up the map data
        self.map_data.set_cell(2, 2, MapData.ROCK_PILE)  # Rock pile at (64, 64)
        self.map_data.set_cell(4, 4, MapData.PETROL_BARREL)  # Petrol barrel at (128, 128)
    
    def test_projectile_rock_pile_collision_detection(self):
        """Test that projectile correctly detects collision with rock pile."""
        # Check collision at rock pile position
        collision, hit_object = self.projectile._check_collision(64, 64, self.map_data)
        
        # Assert that collision is detected
        self.assertTrue(collision)
        # Assert that hit_object is a tuple of cell coordinates
        self.assertIsInstance(hit_object, tuple)
        # Assert that the cell coordinates are correct
        self.assertEqual(hit_object, (2, 2))
    
    def test_projectile_petrol_barrel_collision_detection(self):
        """Test that projectile correctly detects collision with petrol barrel."""
        # Check collision at petrol barrel position
        collision, hit_object = self.projectile._check_collision(128, 128, self.map_data)
        
        # Assert that collision is detected
        self.assertTrue(collision)
        # Assert that hit_object is a tuple of cell coordinates
        self.assertIsInstance(hit_object, tuple)
        # Assert that the cell coordinates are correct
        self.assertEqual(hit_object, (4, 4))
    
    def test_projectile_no_collision(self):
        """Test that projectile correctly detects no collision with empty space."""
        # Check collision at empty position
        collision, hit_object = self.projectile._check_collision(32, 32, self.map_data)
        
        # Assert that no collision is detected
        self.assertFalse(collision)
        # Assert that hit_object is None
        self.assertIsNone(hit_object)
    
    def test_projectile_handle_collision_with_rock_pile(self):
        """Test that projectile correctly handles collision with rock pile."""
        # Set up game objects list
        game_objects = [self.projectile, self.rock_pile]
        
        # Call handle_collision with rock pile cell coordinates
        result = self.projectile.handle_collision((2, 2), game_objects, self.map_data)
        
        # Assert that the projectile should be removed
        self.assertTrue(result)
        # Assert that the rock pile took damage
        self.assertEqual(self.rock_pile.health, 55)  # 75 - 20 = 55
    
    def test_projectile_handle_collision_with_petrol_barrel(self):
        """Test that projectile correctly handles collision with petrol barrel."""
        # Set up game objects list
        game_objects = [self.projectile, self.petrol_barrel]
        
        # Call handle_collision with petrol barrel cell coordinates
        result = self.projectile.handle_collision((4, 4), game_objects, self.map_data)
        
        # Assert that the projectile should be removed
        self.assertTrue(result)
        # Assert that the petrol barrel took damage
        self.assertEqual(self.petrol_barrel.health, 30)  # 50 - 20 = 30
    
    def test_projectile_destroy_rock_pile(self):
        """Test that projectile correctly destroys rock pile and updates map data."""
        # Set up game objects list
        game_objects = [self.projectile, self.rock_pile]
        
        # Set rock pile health to just above damage amount
        self.rock_pile.health = 19
        
        # Call handle_collision with rock pile cell coordinates
        result = self.projectile.handle_collision((2, 2), game_objects, self.map_data)
        
        # Assert that the projectile should be removed
        self.assertTrue(result)
        # Assert that the rock pile was destroyed
        self.assertFalse(self.rock_pile.active)
        # Assert that the map data was updated
        self.assertEqual(self.map_data.get_cell(2, 2), MapData.EMPTY)
    
    def test_projectile_destroy_petrol_barrel(self):
        """Test that projectile correctly destroys petrol barrel and updates map data."""
        # Set up game objects list
        game_objects = [self.projectile, self.petrol_barrel]
        
        # Set petrol barrel health to just above damage amount
        self.petrol_barrel.health = 19
        
        # Call handle_collision with petrol barrel cell coordinates
        result = self.projectile.handle_collision((4, 4), game_objects, self.map_data)
        
        # Assert that the projectile should be removed
        self.assertTrue(result)
        # Assert that the petrol barrel was destroyed
        self.assertFalse(self.petrol_barrel.active)
        # Assert that the map data was updated
        self.assertEqual(self.map_data.get_cell(4, 4), MapData.EMPTY)


if __name__ == '__main__':
    unittest.main()