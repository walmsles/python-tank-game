""" 
Example script demonstrating the enemy tank AI behavior.
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
from src.renderers.map_renderer import MapRenderer
from src.renderers.tank_renderer import TankRenderer
from src.renderers.projectile_renderer import ProjectileRenderer
from src.game_objects.player_tank import PlayerTank
from src.game_objects.enemy_tank import EnemyTank
from src.game_objects.projectile import Projectile
from src.engine.input_handler import InputHandler


def main():
    """Main function to demonstrate enemy tank AI behavior."""
    # Create and initialize the game engine
    game_engine = GameEngine(width=800, height=600, title="Enemy Tank AI Example")
    game_engine.initialize()
    
    # Create a map generator
    map_width = 25  # Number of cells horizontally
    map_height = 19  # Number of cells vertically
    map_generator = MapGenerator(map_width, map_height)
    
    # Generate a map
    difficulty = 1
    map_data = map_generator.generate_map(difficulty)
    
    # Set the cell size
    cell_size = 32
    map_data.set_cell_size(cell_size)
    
    # Create renderers
    map_renderer = MapRenderer(game_engine.renderer)
    map_renderer.set_cell_size(cell_size)
    tank_renderer = TankRenderer(game_engine.renderer)
    projectile_renderer = ProjectileRenderer(game_engine.renderer)
    
    # Create an input handler
    input_handler = InputHandler()
    
    # Create a player tank
    player_tank = PlayerTank(400, 300, health=100, speed=5)
    
    # Create enemy tanks with different difficulty levels
    enemy_tanks = [
        EnemyTank(200, 200, difficulty=1),  # Easy
        EnemyTank(600, 200, difficulty=3),  # Medium
        EnemyTank(200, 400, difficulty=5)   # Hard
    ]
    
    # Add tanks to game objects
    game_engine.add_game_object(player_tank)
    for enemy_tank in enemy_tanks:
        game_engine.add_game_object(enemy_tank)
    
    # List to store active projectiles
    projectiles = []
    
    # Custom update function to handle input and game logic
    def custom_update():
        # Process input events
        input_handler.process_events()
        
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
        
        # Check if the player tank is destroyed
        if not player_tank.active:
            print("Game Over - Player Destroyed")
            game_engine.running = False
        
        # Check if all enemy tanks are destroyed
        if not enemy_tanks:
            print("Victory - All Enemies Destroyed")
            game_engine.running = False
    
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
        
        # Display player health
        health_text = f"Player Health: {player_tank.health}"
        health_surface = font.render(health_text, True, (255, 255, 255))
        game_engine.screen.blit(health_surface, (10, 10))
        
        # Display enemy states
        y_offset = 40
        for i, enemy_tank in enumerate(enemy_tanks):
            difficulty_text = f"Enemy {i+1} (Difficulty {enemy_tank.difficulty})"
            state_text = f"State: {enemy_tank.state}, Health: {enemy_tank.health}"
            
            difficulty_surface = font.render(difficulty_text, True, (255, 200, 200))
            state_surface = font.render(state_text, True, (255, 200, 200))
            
            game_engine.screen.blit(difficulty_surface, (10, y_offset))
            game_engine.screen.blit(state_surface, (10, y_offset + 20))
            
            y_offset += 50
        
        # Update the display
        game_engine.renderer.update_display()
    
    # Replace the game engine's update and render methods with our custom ones
    game_engine.update = custom_update
    game_engine.render = custom_render
    
    # Start the game loop
    game_engine.start_game()


if __name__ == "__main__":
    main()