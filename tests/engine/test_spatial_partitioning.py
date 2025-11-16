"""
Tests for the Spatial Partitioning module.
"""
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.engine.spatial_partitioning import SpatialGrid, OptimizedCollisionDetector


class MockGameObject:
    """Mock game object for testing."""
    
    def __init__(self, x, y, width=32, height=32):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = True
        
    def collides_with(self, other):
        """Simple AABB collision detection."""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)


class TestSpatialGrid(unittest.TestCase):
    """Test cases for the SpatialGrid class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.grid = SpatialGrid(800, 600, 64)
        
    def test_initialization(self):
        """Test spatial grid initialization."""
        self.assertEqual(self.grid.world_width, 800)
        self.assertEqual(self.grid.world_height, 600)
        self.assertEqual(self.grid.cell_size, 64)
        self.assertEqual(self.grid.grid_width, 13)  # ceil(800/64)
        self.assertEqual(self.grid.grid_height, 10)  # ceil(600/64)
        
    def test_grid_coords_conversion(self):
        """Test conversion from world coordinates to grid coordinates."""
        # Test corner cases
        self.assertEqual(self.grid._get_grid_coords(0, 0), (0, 0))
        self.assertEqual(self.grid._get_grid_coords(63, 63), (0, 0))
        self.assertEqual(self.grid._get_grid_coords(64, 64), (1, 1))
        self.assertEqual(self.grid._get_grid_coords(799, 599), (12, 9))
        
        # Test boundary clamping
        self.assertEqual(self.grid._get_grid_coords(-10, -10), (0, 0))
        self.assertEqual(self.grid._get_grid_coords(1000, 1000), (12, 9))
        
    def test_add_and_remove_object(self):
        """Test adding and removing objects from the grid."""
        obj = MockGameObject(100, 100)
        
        # Add object
        self.grid.add_object(obj)
        self.assertIn(id(obj), self.grid.objects)
        self.assertIn(id(obj), self.grid.object_cells)
        
        # Check that object is in the correct cell
        expected_cell = self.grid._get_grid_coords(100, 100)
        self.assertIn(expected_cell, self.grid.object_cells[id(obj)])
        
        # Remove object
        self.grid.remove_object(obj)
        self.assertNotIn(id(obj), self.grid.objects)
        self.assertNotIn(id(obj), self.grid.object_cells)
        
    def test_object_spanning_multiple_cells(self):
        """Test objects that span multiple grid cells."""
        # Create a large object that spans multiple cells
        obj = MockGameObject(60, 60, 80, 80)  # Spans from (60,60) to (140,140)
        
        self.grid.add_object(obj)
        
        # Object should be in multiple cells
        cells = self.grid.object_cells[id(obj)]
        self.assertGreater(len(cells), 1)
        
        # Should be in cells (0,0), (0,1), (1,0), (1,1), (2,0), (2,1), (0,2), (1,2), (2,2)
        expected_cells = {(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)}
        self.assertEqual(cells, expected_cells)
        
    def test_update_object_position(self):
        """Test updating an object's position in the grid."""
        obj = MockGameObject(100, 100)
        self.grid.add_object(obj)
        
        old_cells = self.grid.object_cells[id(obj)].copy()
        
        # Move object to a different cell
        obj.x = 200
        obj.y = 200
        self.grid.update_object(obj)
        
        new_cells = self.grid.object_cells[id(obj)]
        self.assertNotEqual(old_cells, new_cells)
        
        # Check that object is in the new correct cell
        expected_cell = self.grid._get_grid_coords(200, 200)
        self.assertIn(expected_cell, new_cells)
        
    def test_get_nearby_objects(self):
        """Test finding nearby objects."""
        obj1 = MockGameObject(100, 100)
        obj2 = MockGameObject(120, 120)  # Nearby
        obj3 = MockGameObject(500, 500)  # Far away
        
        self.grid.add_object(obj1)
        self.grid.add_object(obj2)
        self.grid.add_object(obj3)
        
        nearby = self.grid.get_nearby_objects(obj1)
        
        # obj2 should be nearby, obj3 should not
        self.assertIn(obj2, nearby)
        self.assertNotIn(obj3, nearby)
        self.assertNotIn(obj1, nearby)  # Object should not include itself
        
    def test_get_objects_in_region(self):
        """Test finding objects in a specific region."""
        obj1 = MockGameObject(50, 50)
        obj2 = MockGameObject(150, 150)
        obj3 = MockGameObject(250, 250)
        
        self.grid.add_object(obj1)
        self.grid.add_object(obj2)
        self.grid.add_object(obj3)
        
        # Get objects in region (0, 0, 200, 200)
        objects_in_region = self.grid.get_objects_in_region(0, 0, 200, 200)
        
        # obj1 and obj2 should be in region, obj3 should not
        self.assertIn(obj1, objects_in_region)
        self.assertIn(obj2, objects_in_region)
        self.assertNotIn(obj3, objects_in_region)
        
    def test_clear_grid(self):
        """Test clearing the grid."""
        obj1 = MockGameObject(100, 100)
        obj2 = MockGameObject(200, 200)
        
        self.grid.add_object(obj1)
        self.grid.add_object(obj2)
        
        self.assertEqual(len(self.grid.objects), 2)
        
        self.grid.clear()
        
        self.assertEqual(len(self.grid.objects), 0)
        self.assertEqual(len(self.grid.object_cells), 0)
        self.assertEqual(len(self.grid.grid), 0)
        
    def test_get_stats(self):
        """Test getting grid statistics."""
        obj1 = MockGameObject(100, 100)
        obj2 = MockGameObject(200, 200)
        
        self.grid.add_object(obj1)
        self.grid.add_object(obj2)
        
        stats = self.grid.get_stats()
        
        self.assertEqual(stats['total_objects'], 2)
        self.assertGreater(stats['occupied_cells'], 0)
        self.assertEqual(stats['total_cells'], 13 * 10)  # grid_width * grid_height
        self.assertGreater(stats['cell_utilization'], 0)
        self.assertGreater(stats['avg_objects_per_cell'], 0)


