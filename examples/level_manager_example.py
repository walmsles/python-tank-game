"""
Example script demonstrating the level manager functionality.
"""
import pygame
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.game_engine import GameEngine
from src.level_manager.level_manager import LevelManager
from src.renderers.map_renderer import MapRenderer
from src.renderers.tank_renderer import TankRenderer
from src.renderers.projectile_renderer import ProjectileRenderer
from src.game_objects.player_tank import PlayerTank
from src.game_objects.projectile import Projectile
from src.engine.input_handler import InputHandler


def main():
    """Main function to demonstrate level manager functionality."""
    # Create and initialize the game engine
    game_engine = GameEngine(width=800, height=600, title="Level Manager Example")
    game_engine.initialize()
    
    # Create renderers
    map_renderer = MapRenderer(game_engine.renderer)
    tank_renderer = TankRenderer(game_engine.renderer)
    projectile_renderer = ProjectileRenderer(game_engine.renderer)
    
    # Create an input handler
    input_handler = InputHandler()
    
    # Create a player tank
    player_tank = PlayerTank(400, 300, health=100, speed=5)
    game_engine.add_game_object(player_tank)
    
    # Create a level manager
    level_manager = LevelManager(game_engine, max_level=5)
    level_manager.initialize(player_tank)
    
    # List to store active projectiles
    projectiles = []
    
    # Custom update function to handle input and game logic
    def custom_update():
        # Process input events
        input_handler.process_events()
        
        # Check for level change key (L key)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_l]:
            # Start the next level
            level_manager.start_level(level_manager.get_current_level() + 1)
            
        # Check for spawn enemy key (S key)
        if keys[pygame.K_s]:
            # Spawn a single enemy tank
            level_manager.spawn_enemy_tank()
            
        # Check for reset key (R key)
        if keys[pygame.K_r]:
            # Reset the level manager
            level_manager.reset()
            
        # Update the player tank and check for projectile firing
        new_projectile = player_tank.update(game_engine.delta_time, level_manager.map_data, input_handler)
        if new_projectile:
            projectiles.append(new_projectile)
            game_engine.add_game_object(new_projectile)
        
        # Update enemy tanks
        game_objects = [player_tank] + level_manager.enemy_tanks + projectiles
        for enemy_tank in level_manager.enemy_tanks[:]:
            if enemy_tank.active:
                new_projectile = enemy_tank.update(game_engine.delta_time, level_manager.map_data, game_objects)
                if new_projectile:
                    projectiles.append(new_projectile)
                    game_engine.add_game_object(new_projectile)
        
        # Update projectiles and handle collisions
        for projectile in projectiles[:]:  # Create a copy of the list to safely remove items
            if not projectile.active or not projectile.update(game_engine.delta_time, level_manager.map_data):
                # Projectile hit something or expired
                projectiles.remove(projectile)
                game_engine.remove_game_object(projectile)
                continue
                
            # Check for collisions with tanks
            for tank in [player_tank] + level_manager.enemy_tanks:
                if tank.active and projectile.active and tank != projectile.owner and projectile.collides_with(tank):
                    # Damage the tank
                    tank.take_damage(projectile.damage)
                    
                    # Remove the projectile
                    projectile.active = False
                    projectiles.remove(projectile)
                    game_engine.remove_game_object(projectile)
                    break
        
        # Update the level manager
        level_manager.update(game_engine.delta_time)
        
        # Check if the player tank is destroyed
        if not player_tank.active:
            print("Game Over - Player Destroyed")
            game_engine.running = False
    
    # Custom render function to display the map, tanks, and projectiles
    def custom_render():
        game_engine.renderer.clear_screen()
        
        # Render the map
        map_renderer.render_map(game_engine.screen, level_manager.map_data)
        
        # Render the tanks
        if player_tank.active:
            tank_renderer.render_tank(game_engine.screen, player_tank)
        for enemy_tank in level_manager.enemy_tanks:
            tank_renderer.render_tank(game_engine.screen, enemy_tank)
        
        # Render the projectiles
        for projectile in projectiles:
            projectile_renderer.render_projectile(game_engine.screen, projectile)
        
        # Render level transition if active
        level_manager.render_transition(game_engine.screen)
        
        # Render debug information
        font = pygame.font.SysFont(None, 24)
        
        # Display level, score, and controls
        level_text = f"Level: {level_manager.get_current_level()}/{level_manager.get_max_level()}"
        score_text = f"Score: {level_manager.get_score()}"
        controls_text = "Controls: Arrow keys to move, Space to fire, L to increase level, S to spawn enemy, R to reset"
        enemy_count_text = f"Enemy Tanks: {len(level_manager.enemy_tanks)}"
        
        level_surface = font.render(level_text, True, (255, 255, 255))
        score_surface = font.render(score_text, True, (255, 255, 255))
        controls_surface = font.render(controls_text, True, (255, 255, 255))
        enemy_count_surface = font.render(enemy_count_text, True, (255, 255, 255))
        
        game_engine.screen.blit(level_surface, (10, 10))
        game_engine.screen.blit(score_surface, (10, 40))
        game_engine.screen.blit(controls_surface, (10, 70))
        game_engine.screen.blit(enemy_count_surface, (10, 100))
        
        # Update the display
        game_engine.renderer.update_display()
    
    # Replace the game engine's update and render methods with our custom ones
    game_engine.update = custom_update
    game_engine.render = custom_render
    
    # Start the game loop
    game_engine.start_game()


if __name__ == "__main__":
    main()