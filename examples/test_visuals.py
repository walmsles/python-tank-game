#!/usr/bin/env python3
"""
Test script for enhanced visuals in the Tank Game.
This script creates a simple test to verify the enhanced renderers work correctly.
"""
import pygame
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.renderers.enhanced_tank_renderer import EnhancedTankRenderer
from src.renderers.enhanced_projectile_renderer import EnhancedProjectileRenderer
from src.renderers.enhanced_map_renderer import EnhancedMapRenderer
from src.renderers.visual_effects_manager import VisualEffectsManager
from src.renderers.renderer import Renderer


def test_enhanced_visuals():
    """Test the enhanced visual components."""
    print("Testing enhanced visuals...")
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Enhanced Visuals Test")
    
    # Create renderer
    renderer = Renderer(screen)
    
    # Create enhanced renderers
    tank_renderer = EnhancedTankRenderer(renderer)
    projectile_renderer = EnhancedProjectileRenderer(renderer)
    map_renderer = EnhancedMapRenderer(renderer)
    visual_effects = VisualEffectsManager()
    
    print("✓ All enhanced renderers created successfully")
    
    # Test sprite creation
    player_sprite = tank_renderer.player_tank_sprite
    enemy_sprite = tank_renderer.enemy_tank_sprite
    projectile_sprite = projectile_renderer.projectile_sprite
    
    if player_sprite and enemy_sprite and projectile_sprite:
        print("✓ Enhanced sprites created successfully")
    else:
        print("✗ Failed to create enhanced sprites")
        return False
    
    # Test visual effects
    visual_effects.add_explosion(400, 300, size=50)
    visual_effects.add_impact(200, 200)
    visual_effects.add_muzzle_flash(100, 100, 0)
    
    if visual_effects.get_effect_count() == 3:
        print("✓ Visual effects system working")
    else:
        print("✗ Visual effects system failed")
        return False
    
    # Test map renderer
    ground_sprites = map_renderer.ground_sprites
    if len(ground_sprites) > 0:
        print("✓ Enhanced map sprites created successfully")
    else:
        print("✗ Failed to create enhanced map sprites")
        return False
    
    print("✓ All enhanced visual tests passed!")
    
    # Quick visual test - render for a few frames
    clock = pygame.time.Clock()
    for frame in range(60):  # 1 second at 60 FPS
        # Clear screen
        screen.fill((50, 100, 50))  # Dark green background
        
        # Update and render visual effects
        visual_effects.update(1/60)  # 60 FPS
        visual_effects.render(screen)
        
        # Render some test sprites
        screen.blit(player_sprite, (100, 100))
        screen.blit(enemy_sprite, (200, 100))
        screen.blit(projectile_sprite, (300, 100))
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
        
        # Check for quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
    
    pygame.quit()
    print("✓ Visual rendering test completed successfully")
    return True


if __name__ == "__main__":
    success = test_enhanced_visuals()
    if success:
        print("\n🎉 All enhanced visual tests passed! The visual improvements are working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some visual tests failed. Please check the implementation.")
        sys.exit(1)