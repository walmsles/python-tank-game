"""
Example script demonstrating the tank rendering and projectile firing.
"""
import pygame
import sys
import os
import math
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
from src.game_objects.tank import Tank
from src.game_objects.projectile import Projectile
from src.game_objects.destructible_element import DestructibleElement
from src.engine.input_handler import InputHandler


def main():
    """Main function to demonstrate tank rendering and projectile firing."""
    # Create and initialize the game engine
    game_engine = GameEngine(width=800, height=600, title="Tank Game Example")
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
    
    # Create some enemy tanks
    enemy_tanks = [
        Tank(200, 200, health=80, speed=4),
        Tank(600, 200, health=60, speed=4),
        Tank(200, 400, health=40, speed=4),
        Tank(600, 400, health=20, speed=4)
    ]
    
    # Set enemy tank tags
    for enemy_tank in enemy_tanks:
        enemy_tank.tag = "enemy"
    
    # Add tanks to game objects
    game_engine.add_game_object(player_tank)
    for enemy_tank in enemy_tanks:
        game_engine.add_game_object(enemy_tank)
    
    # Add destructible elements
    destructible_elements = []
    for y in range(map_data.height):
        for x in range(map_data.width):
            if map_data.is_rock_pile_at(x, y):
                # Convert cell coordinates to pixel coordinates
                pixel_x, pixel_y = map_data.get_pixel_position(x, y)
                
                # Create a destructible element
                destructible = DestructibleElement(pixel_x, pixel_y, health=100)
                
                # Set sprites
                destructible.set_sprite(map_renderer.rock_pile_sprite)
                destructible.set_damaged_sprite(map_renderer.rock_pile_damaged_sprite)
                
                # Add to list and game engine
                destructible_elements.append(destructible)
                game_engine.add_game_object(destructible)
            
            elif map_data.is_petrol_barrel_at(x, y):
                # Convert cell coordinates to pixel coordinates
                pixel_x, pixel_y = map_data.get_pixel_position(x, y)
                
                # Create a destructible element
                destructible = DestructibleElement(pixel_x, pixel_y, health=50)
                
                # Set sprites
                destructible.set_sprite(map_renderer.petrol_barrel_sprite)
                destructible.set_damaged_sprite(map_renderer.petrol_barrel_damaged_sprite)
                
                # Add to list and game engine
                destructible_elements.append(destructible)
                game_engine.add_game_object(destructible)
    
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
        
        # Make enemy tanks rotate and occasionally fire
        for i, enemy_tank in enumerate(enemy_tanks):
            # Rotate at different speeds
            enemy_tank.rotate_left(game_engine.delta_time * (i + 1) * 0.5)
            enemy_tank.update(game_engine.delta_time, map_data)
            
            # Occasionally fire (about once every 3 seconds)
            if enemy_tank.active and random.random() < game_engine.delta_time / 3:
                new_projectile = enemy_tank.fire()
                if new_projectile:
                    projectiles.append(new_projectile)
        
        # Update projectiles and handle collisions
        for projectile in projectiles[:]:  # Create a copy of the list to safely remove items
            if not projectile.update(game_engine.delta_time, map_data):
                # Projectile hit something or expired
                projectiles.remove(projectile)
                continue
                
            # Check for collisions with tanks
            for tank in [player_tank] + enemy_tanks:
                if tank.active and projectile.active and tank != projectile.owner and projectile.collides_with(tank):
                    # Damage the tank
                    tank.take_damage(projectile.damage)
                    
                    # Remove the projectile
                    projectile.active = False
                    projectiles.remove(projectile)
                    break
                    
            # Check for collisions with destructible elements
            if projectile.active:
                for destructible in destructible_elements:
                    if destructible.active and projectile.collides_with(destructible):
                        # Damage the destructible element
                        destroyed = destructible.take_damage(projectile.damage)
                        
                        # If it was a petrol barrel and it was destroyed, damage nearby objects
                        if destroyed and destructible.sprite == map_renderer.petrol_barrel_sprite:
                            # Explosion radius
                            explosion_radius = 64
                            
                            # Get the center of the barrel
                            barrel_center_x = destructible.x + destructible.width / 2
                            barrel_center_y = destructible.y + destructible.height / 2
                            
                            # Damage nearby tanks
                            for tank in [player_tank] + enemy_tanks:
                                if tank.active:
                                    # Get the center of the tank
                                    tank_center_x = tank.x + tank.width / 2
                                    tank_center_y = tank.y + tank.height / 2
                                    
                                    # Calculate distance
                                    dx = barrel_center_x - tank_center_x
                                    dy = barrel_center_y - tank_center_y
                                    distance = math.sqrt(dx * dx + dy * dy)
                                    
                                    # If the tank is within the explosion radius, damage it
                                    if distance < explosion_radius:
                                        # Damage decreases with distance
                                        damage = int(50 * (1 - distance / explosion_radius))
                                        tank.take_damage(damage)
                            
                            # Damage nearby destructible elements
                            for other_destructible in destructible_elements:
                                if other_destructible.active and other_destructible != destructible:
                                    # Get the center of the destructible element
                                    other_center_x = other_destructible.x + other_destructible.width / 2
                                    other_center_y = other_destructible.y + other_destructible.height / 2
                                    
                                    # Calculate distance
                                    dx = barrel_center_x - other_center_x
                                    dy = barrel_center_y - other_center_y
                                    distance = math.sqrt(dx * dx + dy * dy)
                                    
                                    # If the destructible element is within the explosion radius, damage it
                                    if distance < explosion_radius:
                                        # Damage decreases with distance
                                        damage = int(50 * (1 - distance / explosion_radius))
                                        other_destructible.take_damage(damage)
                        
                        # Remove the projectile
                        projectile.active = False
                        projectiles.remove(projectile)
                        break
        
        # Remove destroyed tanks
        for tank in enemy_tanks[:]:
            if not tank.active:
                enemy_tanks.remove(tank)
                game_engine.remove_game_object(tank)
        
        # Remove destroyed destructible elements
        for destructible in destructible_elements[:]:
            if not destructible.active:
                destructible_elements.remove(destructible)
                game_engine.remove_game_object(destructible)
        
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
        
        # Update the display
        game_engine.renderer.update_display()
    
    # Replace the game engine's update and render methods with our custom ones
    game_engine.update = custom_update
    game_engine.render = custom_render
    
    # Start the game loop
    game_engine.start_game()


if __name__ == "__main__":
    main()