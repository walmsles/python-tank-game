"""
Example script demonstrating the map generation and rendering.
"""
import pygame
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.game_engine import GameEngine
from src.level_manager.map_generator import MapGenerator
from src.level_manager.map_data import MapData
from src.renderers.map_renderer import MapRenderer
from src.game_objects.destructible_element import DestructibleElement


def main():
    """Main function to demonstrate map generation and rendering."""
    # Create and initialize the game engine
    game_engine = GameEngine(width=800, height=600, title="Open Field Map Generation Example")
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
    
    # Create a map renderer
    map_renderer = MapRenderer(game_engine.renderer)
    map_renderer.set_cell_size(cell_size)
    
    # Add destructible elements as game objects
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
                
                # Add to game engine
                game_engine.add_game_object(destructible)
            
            elif map_data.is_petrol_barrel_at(x, y):
                # Convert cell coordinates to pixel coordinates
                pixel_x, pixel_y = map_data.get_pixel_position(x, y)
                
                # Create a destructible element
                destructible = DestructibleElement(pixel_x, pixel_y, health=50)
                
                # Set sprites
                destructible.set_sprite(map_renderer.petrol_barrel_sprite)
                destructible.set_damaged_sprite(map_renderer.petrol_barrel_damaged_sprite)
                
                # Add to game engine
                game_engine.add_game_object(destructible)
    
    # Custom render function to display the map
    def custom_render():
        game_engine.renderer.clear_screen()
        
        # Render the map
        map_renderer.render_map(game_engine.screen, map_data)
        
        # Render game objects (destructible elements)
        game_engine.renderer.render_game_objects(game_engine.game_objects)
        
        # Update the display
        game_engine.renderer.update_display()
    
    # Replace the game engine's render method with our custom one
    game_engine.render = custom_render
    
    # Start the game loop
    game_engine.start_game()


if __name__ == "__main__":
    main()