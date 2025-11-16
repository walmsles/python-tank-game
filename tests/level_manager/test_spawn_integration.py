"""
Tests for spawn validation integration with tank spawning.
"""
import unittest
from unittest.mock import Mock, MagicMock
from src.level_manager.level_manager import LevelManager
from src.level_manager.enemy_tank_spawner import EnemyTankSpawner
from src.level_manager.map_data import MapData
from src.game_objects.player_tank import PlayerTank


class TestSpawnIntegration(unittest.TestCase):
    """Test spawn validation integration with tank spawning."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock game engine
        self.game_engine = Mock()
        self.game_engine.add_game_object = Mock()
        self.game_engine.remove_game_object = Mock()
        
        # Create a player tank
        self.player_tank = PlayerTank(400, 300)
        
        # Create a level manager
        self.level_manager = LevelManager(self.game_engine, map_width=25, map_height=19)
        
        # Create a simple map data for testing
        self.map_data = MapData(25, 19)
        self.map_data.set_cell_size(32)
        
        # Fill the map with mostly empty space
        for y in range(19):
            for x in range(25):
                self.map_data.set_cell(x, y, 0)  # Empty
        
        # Add some obstacles for testing
        self.map_data.set_cell(5, 5, 1)  # Wall
        self.map_data.set_cell(10, 10, 2)  # Rock pile
        self.map_data.set_cell(15, 15, 3)  # Petrol barrel
    
    def test_player_tank_spawn_validation(self):
        """Test that player tank uses spawn validation."""
        # Initialize the level manager with the player tank
        self.level_manager.initialize(self.player_tank)
        
        # Check that the player tank was positioned
        self.assertIsNotNone(self.player_tank.x)
        self.assertIsNotNone(self.player_tank.y)
        
        # Check that the position is within map bounds
        self.assertGreaterEqual(self.player_tank.x, 0)
        self.assertGreaterEqual(self.player_tank.y, 0)
        self.assertLess(self.player_tank.x, self.map_data.width * self.map_data.cell_size)
        self.assertLess(self.player_tank.y, self.map_data.height * self.map_data.cell_size)
    
    def test_enemy_tank_spawn_validation(self):
        """Test that enemy tanks use spawn validation."""
        # Create an enemy tank spawner
        spawner = EnemyTankSpawner(self.map_data)
        
        # Mock the game engine
        game_engine = Mock()
        game_engine.add_game_object = Mock()
        
        # Spawn enemy tanks
        player_position = (400, 300)
        enemy_tanks = spawner.spawn_enemy_tanks(1, player_position, game_engine)
        
        # Check that at least one enemy tank was spawned
        self.assertGreater(len(enemy_tanks), 0)
        
        # Check that all spawned tanks have valid positions
        for tank in enemy_tanks:
            self.assertIsNotNone(tank.x)
            self.assertIsNotNone(tank.y)
            
            # Check that the position is within map bounds
            self.assertGreaterEqual(tank.x, 0)
            self.assertGreaterEqual(tank.y, 0)
            self.assertLess(tank.x, self.map_data.width * self.map_data.cell_size)
            self.assertLess(tank.y, self.map_data.height * self.map_data.cell_size)
    
    def test_spawn_validation_with_obstacles(self):
        """Test spawn validation works correctly with obstacles."""
        # Create a map with many obstacles
        obstacle_map = MapData(10, 10)
        obstacle_map.set_cell_size(32)
        
        # Fill most of the map with obstacles, leaving some empty spaces
        for y in range(10):
            for x in range(10):
                if (x + y) % 3 == 0:  # Create a pattern of obstacles
                    obstacle_map.set_cell(x, y, 1)  # Wall
                else:
                    obstacle_map.set_cell(x, y, 0)  # Empty
        
        # Create spawner with the obstacle-heavy map
        spawner = EnemyTankSpawner(obstacle_map)
        
        # Mock the game engine
        game_engine = Mock()
        game_engine.add_game_object = Mock()
        
        # Try to spawn enemy tanks
        player_position = (160, 160)  # Center of the map
        enemy_tanks = spawner.spawn_enemy_tanks(1, player_position, game_engine)
        
        # Check that tanks were spawned (or at least attempted)
        # Even if no valid positions are found, the method should handle it gracefully
        self.assertIsInstance(enemy_tanks, list)
        
        # If tanks were spawned, they should be in valid positions
        for tank in enemy_tanks:
            # Convert tank position to cell coordinates
            cell_x = int(tank.x // obstacle_map.cell_size)
            cell_y = int(tank.y // obstacle_map.cell_size)
            
            # Check that the tank is not spawned on an obstacle
            self.assertEqual(obstacle_map.get_cell(cell_x, cell_y), 0)
    
    def test_spawn_validation_error_handling(self):
        """Test error handling when no valid spawn locations are found."""
        # Create a map filled with obstacles
        blocked_map = MapData(5, 5)
        blocked_map.set_cell_size(32)
        
        # Fill the entire map with obstacles
        for y in range(5):
            for x in range(5):
                blocked_map.set_cell(x, y, 1)  # Wall
        
        # Create spawner with the blocked map
        spawner = EnemyTankSpawner(blocked_map)
        
        # Mock the game engine
        game_engine = Mock()
        game_engine.add_game_object = Mock()
        
        # Try to spawn enemy tanks (should fail gracefully)
        player_position = (80, 80)
        enemy_tanks = spawner.spawn_enemy_tanks(1, player_position, game_engine)
        
        # Should return an empty list when no valid positions are found
        self.assertEqual(len(enemy_tanks), 0)
    
    def test_single_enemy_tank_spawn_validation(self):
        """Test spawn validation for single enemy tank spawning."""
        # Create spawner
        spawner = EnemyTankSpawner(self.map_data)
        
        # Mock the game engine
        game_engine = Mock()
        game_engine.add_game_object = Mock()
        
        # Spawn a single enemy tank
        player_position = (400, 300)
        enemy_tank = spawner.spawn_single_enemy_tank(1, player_position, game_engine)
        
        if enemy_tank:  # If a tank was spawned
            # Check that it has a valid position
            self.assertIsNotNone(enemy_tank.x)
            self.assertIsNotNone(enemy_tank.y)
            
            # Check that the position is within map bounds
            self.assertGreaterEqual(enemy_tank.x, 0)
            self.assertGreaterEqual(enemy_tank.y, 0)
            self.assertLess(enemy_tank.x, self.map_data.width * self.map_data.cell_size)
            self.assertLess(enemy_tank.y, self.map_data.height * self.map_data.cell_size)
            
            # Check that it was added to the game engine
            game_engine.add_game_object.assert_called_once_with(enemy_tank)
    
    def test_level_manager_spawn_enemy_tank_validation(self):
        """Test that LevelManager's spawn_enemy_tank method uses validation."""
        # Set up the level manager with a map
        self.level_manager.map_data = self.map_data
        self.level_manager.player_tank = self.player_tank
        
        # Spawn an enemy tank through the level manager
        enemy_tank = self.level_manager.spawn_enemy_tank(difficulty=1)
        
        if enemy_tank:  # If a tank was spawned
            # Check that it has a valid position
            self.assertIsNotNone(enemy_tank.x)
            self.assertIsNotNone(enemy_tank.y)
            
            # Check that the position is within map bounds
            self.assertGreaterEqual(enemy_tank.x, 0)
            self.assertGreaterEqual(enemy_tank.y, 0)
            self.assertLess(enemy_tank.x, self.map_data.width * self.map_data.cell_size)
            self.assertLess(enemy_tank.y, self.map_data.height * self.map_data.cell_size)


if __name__ == '__main__':
    unittest.main()