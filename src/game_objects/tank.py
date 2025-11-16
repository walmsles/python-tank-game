"""
Tank module for the Tank Game.
This module defines the Tank base class that represents a tank in the game.
"""
import math
from src.engine.game_object import GameObject
from src.game_objects.projectile import Projectile


class Tank(GameObject):
    """
    Base class for all tanks in the game.
    """
    def __init__(self, x, y, health=100, speed=5):
        """
        Initialize a tank.
        
        Args:
            x (float): X-coordinate position
            y (float): Y-coordinate position
            health (int): Initial health of the tank
            speed (float): Movement speed of the tank
        """
        super().__init__(x, y)
        # Set default tank dimensions (32x32 pixels)
        self.width = 32
        self.height = 32
        # Sound-related attributes
        self.sound_manager = None  # Will be set by the game engine
        self.movement_sound_channel = None  # Track movement sound channel
        self.is_moving = False  # Track movement state for sound
        self.health = health
        self.max_health = health
        self.speed = speed
        self.direction = 0  # Direction in degrees (0 = up, 90 = right, 180 = down, 270 = left)
        self.rotation_speed = 3  # Degrees per frame
        self.tag = "tank"
        self.collision_radius = 16  # For simplified collision detection
        self.fire_cooldown = 0.5  # 0.5 seconds between shots
        self.last_fire_time = 0
        
    def update(self, delta_time, map_data):
        """
        Update the tank state.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
            map_data (MapData): The map data for collision detection
        """
        # Update fire cooldown
        self.last_fire_time += delta_time
        
        # Update movement sound state
        self._update_movement_sound()
        
    def move_forward(self, delta_time, map_data):
        """
        Move the tank forward in its current direction.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
            map_data (MapData): The map data for collision detection
            
        Returns:
            bool: True if the movement was successful, False if blocked by an obstacle
        """
        # Calculate the movement vector based on direction
        # Note: 0 degrees is up, 90 degrees is right, etc.
        rad = math.radians(self.direction)
        dx = math.sin(rad) * self.speed * delta_time * 60  # Normalize by 60 FPS
        dy = -math.cos(rad) * self.speed * delta_time * 60  # Y is inverted in screen coordinates
        
        # Check if the new position would collide with an obstacle
        if self._check_collision(self.x + dx, self.y + dy, map_data):
            return False
        
        # If no collision, update the position
        self.x += dx
        self.y += dy
        return True
        
    def move_backward(self, delta_time, map_data):
        """
        Move the tank backward (opposite of its current direction).
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
            map_data (MapData): The map data for collision detection
            
        Returns:
            bool: True if the movement was successful, False if blocked by an obstacle
        """
        # Calculate the movement vector based on direction (opposite of forward)
        # Note: 0 degrees is up, 90 degrees is right, etc.
        rad = math.radians(self.direction)
        dx = -math.sin(rad) * self.speed * 0.5 * delta_time * 60  # Half speed when moving backward
        dy = math.cos(rad) * self.speed * 0.5 * delta_time * 60  # Y is inverted in screen coordinates
        
        # Check if the new position would collide with an obstacle
        if self._check_collision(self.x + dx, self.y + dy, map_data):
            return False
        
        # If no collision, update the position
        self.x += dx
        self.y += dy
        return True
        
    def rotate_left(self, delta_time):
        """
        Rotate the tank counter-clockwise.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
        """
        self.direction = (self.direction - self.rotation_speed * delta_time * 60) % 360
        self.set_rotation(-self.direction)  # Negative because pygame rotation is clockwise
        
    def rotate_right(self, delta_time):
        """
        Rotate the tank clockwise.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
        """
        self.direction = (self.direction + self.rotation_speed * delta_time * 60) % 360
        self.set_rotation(-self.direction)  # Negative because pygame rotation is clockwise
        
    def fire(self):
        """
        Fire a projectile from the tank.
        
        Returns:
            Projectile: The fired projectile, or None if the tank cannot fire
        """
        # Check if the tank can fire (cooldown elapsed)
        if self.last_fire_time < self.fire_cooldown:
            return None
            
        # Reset the cooldown
        self.last_fire_time = 0
        
        # Calculate the projectile's starting position (at the end of the tank's barrel)
        # The barrel is pointing in the direction of the tank
        barrel_length = self.width / 2 + 5  # Extend slightly beyond the tank's radius
        rad = math.radians(self.direction)
        
        # Calculate the center of the tank
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        
        # Calculate the position at the end of the barrel
        projectile_center_x = center_x + math.sin(rad) * barrel_length
        projectile_center_y = center_y - math.cos(rad) * barrel_length
        
        # Adjust for the projectile's size (assuming 8x8 projectile)
        projectile_x = projectile_center_x - 4
        projectile_y = projectile_center_y - 4
        
        # Create and return the projectile
        # Play firing sound
        self._play_fire_sound()
        
        return Projectile(projectile_x, projectile_y, self.direction, speed=10, damage=20, owner=self)
        
    def take_damage(self, amount):
        """
        Reduce the health of the tank by the given amount.
        
        Args:
            amount (int): Amount of damage to take
            
        Returns:
            bool: True if the tank was destroyed, False otherwise
        """
        self.health -= amount
        
        if self.health <= 0:
            self.health = 0
            self.active = False
            return True
            
        return False
        
    def _check_collision(self, new_x, new_y, map_data):
        """
        Check if the tank would collide with an obstacle at the given position.
        
        Args:
            new_x (float): New X-coordinate to check
            new_y (float): New Y-coordinate to check
            map_data (MapData): The map data for collision detection
            
        Returns:
            bool: True if there would be a collision, False otherwise
        """
        # Convert pixel coordinates to cell coordinates
        cell_size = map_data.cell_size
        
        # Check the cells around the tank's center
        center_x = new_x + self.width / 2
        center_y = new_y + self.height / 2
        
        # Check in a radius around the tank's center
        for angle in range(0, 360, 30):  # Check every 30 degrees
            rad = math.radians(angle)
            check_x = center_x + math.cos(rad) * self.collision_radius
            check_y = center_y + math.sin(rad) * self.collision_radius
            
            # Convert to cell coordinates (ensuring integers)
            cell_x = int(check_x // cell_size)
            cell_y = int(check_y // cell_size)
            
            if map_data.is_obstacle_at(cell_x, cell_y):
                return True
                
        return False    

    def set_sound_manager(self, sound_manager):
        """
        Set the sound manager for this tank.
        
        Args:
            sound_manager (SoundManager): The sound manager instance
        """
        self.sound_manager = sound_manager
    
    def _play_movement_sound(self):
        """
        Play the tank movement sound if not already playing.
        """
        if (self.sound_manager and self.sound_manager.is_sound_enabled() and 
            (not self.movement_sound_channel or not self.movement_sound_channel.get_busy())):
            self.movement_sound_channel = self.sound_manager.play_sound('tank_move', loops=-1)
    
    def _stop_movement_sound(self):
        """
        Stop the tank movement sound.
        """
        if self.movement_sound_channel and self.movement_sound_channel.get_busy():
            self.movement_sound_channel.stop()
            self.movement_sound_channel = None
    
    def _update_movement_sound(self):
        """
        Update the movement sound based on current movement state.
        """
        if self.is_moving:
            self._play_movement_sound()
        else:
            self._stop_movement_sound()
    
    def _play_fire_sound(self):
        """
        Play the tank firing sound.
        """
        if self.sound_manager and self.sound_manager.is_sound_enabled():
            self.sound_manager.play_sound('tank_fire')
    
    def check_collision_with_object(self, other_object):
        """
        Check if this tank collides with another game object.
        
        Args:
            other_object: The other game object to check collision with
            
        Returns:
            bool: True if there is a collision, False otherwise
        """
        if not other_object or not other_object.active:
            return False
            
        # Simple rectangular collision detection
        tank_left = self.x
        tank_right = self.x + self.width
        tank_top = self.y
        tank_bottom = self.y + self.height
        
        obj_left = other_object.x
        obj_right = other_object.x + other_object.width
        obj_top = other_object.y
        obj_bottom = other_object.y + other_object.height
        
        # Check if rectangles overlap
        return (tank_left < obj_right and tank_right > obj_left and
                tank_top < obj_bottom and tank_bottom > obj_top)