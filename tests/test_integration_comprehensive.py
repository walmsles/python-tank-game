"""
Comprehensive integration tests for the tank game.
Tests complete gameplay scenarios and feature interactions.
"""
import unittest
import pygame
import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.level_manager.level_manager import LevelManager
from src.level_manager.map_data import MapData
from src.level_manager.map_generator import MapGenerator
from src.engine.game_engine import GameEngine
from src.game_objects.player_tank import PlayerTank
from src.game_objects.enemy_tank import EnemyTank
from src.game_objects.projectile import Projectile
from src.game_objects.wall import Wall
from src.game_objects.rock_pile import RockPile
from src.game_objects.petrol_barrel import PetrolBarrel


class TestGameIntegration(unittest.TestCase):
    """Integration tests for complete game scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        
        # Create a game engine
        self.game_engine = GameEngine(width=640, height=480, title="Test Game Engine")
        self.game_engine.initialize()
        
        # Create a level manager
        self.level_manager = LevelManager(self.game_engine, map_width=20, map_height=15, max_level=10)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
        
    def test_complete_level_scenario(self):
        """Test a complete level from start to finish."""
        # Create and initialize player tank
        player_tank = PlayerTank(320, 240)
        self.level_manager.initialize(player_tank)
        
        # Start level 1
        self.level_manager.start_level(1)
        
        # Verify level setup
        self.assertEqual(self.level_manager.current_level, 1)
        self.assertIsNotNone(self.level_manager.player_tank)
        self.assertGreater(len([tank for tank in self.level_manager.enemy_tanks if tank is not None]), 0)
        self.assertIsNotNone(self.level_manager.map_data)
        
        # Simulate destroying all enemy tanks
        for enemy in self.level_manager.enemy_tanks[:]:
            if enemy is not None:
                enemy.take_damage(1000)  # Destroy enemy
        
        # Update level manager to check for completion
        self.level_manager.update(0.016)  # Simulate one frame update
        
        # Check level completion
        self.assertTrue(self.level_manager.is_level_complete())
        
    def test_map_generation_consistency(self):
        """Test that map generation produces consistent, valid maps."""
        generator = MapGenerator(20, 15)
        
        for difficulty in [1, 3, 5]:
            with self.subTest(difficulty=difficulty):
                map_data = generator.generate_map(difficulty)
                
                # Verify map properties
                self.assertEqual(map_data.width, 20)
                self.assertEqual(map_data.height, 15)
                
                # Count different cell types
                wall_count = map_data.count_cells(MapData.WALL)
                rock_count = map_data.count_cells(MapData.ROCK_PILE)
                barrel_count = map_data.count_cells(MapData.PETROL_BARREL)
                empty_count = map_data.count_cells(MapData.EMPTY)
                
                # Ensure sufficient open space
                total_cells = map_data.width * map_data.height
                open_space_ratio = empty_count / total_cells
                self.assertGreater(open_space_ratio, 0.4)  # At least 40% open space
                
                # Ensure some obstacles exist
                total_obstacles = wall_count + rock_count + barrel_count
                self.assertGreater(total_obstacles, 0)
                
    def test_projectile_collision_chain(self):
        """Test chain reactions with projectiles and destructible elements."""
        # Create a simple map with destructible elements
        map_data = MapData(10, 10)
        map_data.set_cell_size(32)
        
        # Create game objects
        petrol_barrel = PetrolBarrel(5 * 32, 5 * 32)
        rock_pile = RockPile(6 * 32, 5 * 32)
        player_tank = PlayerTank(1 * 32, 1 * 32)
        
        # Create projectile aimed at petrol barrel
        projectile = Projectile(
            x=petrol_barrel.x, y=petrol_barrel.y,
            direction=0,  # Moving right
            speed=200,
            damage=25,
            owner=player_tank
        )
        
        # Check collision and explosion
        if projectile.check_collision_with_object(petrol_barrel):
            destroyed = petrol_barrel.take_damage(projectile.damage)
            if destroyed:
                # Petrol barrel should explode
                explosion_data = petrol_barrel.get_explosion_data()
                self.assertIsNotNone(explosion_data)
                
                # Check if rock pile is in explosion radius
                if petrol_barrel.is_in_explosion_radius(rock_pile.x, rock_pile.y, rock_pile.width, rock_pile.height):
                    explosion_damage = petrol_barrel.calculate_explosion_damage(
                        rock_pile.x, rock_pile.y, rock_pile.width, rock_pile.height
                    )
                    rock_pile.take_damage(explosion_damage)
                    
                    # Verify rock pile took damage
                    self.assertLess(rock_pile.health, rock_pile.max_health)
                    
    def test_collision_system_integration(self):
        """Test collision system with multiple object types."""
        # Create test objects
        player_tank = PlayerTank(100, 100)
        wall = Wall(150, 150)
        rock_pile = RockPile(250, 250)
        petrol_barrel = PetrolBarrel(300, 300)
        
        # Test tank-obstacle collisions
        objects = [wall, rock_pile, petrol_barrel]
        
        for obj in objects:
            with self.subTest(obstacle=obj.__class__.__name__):
                # Position tank to overlap with obstacle
                old_x, old_y = player_tank.x, player_tank.y
                player_tank.x = obj.x + 5  # Slight overlap to ensure collision
                player_tank.y = obj.y + 5
                
                # Check collision detection
                collision = player_tank.check_collision_with_object(obj)
                
                # Active obstacles should block movement
                if obj.active and hasattr(obj, 'blocks_movement') and obj.blocks_movement():
                    self.assertTrue(collision)
                
                # Restore position
                player_tank.x, player_tank.y = old_x, old_y
                
    def test_game_state_persistence(self):
        """Test that game state is maintained correctly across operations."""
        # Create and initialize player tank
        player_tank = PlayerTank(320, 240)
        self.level_manager.initialize(player_tank)
        
        # Start game
        self.level_manager.start_level(1)
        initial_score = self.level_manager.score
        initial_level = self.level_manager.current_level
        
        # Simulate scoring
        self.level_manager.add_score(100)
        self.assertEqual(self.level_manager.score, initial_score + 100)
        
        # Simulate level completion
        for enemy in self.level_manager.enemy_tanks[:]:
            if enemy is not None:
                enemy.take_damage(1000)
        
        # Update level manager to check for completion
        self.level_manager.update(0.016)  # Simulate one frame update
        
        # Check level completion
        self.assertTrue(self.level_manager.is_level_complete())


if __name__ == '__main__':
    unittest.main()