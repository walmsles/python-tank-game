"""
Difficulty Manager module for the Tank Game.
This module defines the DifficultyManager class that handles difficulty scaling.
"""
import random


class DifficultyManager:
    """
    Manages difficulty scaling for the game.
    """
    def __init__(self, max_difficulty=5):
        """
        Initialize the difficulty manager.
        
        Args:
            max_difficulty (int): Maximum difficulty level
        """
        self.max_difficulty = max_difficulty
        
    def get_map_difficulty(self, level):
        """
        Get the map difficulty for a given level.
        
        Args:
            level (int): Current level number
            
        Returns:
            int: Map difficulty (1-5)
        """
        # Map difficulty increases with level, capped at max_difficulty
        return min(level, self.max_difficulty)
        
    def get_num_enemy_tanks(self, level):
        """
        Get the number of enemy tanks for a given level.
        
        Args:
            level (int): Current level number
            
        Returns:
            int: Number of enemy tanks
        """
        # Base number of tanks
        base_tanks = 1
        
        # Additional tanks based on level (more tanks at higher levels)
        # Formula: 1 tank at level 1, +1 tank every level up to a cap
        additional_tanks = min(level - 1, 5)  # Cap at 6 tanks total (1 base + 5 additional)
        
        return base_tanks + additional_tanks
        
    def get_enemy_tank_difficulties(self, level, num_tanks):
        """
        Get the difficulty levels for enemy tanks.
        
        Args:
            level (int): Current level number
            num_tanks (int): Number of tanks to spawn
            
        Returns:
            list: List of difficulty levels for each tank
        """
        difficulties = []
        
        # Base difficulty increases with level
        base_difficulty = min(level, self.max_difficulty)
        
        # First tank is always at base difficulty
        difficulties.append(base_difficulty)
        
        # Remaining tanks have varying difficulties
        for i in range(1, num_tanks):
            # Distribution of tank difficulties:
            # - 20% chance: easier than base (-1)
            # - 50% chance: same as base
            # - 30% chance: harder than base (+1)
            # This creates a mix of easier and harder tanks, with a bias towards harder
            rand = random.random()
            if rand < 0.2:
                # Easier tank
                difficulty = max(1, base_difficulty - 1)
            elif rand < 0.7:
                # Same difficulty
                difficulty = base_difficulty
            else:
                # Harder tank
                difficulty = min(self.max_difficulty, base_difficulty + 1)
                
            difficulties.append(difficulty)
            
        return difficulties
        
    def get_enemy_spawn_params(self, level):
        """
        Get enemy spawn parameters for a given level.
        
        Args:
            level (int): Current level number
            
        Returns:
            dict: Dictionary of spawn parameters
        """
        # Base parameters
        params = {
            'min_distance_between_tanks': 5,
            'min_distance_from_player': 8,
            'spawn_attempts': 50
        }
        
        # Adjust parameters based on level
        if level >= 3:
            # At higher levels, tanks can spawn closer together
            params['min_distance_between_tanks'] = 4
            
        if level >= 5:
            # At even higher levels, tanks can spawn closer to the player
            params['min_distance_from_player'] = 6
            
        if level >= 7:
            # At very high levels, make more attempts to find spawn positions
            params['spawn_attempts'] = 75
            
        return params
        
    def get_score_multiplier(self, level, tank_difficulty):
        """
        Get the score multiplier for destroying an enemy tank.
        
        Args:
            level (int): Current level number
            tank_difficulty (int): Difficulty of the destroyed tank
            
        Returns:
            int: Score multiplier
        """
        # Base score is 100 points
        base_score = 100
        
        # Level multiplier
        level_multiplier = level
        
        # Difficulty multiplier
        difficulty_multiplier = tank_difficulty
        
        return base_score * level_multiplier * difficulty_multiplier
        
    def get_player_params(self, level):
        """
        Get player parameters for a given level.
        
        Args:
            level (int): Current level number
            
        Returns:
            dict: Dictionary of player parameters
        """
        # Base parameters
        params = {
            'health': 100,
            'speed': 5,
            'fire_cooldown': 0.5
        }
        
        # Adjust parameters based on level
        if level >= 4:
            # At higher levels, give the player more health
            params['health'] = 120
            
        if level >= 7:
            # At even higher levels, give the player faster firing
            params['fire_cooldown'] = 0.4
            
        if level >= 9:
            # At very high levels, give the player more speed
            params['speed'] = 5.5
            
        return params