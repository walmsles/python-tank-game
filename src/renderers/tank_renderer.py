"""
Tank Renderer module for the Tank Game.
This module handles the rendering of tanks.
"""
import pygame
import math


class TankRenderer:
    """
    Handles rendering of tanks.
    """
    def __init__(self, renderer):
        """
        Initialize the tank renderer.
        
        Args:
            renderer: The game renderer
        """
        self.renderer = renderer
        self.player_tank_sprite = None
        self.enemy_tank_sprite = None
        self.health_bar_width = 30
        self.health_bar_height = 5
        
        # Create default sprites
        self._create_default_sprites()
        
    def _create_default_sprites(self):
        """Create default sprites for tanks."""
        # Create player tank sprite (blue)
        self.player_tank_sprite = self._create_tank_sprite((0, 0, 255))
        
        # Create enemy tank sprite (red)
        self.enemy_tank_sprite = self._create_tank_sprite((255, 0, 0))
        
    def _create_tank_sprite(self, color):
        """
        Create a tank sprite with the given color.
        
        Args:
            color: RGB tuple representing the color
            
        Returns:
            pygame.Surface: The created tank sprite
        """
        # Create a surface for the tank
        tank_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        tank_sprite.fill((0, 0, 0, 0))  # Transparent background
        
        # Draw the tank body (rectangle with rounded corners)
        pygame.draw.rect(tank_sprite, color, (4, 8, 24, 16), border_radius=3)
        
        # Draw the tank turret (circle)
        pygame.draw.circle(tank_sprite, color, (16, 16), 8)
        
        # Draw the tank barrel (rectangle) - pointing upward (0 degrees)
        pygame.draw.rect(tank_sprite, color, (14, 0, 4, 16))
        
        # Draw a direction indicator (small triangle at the front)
        pygame.draw.polygon(tank_sprite, (255, 255, 255), [(14, 0), (18, 0), (16, -4)])
        
        return tank_sprite
        
    def set_player_tank_sprite(self, sprite):
        """
        Set the sprite for the player tank.
        
        Args:
            sprite: Pygame surface to use as player tank sprite
        """
        self.player_tank_sprite = sprite
        
    def set_enemy_tank_sprite(self, sprite):
        """
        Set the sprite for enemy tanks.
        
        Args:
            sprite: Pygame surface to use as enemy tank sprite
        """
        self.enemy_tank_sprite = sprite
        
    def render_tank(self, screen, tank):
        """
        Render a tank on the screen.
        
        Args:
            screen: Pygame surface to render on
            tank: The tank to render
        """
        # Skip rendering if the tank is not active
        if not tank.active:
            return
            
        # Choose the appropriate sprite based on the tank type
        if tank.tag == "player":
            sprite = self.player_tank_sprite
        else:
            sprite = self.enemy_tank_sprite
            
        # Set the tank's sprite if it doesn't have one
        if tank.sprite is None:
            tank.set_sprite(sprite)
            
        # Render the tank
        tank.render(screen)
        
        # Render the health bar
        self._render_health_bar(screen, tank)
        
    def _render_health_bar(self, screen, tank):
        """
        Render a health bar above the tank.
        
        Args:
            screen: Pygame surface to render on
            tank: The tank to render the health bar for
        """
        # Calculate the health bar position (centered above the tank)
        bar_x = tank.x + (tank.width - self.health_bar_width) / 2
        bar_y = tank.y - self.health_bar_height - 2
        
        # Calculate the health percentage
        health_percentage = max(0, min(1, tank.health / tank.max_health))
        
        # Draw the background (gray)
        pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, self.health_bar_width, self.health_bar_height))
        
        # Draw the health (green to red based on health percentage)
        health_width = int(self.health_bar_width * health_percentage)
        if health_percentage > 0.6:
            health_color = (0, 255, 0)  # Green
        elif health_percentage > 0.3:
            health_color = (255, 255, 0)  # Yellow
        else:
            health_color = (255, 0, 0)  # Red
            
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, self.health_bar_height))
        
        # Draw a border around the health bar
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, self.health_bar_width, self.health_bar_height), 1)