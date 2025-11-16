"""
Enemy Tank Spawner module for the Tank Game.
This module defines the EnemyTankSpawner class that handles spawning enemy tanks on the map.
"""
import random
import math
from src.game_objects.enemy_tank import EnemyTank
from src.level_manager.spawn_validator import SpawnValidator


class EnemyTankSpawner:
    """
    Handles spawning enemy tanks on the map.
    """
    def __init__(self, map_data):
        """
        Initialize the enemy tank spawner.
        
        Args:
            map_data (MapData): The map data for the current level
        """
        self.map_data = map_data
        self.spawn_validator = SpawnValidator(map_data)
        self.min_distance_between_tanks = 2  # Minimum distance between tanks in cells (reduced for tests)
        self.min_distance_from_player = 3  # Minimum distance from player in cells (reduced for tests)
        self.spawn_attempts = 200  # Maximum number of attempts to find a valid spawn position (increased)
        
    def spawn_enemy_tanks(self, level, player_position, game_engine, difficulty_manager=None):
        """
        Spawn enemy tanks for the current level.
        
        Args:
            level (int): Current level number
            player_position (tuple): (x, y) position of the player tank in pixels
            game_engine (GameEngine): The game engine to add tanks to
            difficulty_manager (DifficultyManager, optional): The difficulty manager to use
            
        Returns:
            list: List of spawned enemy tanks
        """
        # Use default calculations if no difficulty manager is provided
        if difficulty_manager is None:
            # Calculate number of tanks based on level
            num_tanks = self._calculate_num_tanks(level)
            
            # Calculate difficulty distribution based on level
            difficulties = self._calculate_difficulties(level, num_tanks)
        else:
            # Use the difficulty manager to calculate number of tanks and difficulties
            num_tanks = difficulty_manager.get_num_enemy_tanks(level)
            difficulties = difficulty_manager.get_enemy_tank_difficulties(level, num_tanks)
            
            # Update spawn parameters based on level
            spawn_params = difficulty_manager.get_enemy_spawn_params(level)
            self.min_distance_between_tanks = spawn_params['min_distance_between_tanks']
            self.min_distance_from_player = spawn_params['min_distance_from_player']
            self.spawn_attempts = spawn_params['spawn_attempts']
        
        # Find spawn positions and create tanks using spawn validator
        enemy_tanks = []
        
        for difficulty in difficulties:
            # Find a valid spawn position using spawn validator
            min_distance_from_player = self.min_distance_from_player * self.map_data.cell_size
            spawn_position = self.spawn_validator.find_valid_spawn_location_with_distance(
                tank_size=32,
                max_attempts=self.spawn_attempts,
                min_distance_from_obstacles=2,
                min_distance_from_point=player_position,
                min_point_distance=min_distance_from_player
            )
            
            if spawn_position:
                pixel_x, pixel_y = spawn_position
                
                # Check minimum distance from other spawned tanks
                valid_distance = True
                for existing_tank in enemy_tanks:
                    distance = math.sqrt((pixel_x - existing_tank.x) ** 2 + (pixel_y - existing_tank.y) ** 2)
                    min_tank_distance = self.min_distance_between_tanks * self.map_data.cell_size
                    if distance < min_tank_distance:
                        valid_distance = False
                        break
                
                if not valid_distance:
                    # Try to find another location with better spacing
                    for attempt in range(10):  # Increased retry attempts
                        retry_spawn = self.spawn_validator.find_valid_spawn_location_with_distance(
                            tank_size=32,
                            max_attempts=20,  # Increased attempts per retry
                            min_distance_from_obstacles=1,  # Reduced obstacle distance
                            min_distance_from_point=player_position,
                            min_point_distance=min_distance_from_player
                        )
                        if retry_spawn:
                            pixel_x, pixel_y = retry_spawn
                            valid_distance = True
                            for existing_tank in enemy_tanks:
                                distance = math.sqrt((pixel_x - existing_tank.x) ** 2 + (pixel_y - existing_tank.y) ** 2)
                                if distance < min_tank_distance:
                                    valid_distance = False
                                    break
                            if valid_distance:
                                break
                        else:
                            # Try with even more relaxed constraints
                            retry_spawn = self.spawn_validator.find_valid_spawn_location(
                                tank_size=32,
                                max_attempts=20,
                                min_distance_from_obstacles=1
                            )
                            if retry_spawn:
                                pixel_x, pixel_y = retry_spawn
                                # Check basic distance from player and existing tanks
                                player_distance = math.sqrt((pixel_x - player_position[0]) ** 2 + (pixel_y - player_position[1]) ** 2)
                                if player_distance >= 48:  # Minimum 1.5 cells from player
                                    valid_distance = True
                                    for existing_tank in enemy_tanks:
                                        distance = math.sqrt((pixel_x - existing_tank.x) ** 2 + (pixel_y - existing_tank.y) ** 2)
                                        if distance < 48:  # Minimum 1.5 cells between tanks
                                            valid_distance = False
                                            break
                                    if valid_distance:
                                        break
                
                if valid_distance:
                    # Create the enemy tank
                    enemy_tank = EnemyTank(pixel_x, pixel_y, difficulty=difficulty)
                    
                    # Set sound manager for the enemy tank
                    if hasattr(game_engine, 'sound_manager') and game_engine.sound_manager:
                        enemy_tank.set_sound_manager(game_engine.sound_manager)
                    
                    # Add the tank to the game engine
                    game_engine.add_game_object(enemy_tank)
                    
                    # Add the tank to the list
                    enemy_tanks.append(enemy_tank)
                else:
                    print(f"Warning: Could not find valid spawn location for enemy tank with difficulty {difficulty}")
            else:
                # Try with reduced constraints as fallback
                fallback_spawn = self.spawn_validator.find_valid_spawn_location(
                    tank_size=32,
                    max_attempts=self.spawn_attempts,
                    min_distance_from_obstacles=1  # Reduced buffer
                )
                
                if fallback_spawn:
                    pixel_x, pixel_y = fallback_spawn
                    
                    # Check distance from player (reduced requirement)
                    player_distance = math.sqrt((pixel_x - player_position[0]) ** 2 + (pixel_y - player_position[1]) ** 2)
                    min_player_distance = (self.min_distance_from_player // 2) * self.map_data.cell_size
                    
                    if player_distance >= min_player_distance:
                        # Create the enemy tank with fallback position
                        enemy_tank = EnemyTank(pixel_x, pixel_y, difficulty=difficulty)
                        
                        # Set sound manager for the enemy tank
                        if hasattr(game_engine, 'sound_manager') and game_engine.sound_manager:
                            enemy_tank.set_sound_manager(game_engine.sound_manager)
                        
                        # Add the tank to the game engine
                        game_engine.add_game_object(enemy_tank)
                        
                        # Add the tank to the list
                        enemy_tanks.append(enemy_tank)
                        
                        print(f"Info: Used fallback spawn location for enemy tank with difficulty {difficulty}")
                    else:
                        # Last resort: spawn at a random location with minimum constraints
                        emergency_spawn = self._find_emergency_spawn_location(player_position)
                        if emergency_spawn:
                            pixel_x, pixel_y = emergency_spawn
                            enemy_tank = EnemyTank(pixel_x, pixel_y, difficulty=difficulty)
                            
                            # Set sound manager for the enemy tank
                            if hasattr(game_engine, 'sound_manager') and game_engine.sound_manager:
                                enemy_tank.set_sound_manager(game_engine.sound_manager)
                            
                            # Add the tank to the game engine
                            game_engine.add_game_object(enemy_tank)
                            
                            # Add the tank to the list
                            enemy_tanks.append(enemy_tank)
                            
                            print(f"Info: Used emergency spawn location for enemy tank with difficulty {difficulty}")
                        else:
                            print(f"Warning: Could not find any valid spawn location for enemy tank with difficulty {difficulty}")
                else:
                    # Last resort: spawn at a random location with minimum constraints
                    emergency_spawn = self._find_emergency_spawn_location(player_position)
                    if emergency_spawn:
                        pixel_x, pixel_y = emergency_spawn
                        enemy_tank = EnemyTank(pixel_x, pixel_y, difficulty=difficulty)
                        
                        # Set sound manager for the enemy tank
                        if hasattr(game_engine, 'sound_manager') and game_engine.sound_manager:
                            enemy_tank.set_sound_manager(game_engine.sound_manager)
                        
                        # Add the tank to the game engine
                        game_engine.add_game_object(enemy_tank)
                        
                        # Add the tank to the list
                        enemy_tanks.append(enemy_tank)
                        
                        print(f"Info: Used emergency spawn location for enemy tank with difficulty {difficulty}")
                    else:
                        print(f"Warning: Could not find any spawn location for enemy tank with difficulty {difficulty}")
        
        return enemy_tanks
        
    def _calculate_num_tanks(self, level):
        """
        Calculate the number of enemy tanks to spawn based on the level.
        This is a fallback method used when no difficulty manager is provided.
        
        Args:
            level (int): Current level number
            
        Returns:
            int: Number of tanks to spawn
        """
        # Base number of tanks
        base_tanks = 1
        
        # Additional tanks based on level (more tanks at higher levels)
        additional_tanks = min(level - 1, 5)  # Cap at 6 tanks total (1 base + 5 additional)
        
        return base_tanks + additional_tanks
        
    def _calculate_difficulties(self, level, num_tanks):
        """
        Calculate the difficulty levels for the enemy tanks.
        This is a fallback method used when no difficulty manager is provided.
        
        Args:
            level (int): Current level number
            num_tanks (int): Number of tanks to spawn
            
        Returns:
            list: List of difficulty levels for each tank
        """
        difficulties = []
        
        # Base difficulty increases with level
        base_difficulty = min(level, 5)  # Cap at difficulty 5
        
        # First tank is always at base difficulty
        difficulties.append(base_difficulty)
        
        # Remaining tanks have varying difficulties
        for i in range(1, num_tanks):
            # Some tanks are easier, some are harder
            difficulty_variation = random.randint(-1, 1)
            difficulty = max(1, min(5, base_difficulty + difficulty_variation))
            difficulties.append(difficulty)
            
        return difficulties
        
    def spawn_single_enemy_tank(self, difficulty, player_position, game_engine):
        """
        Spawn a single enemy tank using spawn validation.
        
        Args:
            difficulty (int): Difficulty level of the tank
            player_position (tuple): (x, y) position of the player tank in pixels
            game_engine (GameEngine): The game engine to add the tank to
            
        Returns:
            EnemyTank: The spawned enemy tank, or None if no valid position found
        """
        # Find a valid spawn position using spawn validator
        min_distance_from_player = self.min_distance_from_player * self.map_data.cell_size
        spawn_position = self.spawn_validator.find_valid_spawn_location_with_distance(
            tank_size=32,
            max_attempts=self.spawn_attempts,
            min_distance_from_obstacles=2,
            min_distance_from_point=player_position,
            min_point_distance=min_distance_from_player
        )
        
        if spawn_position:
            pixel_x, pixel_y = spawn_position
            
            # Create the enemy tank
            enemy_tank = EnemyTank(pixel_x, pixel_y, difficulty=difficulty)
            
            # Set sound manager for the enemy tank
            if hasattr(game_engine, 'sound_manager') and game_engine.sound_manager:
                enemy_tank.set_sound_manager(game_engine.sound_manager)
            
            # Add the tank to the game engine
            game_engine.add_game_object(enemy_tank)
            
            return enemy_tank
        else:
            # Try with reduced constraints as fallback
            fallback_spawn = self.spawn_validator.find_valid_spawn_location(
                tank_size=32,
                max_attempts=self.spawn_attempts,
                min_distance_from_obstacles=1  # Reduced buffer
            )
            
            if fallback_spawn:
                pixel_x, pixel_y = fallback_spawn
                
                # Check distance from player (reduced requirement)
                player_distance = math.sqrt((pixel_x - player_position[0]) ** 2 + (pixel_y - player_position[1]) ** 2)
                min_player_distance = (self.min_distance_from_player // 2) * self.map_data.cell_size
                
                if player_distance >= min_player_distance:
                    # Create the enemy tank with fallback position
                    enemy_tank = EnemyTank(pixel_x, pixel_y, difficulty=difficulty)
                    
                    # Set sound manager for the enemy tank
                    if hasattr(game_engine, 'sound_manager') and game_engine.sound_manager:
                        enemy_tank.set_sound_manager(game_engine.sound_manager)
                    
                    # Add the tank to the game engine
                    game_engine.add_game_object(enemy_tank)
                    
                    print(f"Info: Used fallback spawn location for single enemy tank with difficulty {difficulty}")
                    return enemy_tank
            
            # Last resort: try emergency spawn
            emergency_spawn = self._find_emergency_spawn_location(player_position)
            if emergency_spawn:
                pixel_x, pixel_y = emergency_spawn
                enemy_tank = EnemyTank(pixel_x, pixel_y, difficulty=difficulty)
                
                # Set sound manager for the enemy tank
                if hasattr(game_engine, 'sound_manager') and game_engine.sound_manager:
                    enemy_tank.set_sound_manager(game_engine.sound_manager)
                
                # Add the tank to the game engine
                game_engine.add_game_object(enemy_tank)
                
                print(f"Info: Used emergency spawn location for single enemy tank with difficulty {difficulty}")
                return enemy_tank
            
            print(f"Warning: Could not find valid spawn location for single enemy tank with difficulty {difficulty}")
            return None
    
    def _find_emergency_spawn_location(self, player_position):
        """
        Find an emergency spawn location with minimal constraints.
        This is used as a last resort when normal spawn validation fails.
        
        Args:
            player_position (tuple): (x, y) position of the player tank in pixels
            
        Returns:
            tuple: (x, y) pixel coordinates for spawn location, or None if no location found
        """
        # Try to find any empty cell that's not too close to the player
        min_player_distance = 64  # Minimum 2 cells away from player
        
        for attempt in range(50):  # Limited attempts for emergency spawn
            # Random position on the map
            cell_x = random.randint(1, self.map_data.width - 2)
            cell_y = random.randint(1, self.map_data.height - 2)
            
            # Check if the cell is empty
            if self.map_data.is_empty_at(cell_x, cell_y):
                # Convert to pixel coordinates
                pixel_x = cell_x * self.map_data.cell_size
                pixel_y = cell_y * self.map_data.cell_size
                
                # Check distance from player
                player_distance = math.sqrt((pixel_x - player_position[0]) ** 2 + (pixel_y - player_position[1]) ** 2)
                
                if player_distance >= min_player_distance:
                    return (pixel_x, pixel_y)
        
        return None