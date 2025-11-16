"""
Projectile Renderer module for the Tank Game.
This module handles the rendering of projectiles.
"""
import pygame
import math


class ProjectileRenderer:
    """
    Handles rendering of projectiles.
    """
    def __init__(self, renderer):
        """
        Initialize the projectile renderer.
        
        Args:
            renderer: The game renderer
        """
        self.renderer = renderer
        self.projectile_sprite = None
        
        # Create default sprite
        self._create_default_sprite()
        
    def _create_default_sprite(self):
        """Create default sprite for projectiles."""
        # Create projectile sprite (yellow circle)
        self.projectile_sprite = pygame.Surface((8, 8), pygame.SRCALPHA)
        self.projectile_sprite.fill((0, 0, 0, 0))  # Transparent background
        pygame.draw.circle(self.projectile_sprite, (255, 255, 0), (4, 4), 4)  # Yellow circle
        
    def set_projectile_sprite(self, sprite):
        """
        Set the sprite for projectiles.
        
        Args:
            sprite: Pygame surface to use as projectile sprite
        """
        self.projectile_sprite = sprite
        
    def render_projectile(self, screen, projectile):
        """
        Render a projectile on the screen.
        
        Args:
            screen: Pygame surface to render on
            projectile: The projectile to render
        """
        # Skip rendering if the projectile is not active
        if not projectile.active:
            return
            
        # Set the projectile's sprite if it doesn't have one
        if projectile.sprite is None:
            projectile.set_sprite(self.projectile_sprite)
            
        # Render the projectile
        projectile.render(screen)
        
        # Optionally add a trail effect
        self._render_trail(screen, projectile)
        
    def _render_trail(self, screen, projectile):
        """
        Render a trail effect behind the projectile.
        
        Args:
            screen: Pygame surface to render on
            projectile: The projectile to render the trail for
        """
        # Calculate the trail position (behind the projectile)
        rad = math.radians(projectile.direction + 180)  # Opposite direction
        trail_length = 12
        
        # Draw a few trail segments with decreasing opacity
        for i in range(3):
            offset = (i + 1) * 4
            trail_x = projectile.x + projectile.width / 2 + math.sin(rad) * offset - 2
            trail_y = projectile.y + projectile.height / 2 - math.cos(rad) * offset - 2
            
            # Create a smaller, semi-transparent circle for the trail
            trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            alpha = 150 - i * 50  # Decreasing opacity
            pygame.draw.circle(trail_surface, (255, 255, 0, alpha), (2, 2), 2)
            
            # Render the trail segment
            screen.blit(trail_surface, (trail_x, trail_y))