class TestOptimizedCollisionDetector(unittest.TestCase):
    """Test cases for the OptimizedCollisionDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = OptimizedCollisionDetector(800, 600, 64)
        
    def test_initialization(self):
        """Test collision detector initialization."""
        self.assertIsNotNone(self.detector.spatial_grid)
        self.assertEqual(self.detector.collision_pairs_checked, 0)
        
    def test_collision_detection_with_no_objects(self):
        """Test collision detection with no objects."""
        self.detector.update_objects([])
        collisions = self.detector.check_collisions()
        self.assertEqual(len(collisions), 0)
        
    def test_collision_detection_with_non_colliding_objects(self):
        """Test collision detection with objects that don't collide."""
        obj1 = MockGameObject(100, 100)
        obj2 = MockGameObject(500, 500)
        
        self.detector.update_objects([obj1, obj2])
        collisions = self.detector.check_collisions()
        
        self.assertEqual(len(collisions), 0)
        
    def test_collision_detection_with_colliding_objects(self):
        """Test collision detection with objects that do collide."""
        obj1 = MockGameObject(100, 100, 32, 32)
        obj2 = MockGameObject(120, 120, 32, 32)  # Overlapping
        
        self.detector.update_objects([obj1, obj2])
        collisions = self.detector.check_collisions()
        
        self.assertEqual(len(collisions), 1)
        self.assertIn((obj1, obj2), collisions)
        
    def test_performance_stats(self):
        """Test getting performance statistics."""
        obj1 = MockGameObject(100, 100)
        obj2 = MockGameObject(120, 120)
        obj3 = MockGameObject(500, 500)
        
        self.detector.update_objects([obj1, obj2, obj3])
        collisions = self.detector.check_collisions()
        
        stats = self.detector.get_performance_stats()
        
        self.assertIn('total_objects', stats)
        self.assertIn('collision_pairs_checked', stats)
        self.assertEqual(stats['total_objects'], 3)
        self.assertGreater(stats['collision_pairs_checked'], 0)
        
    def test_inactive_objects_ignored(self):
        """Test that inactive objects are ignored."""
        obj1 = MockGameObject(100, 100)
        obj2 = MockGameObject(120, 120)
        obj2.active = False  # Make object inactive
        
        self.detector.update_objects([obj1, obj2])
        collisions = self.detector.check_collisions()
        
        # Should be no collisions since obj2 is inactive
        self.assertEqual(len(collisions), 0)


if __name__ == '__main__':
    unittest.main()