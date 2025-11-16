"""
Example script demonstrating the rendering system.
"""
import pygame
import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.game_engine import GameEngine
from src.engine.game_object import GameObject


class MovingObject(GameObject):
    """A simple moving game object for demonstration."""
    
    def __init__(self, x, y, color, speed_x, speed_y):
        """Initialize the moving object."""
        super().__init__(x, y)
        self.width = 32
        self.height = 32
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = color
        
    def update(self, delta_time):
        """Update the object position."""
        self.x += self.speed_x * delta_time
        self.y += self.speed_y * delta_time
        
        # Bounce off the edges of the screen
        if self.x < 0 or self.x + self.width > 800:
            self.speed_x = -self.speed_x
        if self.y < 0 or self.y + self.height > 600:
            self.speed_y = -self.speed_y


def main():
    """Main function to demonstrate the rendering system."""
    # Create and initialize the game engine
    game_engine = GameEngine(width=800, height=600, title="Rendering Example")
    game_engine.initialize()
    
    # Disable spatial partitioning for this simple example
    game_engine.set_performance_options(spatial_partitioning=False)
    
    # Create some moving objects with different colors and speeds
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
    ]
    
    for i in range(10):
        # Create a moving object with random position and speed
        obj = MovingObject(
            x=400,
            y=300,
            color=colors[i % len(colors)],
            speed_x=(i - 5) * 50,
            speed_y=(i - 5) * 30
        )
        
        # Create a sprite for the object
        sprite = game_engine.renderer.create_simple_sprite(
            f"obj_{i}",
            32,
            32,
            obj.color
        )
        obj.set_sprite(sprite)
        
        # Add the object to the game engine
        game_engine.add_game_object(obj)
    
    # Start the game loop
    game_engine.start_game()


if __name__ == "__main__":
    main()