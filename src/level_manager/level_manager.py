"""
Level Manager module for the Tank Game.
This module defines the LevelManager class that handles level progression and management.
"""
import pygame
import random
import math
from src.level_manager.map_generator import MapGenerator
from src.level_manager.enemy_tank_spawner import EnemyTankSpawner
from src.level_manager.difficulty_manager import DifficultyManager
from src.level_manager.level_transition import LevelTransition
from src.level_manager.spawn_validator import SpawnValidator


class LevelManager:
    """
    Manages game levels, progression, and difficulty scaling.
    """
    def __init__(self, game_engine, map_width=25, map_height=19, max_level=10):
        """
        Initialize the level manager.
        
        Args:
            game_engine (GameEngine): The game engine instance
            map_width (int): Width of the map in cells
            map_height (int): Height of the map in cells
            max_level (int): Maximum level number
        """
        self.game_engine = game_engine
        self.map_width = map_width
        self.map_height = map_height
        self.current_level = 1
        self.max_level = max_level
        self.map_generator = MapGenerator(map_width, map_height)
        self.map_data = None
        self.enemy_tanks = []
        self.player_tank = None
        self.level_complete = False
        self.game_complete = False
        self.score = 0
        self.difficulty_manager = DifficultyManager(max_difficulty=5)
        self.transition = LevelTransition(game_engine)
        
    def initialize(self, player_tank):
        """
        Initialize the level manager with a player tank.
        
        Args:
            player_tank: The player's tank
        """
        self.player_tank = player_tank
        self.start_level(1)
        
    def start_level(self, level_number):
        """
        Start a new level.
        
        Args:
            level_number (int): The level number to start
            
        Returns:
            bool: True if the level was started successfully, False otherwise
        """
        # Check if the level number is valid
        if level_number < 1 or level_number > self.max_level:
            return False
            
        # Update the current level
        self.current_level = level_number
        self.game_engine.current_level = level_number
        
        # Reset level state
        self.level_complete = False
        
        # Generate a new map with difficulty based on level
        map_difficulty = self.difficulty_manager.get_map_difficulty(level_number)
        self.map_data = self.map_generator.generate_map(map_difficulty)
        
        # Set the cell size
        self.map_data.set_cell_size(32)
        
        # Create game objects for destructible elements
        self._create_destructible_elements()
        
        # Clear existing enemy tanks
        for tank in self.enemy_tanks:
            self.game_engine.remove_game_object(tank)
        self.enemy_tanks = []
        
        # Create an enemy tank spawner
        spawner = EnemyTankSpawner(self.map_data)
        
        # Spawn enemy tanks
        player_position = (self.player_tank.x, self.player_tank.y)
        
        try:
            self.enemy_tanks = spawner.spawn_enemy_tanks(level_number, player_position, self.game_engine, self.difficulty_manager)
        except TypeError:
            # Fallback to spawning without difficulty manager
            self.enemy_tanks = spawner.spawn_enemy_tanks(level_number, player_position, self.game_engine)
        
        # Update player parameters based on level
        player_params = self.difficulty_manager.get_player_params(level_number)
        self.player_tank.health = player_params['health']
        self.player_tank.max_health = player_params['health']
        self.player_tank.speed = player_params['speed']
        self.player_tank.fire_cooldown = player_params['fire_cooldown']
        
        # Position the player tank using spawn validation
        spawn_validator = SpawnValidator(self.map_data)
        player_spawn = spawn_validator.find_valid_spawn_location(
            tank_size=32,
            max_attempts=100,
            min_distance_from_obstacles=2
        )
        
        if player_spawn:
            self.player_tank.x, self.player_tank.y = player_spawn
        else:
            # Fallback to center if no valid spawn found (should be rare)
            print("Warning: Could not find valid spawn location for player tank, using center")
            self.player_tank.x = self.map_data.width * self.map_data.cell_size / 2
            self.player_tank.y = self.map_data.height * self.map_data.cell_size / 2
        
        return True
        
    def update(self, delta_time):
        """
        Update the level manager.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
            
        Returns:
            bool: True if the game is still running, False otherwise
        """
        # If in transition, update the transition
        if self.transition.active:
            transition_complete = self.transition.update(delta_time)
            
            if transition_complete:
                # If the game is complete, return False
                if self.game_complete:
                    return False
                    
                # Otherwise, start the next level
                self.start_level(self.current_level + 1)
            
            return True
            
        # Remove destroyed enemy tanks and None entries
        for tank in self.enemy_tanks[:]:
            if tank is None or not tank.active:
                if tank is not None:
                    self.game_engine.remove_game_object(tank)
                    # Award points for destroying the tank
                    if hasattr(tank, 'difficulty'):
                        score_multiplier = self.difficulty_manager.get_score_multiplier(self.current_level, tank.difficulty)
                        self.score += score_multiplier
                self.enemy_tanks.remove(tank)
        
        # Check if all enemy tanks are destroyed
        active_enemy_count = len([tank for tank in self.enemy_tanks if tank is not None and tank.active])
        if active_enemy_count == 0:
            self.level_complete = True
            
            # Check if this was the last level
            if self.current_level >= self.max_level:
                self.game_complete = True
                
            # Start the transition to the next level
            self.transition.start(self.current_level, self.score, self.game_complete)
            
        return True
        
    def render_transition(self, screen):
        """
        Render the level transition on the screen.
        
        Args:
            screen: The pygame screen to render on
        """
        self.transition.render(screen)
        
    def is_level_complete(self):
        """
        Check if the current level is complete.
        
        Returns:
            bool: True if the level is complete, False otherwise
        """
        return self.level_complete
        
    def is_game_complete(self):
        """
        Check if the game is complete (all levels finished).
        
        Returns:
            bool: True if the game is complete, False otherwise
        """
        return self.game_complete
        
    def get_current_level(self):
        """
        Get the current level number.
        
        Returns:
            int: The current level number
        """
        return self.current_level
        
    def get_max_level(self):
        """
        Get the maximum level number.
        
        Returns:
            int: The maximum level number
        """
        return self.max_level
        
    def get_score(self):
        """
        Get the current score.
        
        Returns:
            int: The current score
        """
        return self.score
        
    def add_score(self, points):
        """
        Add points to the score.
        
        Args:
            points (int): The number of points to add
        """
        self.score += points
        
    def _create_destructible_elements(self):
        """
        Create game objects for destructible elements in the map.
        """
        # Import here to avoid circular imports
        from src.game_objects.rock_pile import RockPile
        from src.game_objects.petrol_barrel import PetrolBarrel
        
        # Remove existing destructible elements
        for obj in self.game_engine.game_objects[:]:
            if hasattr(obj, 'tag') and obj.tag in ["rock_pile", "petrol_barrel"]:
                self.game_engine.remove_game_object(obj)
        
        # Create new destructible elements
        for y in range(self.map_data.height):
            for x in range(self.map_data.width):
                cell_type = self.map_data.get_cell(x, y)
                
                if cell_type == self.map_data.ROCK_PILE:
                    # Create a rock pile
                    pixel_x = x * self.map_data.cell_size
                    pixel_y = y * self.map_data.cell_size
                    rock_pile = RockPile(pixel_x, pixel_y, health=50)  # Updated health value
                    rock_pile.width = self.map_data.cell_size
                    rock_pile.height = self.map_data.cell_size
                    self.game_engine.add_game_object(rock_pile)
                    print(f"Created rock pile at ({x}, {y}) -> ({pixel_x}, {pixel_y})")
                    
                elif cell_type == self.map_data.PETROL_BARREL:
                    # Create a petrol barrel
                    pixel_x = x * self.map_data.cell_size
                    pixel_y = y * self.map_data.cell_size
                    petrol_barrel = PetrolBarrel(pixel_x, pixel_y, health=30)  # Updated health value
                    petrol_barrel.width = self.map_data.cell_size
                    petrol_barrel.height = self.map_data.cell_size
                    self.game_engine.add_game_object(petrol_barrel)
                    print(f"Created petrol barrel at ({x}, {y}) -> ({pixel_x}, {pixel_y})")
    
    def reset(self):
        """
        Reset the level manager to its initial state.
        """
        self.current_level = 1
        self.level_complete = False
        self.game_complete = False
        self.score = 0
        
        # Start the first level
        if self.player_tank:
            self.start_level(1)
            
    def spawn_enemy_tank(self, difficulty=None):
        """
        Spawn a single enemy tank.
        
        Args:
            difficulty (int, optional): Difficulty level of the tank. If None, uses the current level.
            
        Returns:
            EnemyTank: The spawned enemy tank, or None if no valid position found
        """
        if self.map_data is None:
            return None
            
        # Use the current level's difficulty if not specified
        if difficulty is None:
            difficulty = self.difficulty_manager.get_map_difficulty(self.current_level)
            
        # Create a spawner
        spawner = EnemyTankSpawner(self.map_data)
        
        # Spawn a single enemy tank
        player_position = (self.player_tank.x, self.player_tank.y)
        enemy_tank = spawner.spawn_single_enemy_tank(difficulty, player_position, self.game_engine)
        
        # Add the tank to the list if it was spawned successfully
        if enemy_tank:
            self.enemy_tanks.append(enemy_tank)
            
        return enemy_tank