"""
Unit tests for the MapData class.
"""
import unittest
from src.level_manager.map_data import MapData


class TestMapData(unittest.TestCase):
    """Test cases for the MapData class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.map_data = MapData(10, 8)
        
    def test_initialization(self):
        """Test that the map is initialized correctly."""
        self.assertEqual(self.map_data.width, 10)
        self.assertEqual(self.map_data.height, 8)
        self.assertEqual(len(self.map_data.grid), 8)
        self.assertEqual(len(self.map_data.grid[0]), 10)
        
    def test_set_get_cell(self):
        """Test setting and getting cell values."""
        self.map_data.set_cell(3, 4, MapData.WALL)
        self.assertEqual(self.map_data.get_cell(3, 4), MapData.WALL)
        
        self.map_data.set_cell(5, 6, MapData.ROCK_PILE)
        self.assertEqual(self.map_data.get_cell(5, 6), MapData.ROCK_PILE)
        
        self.map_data.set_cell(7, 2, MapData.PETROL_BARREL)
        self.assertEqual(self.map_data.get_cell(7, 2), MapData.PETROL_BARREL)
        
    def test_is_wall_at(self):
        """Test checking if a cell is a wall."""
        self.map_data.set_cell(3, 4, MapData.WALL)
        self.assertTrue(self.map_data.is_wall_at(3, 4))
        self.assertFalse(self.map_data.is_wall_at(5, 6))
        
    def test_is_obstacle_at(self):
        """Test checking if a cell is an obstacle."""
        self.map_data.set_cell(3, 4, MapData.WALL)
        self.map_data.set_cell(5, 6, MapData.ROCK_PILE)
        self.map_data.set_cell(7, 2, MapData.PETROL_BARREL)
        
        self.assertTrue(self.map_data.is_obstacle_at(3, 4))
        self.assertTrue(self.map_data.is_obstacle_at(5, 6))
        self.assertTrue(self.map_data.is_obstacle_at(7, 2))
        self.assertFalse(self.map_data.is_obstacle_at(1, 1))
        
    def test_is_rock_pile_at(self):
        """Test checking if a cell is a rock pile."""
        self.map_data.set_cell(5, 6, MapData.ROCK_PILE)
        self.assertTrue(self.map_data.is_rock_pile_at(5, 6))
        self.assertFalse(self.map_data.is_rock_pile_at(3, 4))
        
    def test_is_petrol_barrel_at(self):
        """Test checking if a cell is a petrol barrel."""
        self.map_data.set_cell(7, 2, MapData.PETROL_BARREL)
        self.assertTrue(self.map_data.is_petrol_barrel_at(7, 2))
        self.assertFalse(self.map_data.is_petrol_barrel_at(3, 4))
        
    def test_is_destructible_at(self):
        """Test checking if a cell is destructible."""
        self.map_data.set_cell(5, 6, MapData.ROCK_PILE)
        self.map_data.set_cell(7, 2, MapData.PETROL_BARREL)
        self.map_data.set_cell(3, 4, MapData.WALL)
        
        self.assertTrue(self.map_data.is_destructible_at(5, 6))
        self.assertTrue(self.map_data.is_destructible_at(7, 2))
        self.assertFalse(self.map_data.is_destructible_at(3, 4))
        
    def test_is_empty_at(self):
        """Test checking if a cell is empty."""
        self.assertTrue(self.map_data.is_empty_at(1, 1))
        self.map_data.set_cell(1, 1, MapData.WALL)
        self.assertFalse(self.map_data.is_empty_at(1, 1))
        
    def test_clear(self):
        """Test clearing the map."""
        self.map_data.set_cell(3, 4, MapData.WALL)
        self.map_data.set_cell(5, 6, MapData.ROCK_PILE)
        self.map_data.set_cell(7, 2, MapData.PETROL_BARREL)
        self.map_data.clear()
        self.assertTrue(self.map_data.is_empty_at(3, 4))
        self.assertTrue(self.map_data.is_empty_at(5, 6))
        self.assertTrue(self.map_data.is_empty_at(7, 2))
        
    def test_count_cells(self):
        """Test counting cells of different types."""
        self.map_data.clear()
        self.assertEqual(self.map_data.count_empty_cells(), 10 * 8)
        self.assertEqual(self.map_data.count_wall_cells(), 0)
        self.assertEqual(self.map_data.count_obstacle_cells(), 0)
        self.assertEqual(self.map_data.count_rock_pile_cells(), 0)
        self.assertEqual(self.map_data.count_petrol_barrel_cells(), 0)
        self.assertEqual(self.map_data.count_destructible_cells(), 0)
        
        self.map_data.set_cell(3, 4, MapData.WALL)
        self.map_data.set_cell(5, 6, MapData.ROCK_PILE)
        self.map_data.set_cell(7, 2, MapData.PETROL_BARREL)
        
        self.assertEqual(self.map_data.count_empty_cells(), 10 * 8 - 3)
        self.assertEqual(self.map_data.count_wall_cells(), 1)
        self.assertEqual(self.map_data.count_obstacle_cells(), 3)
        self.assertEqual(self.map_data.count_rock_pile_cells(), 1)
        self.assertEqual(self.map_data.count_petrol_barrel_cells(), 1)
        self.assertEqual(self.map_data.count_destructible_cells(), 2)
        
    def test_pixel_conversion(self):
        """Test conversion between cell and pixel coordinates."""
        self.map_data.set_cell_size(32)
        
        # Test cell to pixel
        pixel_x, pixel_y = self.map_data.get_pixel_position(3, 4)
        self.assertEqual(pixel_x, 3 * 32)
        self.assertEqual(pixel_y, 4 * 32)
        
        # Test pixel to cell
        cell_x, cell_y = self.map_data.get_cell_from_pixel(100, 150)
        self.assertEqual(cell_x, 100 // 32)
        self.assertEqual(cell_y, 150 // 32)
        
    def test_out_of_bounds(self):
        """Test handling of out-of-bounds coordinates."""
        # Out of bounds should be treated as walls/obstacles
        self.assertEqual(self.map_data.get_cell(-1, 0), MapData.WALL)
        self.assertEqual(self.map_data.get_cell(0, -1), MapData.WALL)
        self.assertEqual(self.map_data.get_cell(10, 0), MapData.WALL)
        self.assertEqual(self.map_data.get_cell(0, 8), MapData.WALL)


if __name__ == '__main__':
    unittest.main()