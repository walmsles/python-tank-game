"""
Enhanced Tank Renderer module for the Tank Game.
This module handles the rendering of tanks with improved visuals.
"""
import pygame
import math


class EnhancedTankRenderer:
    """
    Handles enhanced rendering of tanks with improved visuals.
    """
    def __init__(self, renderer):
        """
        Initialize the enhanced tank renderer.
        
        Args:
            renderer: The game renderer
        """
        self.renderer = renderer
        self.player_tank_sprite = None
        self.enemy_tank_sprite = None
        self.health_bar_width = 30
        self.health_bar_height = 5
        
        # Create enhanced sprites
        self._create_enhanced_sprites()
        
    def _create_enhanced_sprites(self):
        """Create enhanced sprites for tanks."""
        # Create player tank sprite (blue with enhanced details)
        self.player_tank_sprite = self._create_enhanced_tank_sprite((0, 100, 255))
        
        # Create enemy tank sprite (red with enhanced details)
        self.enemy_tank_sprite = self._create_enhanced_tank_sprite((255, 50, 50))
        
    def _create_enhanced_tank_sprite(self, color):
        """
        Create an enhanced tank sprite with the given color.
        
        Args:
            color: RGB tuple representing the color
            
        Returns:
            pygame.Surface: The created tank sprite
        """
        # Create a surface for the tank
        tank_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        tank_sprite.fill((0, 0, 0, 0))  # Transparent background
        
        # Calculate darker and lighter shades for 3D effect
        darker_color = tuple(max(0, c - 40) for c in color)
        lighter_color = tuple(min(255, c + 40) for c in color)
        shadow_color = tuple(max(0, c - 60) for c in color)
        
        # Draw tank tracks (darker rectangles on sides with treads)
        pygame.draw.rect(tank_sprite, shadow_color, (2, 6, 4, 20), border_radius=2)
        pygame.draw.rect(tank_sprite, shadow_color, (26, 6, 4, 20), border_radius=2)
        
        # Add tread details
        for i in range(4):
            y_pos = 8 + i * 4
            pygame.draw.line(tank_sprite, darker_color, (2, y_pos), (6, y_pos), 1)
            pygame.draw.line(tank_sprite, darker_color, (26, y_pos), (30, y_pos), 1)
        
        # Draw the tank body (main hull) with gradient effect
        pygame.draw.rect(tank_sprite, shadow_color, (6, 8, 20, 16), border_radius=3)
        pygame.draw.rect(tank_sprite, color, (7, 9, 18, 14), border_radius=3)
        # Add highlight to body
        pygame.draw.rect(tank_sprite, lighter_color, (8, 10, 16, 3))
        
        # Draw the tank turret (circle with 3D effect)
        pygame.draw.circle(tank_sprite, shadow_color, (17, 17), 9)  # Shadow
        pygame.draw.circle(tank_sprite, darker_color, (16, 16), 9)  # Base shadow
        pygame.draw.circle(tank_sprite, color, (16, 16), 8)
        pygame.draw.circle(tank_sprite, lighter_color, (14, 14), 4)  # Highlight
        pygame.draw.circle(tank_sprite, color, (14, 14), 3)  # Inner highlight
        
        # Draw the tank barrel (rectangle) - pointing upward (0 degrees)
        pygame.draw.rect(tank_sprite, shadow_color, (13, -1, 6, 17))  # Shadow
        pygame.draw.rect(tank_sprite, darker_color, (14, 0, 4, 16))  # Base
        pygame.draw.rect(tank_sprite, color, (14.5, 0.5, 3, 15))  # Main barrel
        pygame.draw.rect(tank_sprite, lighter_color, (15, 1, 2, 14))  # Highlight
        
        # Draw a muzzle brake at barrel tip
        pygame.draw.rect(tank_sprite, darker_color, (13, -2, 6, 3))
        pygame.draw.rect(tank_sprite, color, (14, -1, 4, 2))
        
        # Add some detail lines and rivets to the body
        pygame.draw.line(tank_sprite, darker_color, (8, 12), (24, 12), 1)
        pygame.draw.line(tank_sprite, darker_color, (8, 20), (24, 20), 1)
        
        # Add rivets (small circles)
        for x in [10, 16, 22]:
            pygame.draw.circle(tank_sprite, darker_color, (x, 14), 1)
            pygame.draw.circle(tank_sprite, lighter_color, (x-1, 13), 1)
        
        # Add antenna (small line)
        pygame.draw.line(tank_sprite, (200, 200, 200), (20, 10), (22, 6), 2)
        pygame.draw.circle(tank_sprite, (255, 255, 0), (22, 6), 1)  # Antenna tip
        
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
        Render a tank on the screen with enhanced visuals.
        
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
            
        # Render the tank with enhanced effects
        self._render_tank_with_effects(screen, tank)
        
        # Render the enhanced health bar
        self._render_enhanced_health_bar(screen, tank)
        
    def _render_tank_with_effects(self, screen, tank):
        """
        Render a tank with visual effects.
        
        Args:
            screen: Pygame surface to render on
            tank: The tank to render
        """
        # Add a subtle shadow beneath the tank
        shadow_surface = pygame.Surface((tank.width + 4, tank.height + 4), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 50))  # Semi-transparent black
        screen.blit(shadow_surface, (tank.x - 2, tank.y + 2))
        
        # Render the tank normally
        tank.render(screen)
        
        # Add damage effects if tank is damaged
        if hasattr(tank, 'health') and hasattr(tank, 'max_health'):
            damage_ratio = 1 - (tank.health / tank.max_health)
            if damage_ratio > 0.3:  # Show damage effects when below 70% health
                self._render_damage_effects(screen, tank, damage_ratio)
                
    def _render_damage_effects(self, screen, tank, damage_ratio):
        """
        Render damage effects on the tank.
        
        Args:
            screen: Pygame surface to render on
            tank: The tank to render effects for
            damage_ratio: Ratio of damage (0.0 to 1.0)
        """
        # Create smoke particles for heavily damaged tanks
        if damage_ratio > 0.5:
            import random
            for _ in range(int(damage_ratio * 3)):
                smoke_x = tank.x + random.randint(0, tank.width)
                smoke_y = tank.y + random.randint(0, tank.height // 2)
                smoke_size = random.randint(2, 4)
                smoke_alpha = int(100 * damage_ratio)
                
                smoke_surface = pygame.Surface((smoke_size * 2, smoke_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surface, (80, 80, 80, smoke_alpha), 
                                 (smoke_size, smoke_size), smoke_size)
                screen.blit(smoke_surface, (smoke_x - smoke_size, smoke_y - smoke_size))
        
        # Add sparks for critical damage
        if damage_ratio > 0.7:
            import random
            for _ in range(int(damage_ratio * 2)):
                spark_x = tank.x + random.randint(0, tank.width)
                spark_y = tank.y + random.randint(0, tank.height)
                pygame.draw.circle(screen, (255, 255, 0), (int(spark_x), int(spark_y)), 1)
                
    def _render_enhanced_health_bar(self, screen, tank):
        """
        Render an enhanced health bar above the tank.
        
        Args:
            screen: Pygame surface to render on
            tank: The tank to render the health bar for
        """
        # Calculate the health bar position (centered above the tank)
        bar_x = tank.x + (tank.width - self.health_bar_width) / 2
        bar_y = tank.y - self.health_bar_height - 4
        
        # Calculate the health percentage
        health_percentage = max(0, min(1, tank.health / tank.max_health))
        
        # Draw a background shadow
        pygame.draw.rect(screen, (0, 0, 0, 100), 
                        (bar_x - 1, bar_y - 1, self.health_bar_width + 2, self.health_bar_height + 2))
        
        # Draw the background (dark red)
        pygame.draw.rect(screen, (100, 20, 20), 
                        (bar_x, bar_y, self.health_bar_width, self.health_bar_height))
        
        # Draw the health with gradient effect
        health_width = int(self.health_bar_width * health_percentage)
        if health_percentage > 0.6:
            health_color = (0, 200, 0)  # Green
            highlight_color = (50, 255, 50)
        elif health_percentage > 0.3:
            health_color = (200, 200, 0)  # Yellow
            highlight_color = (255, 255, 50)
        else:
            health_color = (200, 0, 0)  # Red
            highlight_color = (255, 50, 50)
            
        # Main health bar
        pygame.draw.rect(screen, health_color, 
                        (bar_x, bar_y, health_width, self.health_bar_height))
        
        # Highlight on top
        if health_width > 2:
            pygame.draw.rect(screen, highlight_color, 
                            (bar_x, bar_y, health_width, 1))
        
        # Draw a border around the health bar
        pygame.draw.rect(screen, (255, 255, 255), 
                        (bar_x, bar_y, self.health_bar_width, self.health_bar_height), 1)