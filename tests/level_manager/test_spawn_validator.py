"""
Unit tests for the SpawnValidator class.
"""
import unittest
import math
from src.level_manager.spawn_validator import SpawnValidator
from src.level_manager.map_data import MapData


class TestSpawnValidator(unittest.TestCase):
    """Test cases for the SpawnValidator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a 10x10 map for testing
        self.map_data = MapData(10, 10)
        self.map_data.set_cell_size(32)
        self.validator = SpawnValidator(self.map_data)
        
    def test_init(self):
        """Test SpawnValidator initialization."""
        self.assertEqual(self.validator.map_data, self.map_data)
        
    def test_is_within_bounds_valid_location(self):
        """Test _is_within_bounds with valid locations."""
        # Test center of map
        self.assertTrue(self.validator._is_within_bounds(160, 160, 32))
        
        # Test near edges but still valid
        self.assertTrue(self.validator._is_within_bounds(32, 32, 32))
        self.assertTrue(self.validator._is_within_bounds(288, 288, 32))
        
    def test_is_within_bounds_invalid_location(self):
        """Test _is_within_bounds with invalid locations."""
        # Test outside left edge
        self.assertFalse(self.validator._is_within_bounds(10, 160, 32))
        
        # Test outside top edge
        self.assertFalse(self.validator._is_within_bounds(160, 10, 32))
        
        # Test outside right edge
        self.assertFalse(self.validator._is_within_bounds(310, 160, 32))
        
        # Test outside bottom edge
        self.assertFalse(self.validator._is_within_bounds(160, 310, 32))
        
    def test_check_obstacle_collision_no_obstacles(self):
        """Test _check_obstacle_collision with no obstacles."""
        # Empty map should have no collisions
        self.assertFalse(self.validator._check_obstacle_collision(160, 160, 32, 1))
        
    def test_check_obstacle_collision_with_obstacles(self):
        """Test _check_obstacle_collision with obstacles."""
        # Place a wall at cell (5, 5)
        self.map_data.set_cell(5, 5, MapData.WALL)
        
        # Test collision at the obstacle location
        obstacle_x = 5 * 32 + 16  # Center of cell (5, 5)
        obstacle_y = 5 * 32 + 16
        self.assertTrue(self.validator._check_obstacle_collision(obstacle_x, obstacle_y, 32, 1))
        
        # Test no collision at a distance (use cell 2,2 which is far from obstacle at 5,5)
        self.assertFalse(self.validator._check_obstacle_collision(80, 80, 32, 1))
        
    def test_check_obstacle_collision_with_buffer(self):
        """Test _check_obstacle_collision with different buffer distances."""
        # Place a wall at cell (5, 5)
        self.map_data.set_cell(5, 5, MapData.WALL)
        
        obstacle_x = 5 * 32 + 16  # Center of cell (5, 5)
        obstacle_y = 5 * 32 + 16
        
        # Test with larger buffer - should detect collision from further away
        nearby_x = obstacle_x + 40  # Just over one cell away
        nearby_y = obstacle_y
        
        # With buffer of 1 cell, this should be a collision
        self.assertTrue(self.validator._check_obstacle_collision(nearby_x, nearby_y, 32, 1))
        
        # With no buffer, this should not be a collision
        self.assertFalse(self.validator._check_obstacle_collision(nearby_x, nearby_y, 32, 0))
        
    def test_has_maneuvering_space_open_area(self):
        """Test _has_maneuvering_space in an open area."""
        # Center of empty map should have maneuvering space
        self.assertTrue(self.validator._has_maneuvering_space(160, 160, 32))
        
    def test_has_maneuvering_space_blocked(self):
        """Test _has_maneuvering_space when blocked."""
        # Create a box of walls around position (3, 3)
        for x in range(2, 5):
            for y in range(2, 5):
                if x != 3 or y != 3:  # Don't block the center
                    self.map_data.set_cell(x, y, MapData.WALL)
                    
        # Position at center of box should not have enough maneuvering space
        center_x = 3 * 32 + 16
        center_y = 3 * 32 + 16
        self.assertFalse(self.validator._has_maneuvering_space(center_x, center_y, 32))
        
    def test_has_maneuvering_space_partial_blocking(self):
        """Test _has_maneuvering_space with partial blocking."""
        # Block two directions (up and right) from position (3, 3)
        self.map_data.set_cell(3, 2, MapData.WALL)  # Up
        self.map_data.set_cell(4, 3, MapData.WALL)  # Right
        
        # Should still have maneuvering space (down and left are clear)
        center_x = 3 * 32 + 16
        center_y = 3 * 32 + 16
        self.assertTrue(self.validator._has_maneuvering_space(center_x, center_y, 32))
        
    def test_is_location_valid_empty_map(self):
        """Test is_location_valid on an empty map."""
        # Center of empty map should be valid
        self.assertTrue(self.validator.is_location_valid(160, 160, 32, 1))
        
        # Near edges should be valid
        self.assertTrue(self.validator.is_location_valid(64, 64, 32, 1))
        
    def test_is_location_valid_with_obstacles(self):
        """Test is_location_valid with obstacles."""
        # Place obstacles
        self.map_data.set_cell(5, 5, MapData.WALL)
        self.map_data.set_cell(6, 5, MapData.ROCK_PILE)
        
        # Location at obstacle should be invalid
        obstacle_x = 5 * 32 + 16
        obstacle_y = 5 * 32 + 16
        self.assertFalse(self.validator.is_location_valid(obstacle_x, obstacle_y, 32, 1))
        
        # Location away from obstacles should be valid (use cell 2,2)
        self.assertTrue(self.validator.is_location_valid(80, 80, 32, 1))
        
    def test_is_location_valid_out_of_bounds(self):
        """Test is_location_valid with out-of-bounds locations."""
        # Test locations outside the map
        self.assertFalse(self.validator.is_location_valid(10, 160, 32, 1))
        self.assertFalse(self.validator.is_location_valid(160, 10, 32, 1))
        self.assertFalse(self.validator.is_location_valid(350, 160, 32, 1))
        self.assertFalse(self.validator.is_location_valid(160, 350, 32, 1))
        
    def test_find_valid_spawn_location_empty_map(self):
        """Test find_valid_spawn_location on an empty map."""
        location = self.validator.find_valid_spawn_location(32, 10, 1)
        
        # Should find a valid location
        self.assertIsNotNone(location)
        
        # Location should be valid
        x, y = location
        self.assertTrue(self.validator.is_location_valid(x, y, 32, 1))
        
    def test_find_valid_spawn_location_crowded_map(self):
        """Test find_valid_spawn_location on a crowded map."""
        # Fill most of the map with obstacles, leaving only a 4x4 area clear in the center
        for x in range(10):
            for y in range(10):
                if not (3 <= x <= 6 and 3 <= y <= 6):  # Leave 4x4 area clear
                    self.map_data.set_cell(x, y, MapData.WALL)
                    
        location = self.validator.find_valid_spawn_location(32, 50, 0)  # No buffer for crowded map
        
        # Should still find a valid location in the clear area
        self.assertIsNotNone(location)
        
        if location:
            x, y = location
            self.assertTrue(self.validator.is_location_valid(x, y, 32, 0))
            
    def test_find_valid_spawn_location_impossible(self):
        """Test find_valid_spawn_location when no valid location exists."""
        # Fill the entire map with obstacles
        for x in range(10):
            for y in range(10):
                self.map_data.set_cell(x, y, MapData.WALL)
                
        location = self.validator.find_valid_spawn_location(32, 10, 1)
        
        # Should not find a valid location
        self.assertIsNone(location)
        
    def test_find_valid_spawn_location_with_distance(self):
        """Test find_valid_spawn_location_with_distance."""
        # Test without distance constraint
        location1 = self.validator.find_valid_spawn_location_with_distance(32, 10, 1)
        self.assertIsNotNone(location1)
        
        # Test with distance constraint
        point = (160, 160)  # Center of map
        min_distance = 100
        
        location2 = self.validator.find_valid_spawn_location_with_distance(
            32, 50, 1, point, min_distance)
        
        if location2:
            x, y = location2
            distance = math.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
            self.assertGreaterEqual(distance, min_distance)
            
    def test_validate_existing_spawn_valid(self):
        """Test validate_existing_spawn with a valid location."""
        result = self.validator.validate_existing_spawn(160, 160, 32)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['issues']), 0)
        
    def test_validate_existing_spawn_invalid_bounds(self):
        """Test validate_existing_spawn with out-of-bounds location."""
        result = self.validator.validate_existing_spawn(10, 160, 32)
        
        self.assertFalse(result['valid'])
        self.assertIn('spawn_out_of_bounds', result['issues'])
        
    def test_validate_existing_spawn_invalid_obstacle(self):
        """Test validate_existing_spawn with obstacle collision."""
        # Place obstacle
        self.map_data.set_cell(5, 5, MapData.WALL)
        
        # Test at obstacle location
        obstacle_x = 5 * 32 + 16
        obstacle_y = 5 * 32 + 16
        result = self.validator.validate_existing_spawn(obstacle_x, obstacle_y, 32)
        
        self.assertFalse(result['valid'])
        self.assertIn('spawn_in_obstacle', result['issues'])
        
    def test_validate_existing_spawn_insufficient_space(self):
        """Test validate_existing_spawn with insufficient maneuvering space."""
        # Create a tight box around position (3, 3)
        for x in range(2, 5):
            for y in range(2, 5):
                if x != 3 or y != 3:
                    self.map_data.set_cell(x, y, MapData.WALL)
                    
        center_x = 3 * 32 + 16
        center_y = 3 * 32 + 16
        result = self.validator.validate_existing_spawn(center_x, center_y, 32)
        
        self.assertFalse(result['valid'])
        self.assertIn('insufficient_maneuvering_space', result['issues'])
        
    def test_different_tank_sizes(self):
        """Test spawn validation with different tank sizes."""
        # Test with smaller tank
        self.assertTrue(self.validator.is_location_valid(160, 160, 16, 1))
        
        # Test with larger tank
        self.assertTrue(self.validator.is_location_valid(160, 160, 64, 1))
        
        # Larger tank should be more restrictive near edges
        self.assertFalse(self.validator.is_location_valid(20, 20, 64, 1))
        
    def test_different_obstacle_types(self):
        """Test spawn validation with different obstacle types."""
        # Test with wall
        self.map_data.set_cell(5, 5, MapData.WALL)
        obstacle_x = 5 * 32 + 16
        obstacle_y = 5 * 32 + 16
        self.assertFalse(self.validator.is_location_valid(obstacle_x, obstacle_y, 32, 1))
        
        # Clear and test with rock pile
        self.map_data.set_cell(5, 5, MapData.EMPTY)
        self.map_data.set_cell(5, 5, MapData.ROCK_PILE)
        self.assertFalse(self.validator.is_location_valid(obstacle_x, obstacle_y, 32, 1))
        
        # Clear and test with petrol barrel
        self.map_data.set_cell(5, 5, MapData.EMPTY)
        self.map_data.set_cell(5, 5, MapData.PETROL_BARREL)
        self.assertFalse(self.validator.is_location_valid(obstacle_x, obstacle_y, 32, 1))


if __name__ == '__main__':
    unittest.main()