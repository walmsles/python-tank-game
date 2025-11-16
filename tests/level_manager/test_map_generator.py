"""
Unit tests for the MapGenerator class.
"""
import unittest
from src.level_manager.map_generator import MapGenerator
from src.level_manager.map_data import MapData


class TestMapGenerator(unittest.TestCase):
    """Test cases for the MapGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.map_generator = MapGenerator(20, 15)
        
    def test_initialization(self):
        """Test that the map generator is initialized correctly."""
        self.assertEqual(self.map_generator.width, 20)
        self.assertEqual(self.map_generator.height, 15)
        
    def test_generate_map(self):
        """Test generating a map."""
        map_data = self.map_generator.generate_map(difficulty=1)
        
        # Check that the map has the correct dimensions
        self.assertEqual(map_data.width, 20)
        self.assertEqual(map_data.height, 15)
        
        # Check that the map contains obstacles, empty spaces, and destructible elements
        self.assertGreater(map_data.count_wall_cells(), 0)
        self.assertGreater(map_data.count_empty_cells(), 0)
        self.assertGreater(map_data.count_destructible_cells(), 0)
        
        # Check that the total number of cells is correct
        total_cells = (map_data.count_wall_cells() + 
                       map_data.count_empty_cells() + 
                       map_data.count_destructible_cells())
        self.assertEqual(total_cells, 20 * 15)
        
        # Check that the map has boundary walls
        for x in range(20):
            self.assertEqual(map_data.get_cell(x, 0), MapData.WALL)
            self.assertEqual(map_data.get_cell(x, 14), MapData.WALL)
        
        for y in range(15):
            self.assertEqual(map_data.get_cell(0, y), MapData.WALL)
            self.assertEqual(map_data.get_cell(19, y), MapData.WALL)
        
    def test_generate_simple_map(self):
        """Test generating a simple map."""
        map_data = self.map_generator.generate_simple_map(difficulty=1)
        
        # Check that the map has the correct dimensions
        self.assertEqual(map_data.width, 20)
        self.assertEqual(map_data.height, 15)
        
        # Check that the map contains obstacles, empty spaces, and destructible elements
        self.assertGreater(map_data.count_wall_cells(), 0)
        self.assertGreater(map_data.count_empty_cells(), 0)
        self.assertGreater(map_data.count_destructible_cells(), 0)
        
        # Check that the total number of cells is correct
        total_cells = (map_data.count_wall_cells() + 
                       map_data.count_empty_cells() + 
                       map_data.count_destructible_cells())
        self.assertEqual(total_cells, 20 * 15)
        
        # Check that the edges are walls
        for x in range(20):
            self.assertEqual(map_data.get_cell(x, 0), MapData.WALL)
            self.assertEqual(map_data.get_cell(x, 14), MapData.WALL)
        
        for y in range(15):
            self.assertEqual(map_data.get_cell(0, y), MapData.WALL)
            self.assertEqual(map_data.get_cell(19, y), MapData.WALL)
            
    def test_difficulty_affects_map(self):
        """Test that difficulty affects the map generation."""
        map_easy = self.map_generator.generate_map(difficulty=1)
        map_hard = self.map_generator.generate_map(difficulty=5)
        
        # Higher difficulty should have more destructible elements
        self.assertGreaterEqual(
            map_hard.count_destructible_cells(),
            map_easy.count_destructible_cells()
        )


if __name__ == '__main__':
    unittest.main()