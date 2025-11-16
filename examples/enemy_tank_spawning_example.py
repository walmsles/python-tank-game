"""
Example script demonstrating the enemy tank spawning functionality.
"""
import pygame
import sys
import os
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.game_engine import GameEngine
from src.level_manager.map_generator import MapGenerator
from src.level_manager.map_data import MapData
from src.level_manager.enemy_tank_spawner import EnemyTankSpawner
from src.renderers.map_renderer import MapRenderer
from src.renderers.tank_renderer import TankRenderer
from src.renderers.projectile_renderer import ProjectileRenderer
from src.game_objects.player_tank import PlayerTank
from src.game_objects.enemy_tank import EnemyTank
from src.game_objects.projectile import Projectile
from src.engine.input_handler import InputHandler


def main():
    """Main function to demonstrate enemy tank spawning."""
    # Create and initialize the game engine
    game_engine = GameEngine(width=800, height=600, title="Enemy Tank Spawning Example")
    game_engine.initialize()
    
    # Create a map generator
    map_width = 25  # Number of cells horizontally
    map_height = 19  # Number of cells vertically
    map_generator = MapGenerator(map_width, map_height)
    
    # Create renderers
    map_renderer = MapRenderer(game_engine.renderer)
    tank_renderer = TankRenderer(game_engine.renderer)
    projectile_renderer = ProjectileRenderer(game_engine.renderer)
    
    # Create an input handler
    input_handler = InputHandler()
    
    # Create a player tank
    player_tank = PlayerTank(400, 300, health=100, speed=5)
    game_engine.add_game_object(player_tank)
    
    # List to store active projectiles
    projectiles = []
    
    # Current level
    current_level = 1
    
    # Function to start a new level
    def start_level(level):
        nonlocal current_level, enemy_tanks
        
        # Update current level
        current_level = level
        
        # Generate a new map
        map_data = map_generator.generate_map(difficulty=level)
        
        # Set the cell size
        cell_size = 32
        map_data.set_cell_size(cell_size)
        map_renderer.set_cell_size(cell_size)
        
        # Clear existing enemy tanks
        for tank in enemy_tanks:
            game_engine.remove_game_object(tank)
        enemy_tanks = []
        
        # Create an enemy tank spawner
        spawner = EnemyTankSpawner(map_data)
        
        # Spawn enemy tanks
        player_position = (player_tank.x, player_tank.y)
        enemy_tanks = spawner.spawn_enemy_tanks(level, player_position, game_engine)
        
        # Return the map data
        return map_data
    
    # Initialize enemy tanks list
    enemy_tanks = []
    
    # Start the first level
    map_data = start_level(current_level)
    
    # Custom update function to handle input and game logic
    def custom_update():
        nonlocal current_level, map_data
        
        # Process input events
        input_handler.process_events()
        
        # Check for level change key (L key)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_l]:
            # Increase level and start a new level
            current_level += 1
            map_data = start_level(current_level)
            
        # Check for spawn enemy key (S key)
        if keys[pygame.K_s]:
            # Create an enemy tank spawner
            spawner = EnemyTankSpawner(map_data)
            
            # Spawn a single enemy tank
            player_position = (player_tank.x, player_tank.y)
            enemy_tank = spawner.spawn_single_enemy_tank(random.randint(1, 5), player_position, game_engine)
            
            if enemy_tank:
                enemy_tanks.append(enemy_tank)
        
        # Update the player tank and check for projectile firing
        new_projectile = player_tank.update(game_engine.delta_time, map_data, input_handler)
        if new_projectile:
            projectiles.append(new_projectile)
            game_engine.add_game_object(new_projectile)
        
        # Update enemy tanks
        game_objects = [player_tank] + enemy_tanks + projectiles
        for enemy_tank in enemy_tanks[:]:
            if enemy_tank.active:
                new_projectile = enemy_tank.update(game_engine.delta_time, map_data, game_objects)
                if new_projectile:
                    projectiles.append(new_projectile)
                    game_engine.add_game_object(new_projectile)
            else:
                enemy_tanks.remove(enemy_tank)
                game_engine.remove_game_object(enemy_tank)
        
        # Update projectiles and handle collisions
        for projectile in projectiles[:]:  # Create a copy of the list to safely remove items
            if not projectile.active or not projectile.update(game_engine.delta_time, map_data):
                # Projectile hit something or expired
                projectiles.remove(projectile)
                game_engine.remove_game_object(projectile)
                continue
                
            # Check for collisions with tanks
            for tank in [player_tank] + enemy_tanks:
                if tank.active and projectile.active and tank != projectile.owner and projectile.collides_with(tank):
                    # Damage the tank
                    tank.take_damage(projectile.damage)
                    
                    # Remove the projectile
                    projectile.active = False
                    projectiles.remove(projectile)
                    game_engine.remove_game_object(projectile)
                    break
        
        # Check if all enemy tanks are destroyed
        if not enemy_tanks:
            print(f"Level {current_level} completed!")
            # Start the next level
            current_level += 1
            map_data = start_level(current_level)
    
    # Custom render function to display the map, tanks, and projectiles
    def custom_render():
        game_engine.renderer.clear_screen()
        
        # Render the map
        map_renderer.render_map(game_engine.screen, map_data)
        
        # Render the tanks
        if player_tank.active:
            tank_renderer.render_tank(game_engine.screen, player_tank)
        for enemy_tank in enemy_tanks:
            tank_renderer.render_tank(game_engine.screen, enemy_tank)
        
        # Render the projectiles
        for projectile in projectiles:
            projectile_renderer.render_projectile(game_engine.screen, projectile)
        
        # Render debug information
        font = pygame.font.SysFont(None, 24)
        
        # Display level and controls
        level_text = f"Level: {current_level}"
        controls_text = "Controls: Arrow keys to move, Space to fire, L to increase level, S to spawn enemy"
        enemy_count_text = f"Enemy Tanks: {len(enemy_tanks)}"
        
        level_surface = font.render(level_text, True, (255, 255, 255))
        controls_surface = font.render(controls_text, True, (255, 255, 255))
        enemy_count_surface = font.render(enemy_count_text, True, (255, 255, 255))
        
        game_engine.screen.blit(level_surface, (10, 10))
        game_engine.screen.blit(controls_surface, (10, 40))
        game_engine.screen.blit(enemy_count_surface, (10, 70))
        
        # Update the display
        game_engine.renderer.update_display()
    
    # Replace the game engine's update and render methods with our custom ones
    game_engine.update = custom_update
    game_engine.render = custom_render
    
    # Start the game loop
    game_engine.start_game()


if __name__ == "__main__":
    main()