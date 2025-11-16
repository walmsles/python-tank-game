"""
Unit tests for destructible element damage system.
"""
import unittest
from unittest.mock import Mock, patch
from src.game_objects.destructible_element import DestructibleElement
from src.game_objects.rock_pile import RockPile
from src.game_objects.petrol_barrel import PetrolBarrel
from src.level_manager.map_data import MapData


class TestDestructibleElementDamage(unittest.TestCase):
    """Test cases for destructible element damage system."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a map data object
        self.map_data = MapData(10, 10)
        self.map_data.cell_size = 32
        
        # Create a base destructible element
        self.destructible_element = DestructibleElement(32, 32, health=100)
        self.destructible_element.width = 32
        self.destructible_element.height = 32
        
        # Create a rock pile
        self.rock_pile = RockPile(64, 64, health=75)
        self.rock_pile.width = 32
        self.rock_pile.height = 32
        
        # Create a petrol barrel
        self.petrol_barrel = PetrolBarrel(128, 128, health=50)
        self.petrol_barrel.width = 32
        self.petrol_barrel.height = 32
        
        # Set up the map data
        self.map_data.set_cell(1, 1, MapData.ROCK_PILE)  # Rock pile at (32, 32)
        self.map_data.set_cell(2, 2, MapData.ROCK_PILE)  # Rock pile at (64, 64)
        self.map_data.set_cell(4, 4, MapData.PETROL_BARREL)  # Petrol barrel at (128, 128)
    
    def test_destructible_element_take_damage(self):
        """Test that destructible element correctly takes damage."""
        # Apply damage
        result = self.destructible_element.take_damage(30)
        
        # Assert that the element was not destroyed
        self.assertFalse(result)
        # Assert that the health was reduced
        self.assertEqual(self.destructible_element.health, 70)
        # Assert that the element is still active
        self.assertTrue(self.destructible_element.active)
    
    def test_destructible_element_destroy(self):
        """Test that destructible element is correctly destroyed when health reaches zero."""
        # Apply damage that exceeds health
        result = self.destructible_element.take_damage(110)
        
        # Assert that the element was destroyed
        self.assertTrue(result)
        # Assert that the health is zero or less
        self.assertLessEqual(self.destructible_element.health, 0)
        # Assert that the element is no longer active
        self.assertFalse(self.destructible_element.active)
    
    def test_rock_pile_take_damage(self):
        """Test that rock pile correctly takes damage."""
        # Apply damage
        result = self.rock_pile.take_damage(30)
        
        # Assert that the rock pile was not destroyed
        self.assertFalse(result)
        # Assert that the health was reduced
        self.assertEqual(self.rock_pile.health, 45)
        # Assert that the rock pile is still active
        self.assertTrue(self.rock_pile.active)
    
    def test_rock_pile_destroy(self):
        """Test that rock pile is correctly destroyed when health reaches zero."""
        # Apply damage that exceeds health
        result = self.rock_pile.take_damage(80)
        
        # Assert that the rock pile was destroyed
        self.assertTrue(result)
        # Assert that the health is zero or less
        self.assertLessEqual(self.rock_pile.health, 0)
        # Assert that the rock pile is no longer active
        self.assertFalse(self.rock_pile.active)
    
    def test_petrol_barrel_take_damage(self):
        """Test that petrol barrel correctly takes damage."""
        # Apply damage
        result = self.petrol_barrel.take_damage(20)
        
        # Assert that the petrol barrel was not destroyed
        self.assertFalse(result['destroyed'])
        # Assert that there is no explosion
        self.assertIsNone(result['explosion'])
        # Assert that the health was reduced
        self.assertEqual(self.petrol_barrel.health, 30)
        # Assert that the petrol barrel is still active
        self.assertTrue(self.petrol_barrel.active)
    
    def test_petrol_barrel_destroy(self):
        """Test that petrol barrel is correctly destroyed and creates explosion when health reaches zero."""
        # Apply damage that exceeds health
        result = self.petrol_barrel.take_damage(60)
        
        # Assert that the petrol barrel was destroyed
        self.assertTrue(result['destroyed'])
        # Assert that there is an explosion
        self.assertIsNotNone(result['explosion'])
        # Assert that the health is zero or less
        self.assertLessEqual(self.petrol_barrel.health, 0)
        # Assert that the petrol barrel is no longer active
        self.assertFalse(self.petrol_barrel.active)
        
        # Check explosion data
        explosion = result['explosion']
        self.assertIn('center_x', explosion)
        self.assertIn('center_y', explosion)
        self.assertIn('radius', explosion)
        self.assertIn('damage', explosion)
    
    def test_update_map_data(self):
        """Test that destructible element correctly updates map data when destroyed."""
        # Destroy the element
        self.destructible_element.health = 0
        self.destructible_element.active = False
        
        # Update map data
        result = self.destructible_element.update_map_data(self.map_data)
        
        # Assert that the map data was updated
        self.assertTrue(result)
        # Assert that the cell is now empty
        self.assertEqual(self.map_data.get_cell(1, 1), MapData.EMPTY)
    
    def test_update_map_data_not_destroyed(self):
        """Test that destructible element does not update map data when not destroyed."""
        # Element is still active
        self.destructible_element.health = 50
        self.destructible_element.active = True
        
        # Update map data
        result = self.destructible_element.update_map_data(self.map_data)
        
        # Assert that the map data was not updated
        self.assertFalse(result)
        # Assert that the cell is still a rock pile
        self.assertEqual(self.map_data.get_cell(1, 1), MapData.ROCK_PILE)


if __name__ == '__main__':
    unittest.main()