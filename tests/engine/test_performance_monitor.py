"""
Tests for the Performance Monitor module.
"""
import unittest
import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.engine.performance_monitor import PerformanceMonitor, PerformanceProfiler


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for the PerformanceMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor(max_samples=10)
        
    def tearDown(self):
        """Clean up after tests."""
        self.monitor.cleanup()
        
    def test_initialization(self):
        """Test performance monitor initialization."""
        self.assertEqual(self.monitor.max_samples, 10)
        self.assertEqual(len(self.monitor.frame_times), 0)
        self.assertEqual(self.monitor.fps, 0.0)
        self.assertFalse(self.monitor.show_overlay)
        
    def test_frame_timing(self):
        """Test frame timing functionality."""
        # Simulate a few frames
        for i in range(5):
            self.monitor.start_frame()
            time.sleep(0.01)  # Simulate 10ms frame time
            
        # Check that frame times were recorded
        self.assertGreater(len(self.monitor.frame_times), 0)
        self.assertGreater(self.monitor.fps, 0)
        self.assertGreater(self.monitor.avg_frame_time, 0)
        
    def test_update_timing_recording(self):
        """Test recording of update times."""
        test_times = [0.001, 0.002, 0.003]
        
        for t in test_times:
            self.monitor.record_update_time(t)
            
        self.assertEqual(len(self.monitor.update_times), 3)
        self.assertEqual(list(self.monitor.update_times), test_times)
        
    def test_render_timing_recording(self):
        """Test recording of render times."""
        test_times = [0.005, 0.006, 0.007]
        
        for t in test_times:
            self.monitor.record_render_time(t)
            
        self.assertEqual(len(self.monitor.render_times), 3)
        self.assertEqual(list(self.monitor.render_times), test_times)
        
    def test_collision_timing_recording(self):
        """Test recording of collision detection times."""
        test_times = [0.0001, 0.0002, 0.0003]
        
        for t in test_times:
            self.monitor.record_collision_time(t)
            
        self.assertEqual(len(self.monitor.collision_times), 3)
        self.assertEqual(list(self.monitor.collision_times), test_times)
        
    def test_game_metrics_update(self):
        """Test updating game-specific metrics."""
        spatial_stats = {
            'total_objects': 50,
            'occupied_cells': 10,
            'cell_utilization': 0.2
        }
        
        self.monitor.update_game_metrics(
            object_count=25,
            collision_checks=100,
            spatial_grid_stats=spatial_stats
        )
        
        self.assertEqual(self.monitor.object_count, 25)
        self.assertEqual(self.monitor.collision_checks, 100)
        self.assertEqual(self.monitor.spatial_grid_stats, spatial_stats)
        
    def test_overlay_toggle(self):
        """Test toggling the performance overlay."""
        initial_state = self.monitor.show_overlay
        self.monitor.toggle_overlay()
        self.assertNotEqual(self.monitor.show_overlay, initial_state)
        
        self.monitor.toggle_overlay()
        self.assertEqual(self.monitor.show_overlay, initial_state)
        
    def test_performance_summary(self):
        """Test getting performance summary."""
        # Add some test data
        self.monitor.record_update_time(0.001)
        self.monitor.record_render_time(0.005)
        self.monitor.record_collision_time(0.0001)
        self.monitor.update_game_metrics(10, 50)
        
        summary = self.monitor.get_performance_summary()
        
        # Check that all expected keys are present
        expected_keys = [
            'fps', 'avg_frame_time_ms', 'min_frame_time_ms', 'max_frame_time_ms',
            'avg_update_time_ms', 'avg_render_time_ms', 'avg_collision_time_ms',
            'cpu_usage_percent', 'memory_usage_mb', 'memory_usage_percent',
            'object_count', 'collision_checks', 'spatial_grid_stats'
        ]
        
        for key in expected_keys:
            self.assertIn(key, summary)
            
        # Check specific values
        self.assertEqual(summary['object_count'], 10)
        self.assertEqual(summary['collision_checks'], 50)
        self.assertAlmostEqual(summary['avg_update_time_ms'], 1.0, places=1)
        self.assertAlmostEqual(summary['avg_render_time_ms'], 5.0, places=1)
        self.assertAlmostEqual(summary['avg_collision_time_ms'], 0.1, places=1)
        
    def test_max_samples_limit(self):
        """Test that sample collections respect the maximum size."""
        # Add more samples than the limit
        for i in range(15):
            self.monitor.record_update_time(0.001)
            
        # Should not exceed max_samples
        self.assertLessEqual(len(self.monitor.update_times), self.monitor.max_samples)
        
    def test_system_metrics_initialization(self):
        """Test that system metrics are initialized."""
        # Give the background thread a moment to start
        time.sleep(0.1)
        
        # System metrics should be numbers (may be 0 initially)
        self.assertIsInstance(self.monitor.cpu_usage, (int, float))
        self.assertIsInstance(self.monitor.memory_usage, (int, float))
        self.assertIsInstance(self.monitor.memory_usage_mb, (int, float))


class TestPerformanceProfiler(unittest.TestCase):
    """Test cases for the PerformanceProfiler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor()
        
    def tearDown(self):
        """Clean up after tests."""
        self.monitor.cleanup()
        
    def test_update_profiler(self):
        """Test profiling update operations."""
        with PerformanceProfiler(self.monitor, 'update'):
            time.sleep(0.01)  # Simulate 10ms update
            
        # Check that update time was recorded
        self.assertEqual(len(self.monitor.update_times), 1)
        self.assertGreater(self.monitor.update_times[0], 0.009)  # Should be around 10ms
        
    def test_render_profiler(self):
        """Test profiling render operations."""
        with PerformanceProfiler(self.monitor, 'render'):
            time.sleep(0.005)  # Simulate 5ms render
            
        # Check that render time was recorded
        self.assertEqual(len(self.monitor.render_times), 1)
        self.assertGreater(self.monitor.render_times[0], 0.004)  # Should be around 5ms
        
    def test_collision_profiler(self):
        """Test profiling collision detection operations."""
        with PerformanceProfiler(self.monitor, 'collision'):
            time.sleep(0.001)  # Simulate 1ms collision detection
            
        # Check that collision time was recorded
        self.assertEqual(len(self.monitor.collision_times), 1)
        self.assertGreater(self.monitor.collision_times[0], 0.0009)  # Should be around 1ms
        
    def test_profiler_exception_handling(self):
        """Test that profiler handles exceptions properly."""
        try:
            with PerformanceProfiler(self.monitor, 'update'):
                time.sleep(0.001)
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected
            
        # Time should still be recorded despite the exception
        self.assertEqual(len(self.monitor.update_times), 1)
        self.assertGreater(self.monitor.update_times[0], 0)
        
    def test_nested_profilers(self):
        """Test nested profiler usage."""
        with PerformanceProfiler(self.monitor, 'update'):
            time.sleep(0.002)
            with PerformanceProfiler(self.monitor, 'collision'):
                time.sleep(0.001)
            time.sleep(0.002)
            
        # Both times should be recorded
        self.assertEqual(len(self.monitor.update_times), 1)
        self.assertEqual(len(self.monitor.collision_times), 1)
        
        # Update time should be longer than collision time
        self.assertGreater(self.monitor.update_times[0], self.monitor.collision_times[0])


if __name__ == '__main__':
    unittest.main()