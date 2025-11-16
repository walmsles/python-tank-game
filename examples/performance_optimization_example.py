"""
Performance Optimization Example for the Tank Game.
This example demonstrates the performance improvements from spatial partitioning,
optimized rendering, and performance monitoring.
"""
import sys
import os
import time
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.game_engine import GameEngine
from src.game_objects.player_tank import PlayerTank
from src.game_objects.enemy_tank import EnemyTank
from src.game_objects.projectile import Projectile
from src.level_manager.map_data import MapData
from src.level_manager.map_generator import MapGenerator


class PerformanceTestObject:
    """Simple test object for performance testing."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.active = True
        self.velocity_x = random.uniform(-50, 50)
        self.velocity_y = random.uniform(-50, 50)
        self.sprite = None
        
    def update(self, delta_time):
        """Update the test object position."""
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        
        # Bounce off screen edges
        if self.x < 0 or self.x > 800 - self.width:
            self.velocity_x = -self.velocity_x
            self.x = max(0, min(800 - self.width, self.x))
            
        if self.y < 0 or self.y > 600 - self.height:
            self.velocity_y = -self.velocity_y
            self.y = max(0, min(600 - self.height, self.y))
            
    def collides_with(self, other):
        """Simple AABB collision detection."""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
                
    def render(self, screen):
        """Render the test object."""
        import pygame
        color = (255, 255, 255)
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))


def run_performance_test():
    """Run a performance test comparing optimized vs unoptimized collision detection."""
    print("Tank Game Performance Optimization Demo")
    print("=" * 50)
    
    # Create game engine
    engine = GameEngine(width=800, height=600, title="Performance Test", target_fps=60)
    engine.initialize()
    
    # Create test objects
    test_objects = []
    num_objects = 100  # Start with 100 objects
    
    print(f"Creating {num_objects} test objects...")
    for i in range(num_objects):
        x = random.randint(0, 800 - 16)
        y = random.randint(0, 600 - 16)
        test_objects.append(PerformanceTestObject(x, y))
        engine.add_game_object(test_objects[-1])
    
    # Test with spatial partitioning enabled
    print("\nTesting with spatial partitioning ENABLED...")
    engine.set_performance_options(spatial_partitioning=True, performance_monitoring=True)
    
    # Run for a few seconds to collect metrics
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 3.0 and engine.running:
        engine.handle_events()
        engine.update()
        engine.render()
        frame_count += 1
        
    optimized_stats = engine.get_performance_summary()
    
    print(f"Optimized Results ({frame_count} frames):")
    print(f"  Average FPS: {optimized_stats['fps']:.1f}")
    print(f"  Average Frame Time: {optimized_stats['avg_frame_time_ms']:.2f}ms")
    print(f"  Collision Checks: {optimized_stats['collision_checks']}")
    print(f"  Objects Rendered: {optimized_stats.get('objects_rendered', 'N/A')}")
    print(f"  Objects Culled: {optimized_stats.get('objects_culled', 'N/A')}")
    
    # Test with spatial partitioning disabled
    print("\nTesting with spatial partitioning DISABLED...")
    engine.set_performance_options(spatial_partitioning=False)
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 3.0 and engine.running:
        engine.handle_events()
        engine.update()
        engine.render()
        frame_count += 1
        
    unoptimized_stats = engine.get_performance_summary()
    
    print(f"Unoptimized Results ({frame_count} frames):")
    print(f"  Average FPS: {unoptimized_stats['fps']:.1f}")
    print(f"  Average Frame Time: {unoptimized_stats['avg_frame_time_ms']:.2f}ms")
    print(f"  Collision Checks: {unoptimized_stats['collision_checks']}")
    
    # Calculate improvement
    if unoptimized_stats['fps'] > 0:
        fps_improvement = (optimized_stats['fps'] / unoptimized_stats['fps'] - 1) * 100
        print(f"\nPerformance Improvement:")
        print(f"  FPS Improvement: {fps_improvement:+.1f}%")
        
        if optimized_stats['collision_checks'] > 0 and unoptimized_stats['collision_checks'] > 0:
            collision_reduction = (1 - optimized_stats['collision_checks'] / unoptimized_stats['collision_checks']) * 100
            print(f"  Collision Check Reduction: {collision_reduction:.1f}%")
    
    print("\nControls during demo:")
    print("  F1: Toggle performance overlay")
    print("  F2: Toggle spatial partitioning")
    print("  F3: Toggle viewport culling")
    print("  F4: Toggle render batching")
    print("  F5: Print performance summary")
    print("  ESC: Exit")
    
    # Continue running for interactive testing
    print("\nDemo running... Press ESC to exit or use F-keys to toggle optimizations.")
    engine.set_performance_options(spatial_partitioning=True)  # Re-enable for demo
    
    while engine.running:
        engine.handle_events()
        engine.update()
        engine.render()
        
    engine.cleanup()


def run_tank_performance_demo():
    """Run a performance demo with actual tank game objects."""
    print("\nTank Game Performance Demo with Real Objects")
    print("=" * 50)
    
    engine = GameEngine(width=800, height=600, title="Tank Performance Demo", target_fps=60)
    engine.initialize()
    
    # Create a simple map
    map_generator = MapGenerator(25, 19)  # 800x600 with 32x32 cells
    map_data = map_generator.generate_map(difficulty=1)
    
    # Create player tank
    player_tank = PlayerTank(400, 300, health=100, speed=5)
    engine.add_game_object(player_tank)
    
    # Create multiple enemy tanks for performance testing
    enemy_tanks = []
    for i in range(10):  # 10 enemy tanks
        x = random.randint(50, 750)
        y = random.randint(50, 550)
        enemy_tank = EnemyTank(x, y, health=50, speed=3, difficulty=1)
        enemy_tanks.append(enemy_tank)
        engine.add_game_object(enemy_tank)
    
    # Create some projectiles
    projectiles = []
    for i in range(20):  # 20 projectiles
        x = random.randint(0, 800)
        y = random.randint(0, 600)
        direction = random.randint(0, 360)
        projectile = Projectile(x, y, direction, speed=200, damage=25, owner=None)
        projectiles.append(projectile)
        engine.add_game_object(projectile)
    
    print(f"Created {len(enemy_tanks)} enemy tanks and {len(projectiles)} projectiles")
    print("Performance monitoring enabled - press F1 to show overlay")
    
    # Enable performance monitoring
    engine.set_performance_options(performance_monitoring=True)
    
    # Run the demo
    while engine.running:
        engine.handle_events()
        engine.update()
        engine.render()
        
    engine.cleanup()


if __name__ == "__main__":
    try:
        # Run basic performance test
        run_performance_test()
        
        # Run tank-specific performance demo
        run_tank_performance_demo()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Error running performance demo: {e}")
        import traceback
        traceback.print_exc()