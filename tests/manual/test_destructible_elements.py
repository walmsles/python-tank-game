"""
Manual test script for destructible elements.
This script creates a simple game environment with destructible elements and allows the user to fire projectiles at them.
"""
import pygame
import sys
import os
import math
import random

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.engine.game_engine import GameEngine
from src.game_objects.rock_pile import RockPile
from src.game_objects.petrol_barrel import PetrolBarrel
from src.game_objects.projectile import Projectile
from src.level_manager.map_data import MapData
from src.game_objects.player_tank import PlayerTank


class TestGame:
    """A simple test game for destructible elements."""
    
    def __init__(self):
        """Initialize the test game."""
        # Initialize pygame
        pygame.init()
        
        # Create a game engine
        self.game_engine = GameEngine(width=800, height=600, title="Destructible Elements Test")
        
        # Create a map data object
        self.map_data = MapData(25, 19)  # 800/32 = 25, 600/32 = 18.75
        self.map_data.cell_size = 32
        
        # Create a mock level manager
        self.level_manager = type('MockLevelManager', (), {'map_data': self.map_data})()
        
        # Set the level manager on the game engine
        self.game_engine.level_manager = self.level_manager
        
        # Initialize the game engine
        self.game_engine.initialize()
        
        # Create game objects
        self.create_game_objects()
        
        # Set up the map data
        self.setup_map_data()
        
        # Set up the player tank
        self.setup_player_tank()
        
        # Set up the clock
        self.clock = pygame.time.Clock()
        
        # Set up the font
        self.font = pygame.font.SysFont('Arial', 16)
        
        # Set up the game state
        self.running = True
    
    def create_game_objects(self):
        """Create game objects."""
        # Create rock piles
        self.rock_piles = []
        for _ in range(10):
            x = random.randint(2, 22) * 32
            y = random.randint(2, 16) * 32
            rock_pile = RockPile(x, y, health=75)
            rock_pile.width = 32
            rock_pile.height = 32
            self.rock_piles.append(rock_pile)
            self.game_engine.add_game_object(rock_pile)
        
        # Create petrol barrels
        self.petrol_barrels = []
        for _ in range(5):
            x = random.randint(2, 22) * 32
            y = random.randint(2, 16) * 32
            petrol_barrel = PetrolBarrel(x, y, health=50)
            petrol_barrel.width = 32
            petrol_barrel.height = 32
            self.petrol_barrels.append(petrol_barrel)
            self.game_engine.add_game_object(petrol_barrel)
        
        # Create projectiles list
        self.projectiles = []
    
    def setup_map_data(self):
        """Set up the map data."""
        # Add walls around the edges
        for x in range(self.map_data.width):
            self.map_data.set_cell(x, 0, MapData.WALL)
            self.map_data.set_cell(x, self.map_data.height - 1, MapData.WALL)
        
        for y in range(self.map_data.height):
            self.map_data.set_cell(0, y, MapData.WALL)
            self.map_data.set_cell(self.map_data.width - 1, y, MapData.WALL)
        
        # Add rock piles to map data
        for rock_pile in self.rock_piles:
            cell_x = int(rock_pile.x // self.map_data.cell_size)
            cell_y = int(rock_pile.y // self.map_data.cell_size)
            self.map_data.set_cell(cell_x, cell_y, MapData.ROCK_PILE)
        
        # Add petrol barrels to map data
        for petrol_barrel in self.petrol_barrels:
            cell_x = int(petrol_barrel.x // self.map_data.cell_size)
            cell_y = int(petrol_barrel.y // self.map_data.cell_size)
            self.map_data.set_cell(cell_x, cell_y, MapData.PETROL_BARREL)
    
    def setup_player_tank(self):
        """Set up the player tank."""
        # Create a player tank
        self.player_tank = PlayerTank(400, 300)
        self.player_tank.width = 32
        self.player_tank.height = 32
        
        # Add player tank to game objects
        self.game_engine.add_game_object(self.player_tank)
        
        # Create a simple sprite for the player tank
        self.player_tank.sprite = pygame.Surface((32, 32))
        self.player_tank.sprite.fill((0, 0, 255))  # Blue tank
        
        # Create simple sprites for rock piles
        for rock_pile in self.rock_piles:
            rock_pile.sprite = pygame.Surface((32, 32))
            rock_pile.sprite.fill((128, 128, 128))  # Gray rock pile
            
            # Create damaged sprite
            rock_pile.damaged_sprite = pygame.Surface((32, 32))
            rock_pile.damaged_sprite.fill((100, 100, 100))  # Darker gray for damaged rock pile
        
        # Create simple sprites for petrol barrels
        for petrol_barrel in self.petrol_barrels:
            petrol_barrel.sprite = pygame.Surface((32, 32))
            petrol_barrel.sprite.fill((255, 0, 0))  # Red petrol barrel
            
            # Create damaged sprite
            petrol_barrel.damaged_sprite = pygame.Surface((32, 32))
            petrol_barrel.damaged_sprite.fill((200, 0, 0))  # Darker red for damaged petrol barrel
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.fire_projectile()
    
    def handle_input(self):
        """Handle keyboard input."""
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_w]:
            self.player_tank.move_forward(0.016, self.map_data)
            self.player_tank.is_moving = True
        elif keys[pygame.K_s]:
            self.player_tank.move_backward(0.016, self.map_data)
            self.player_tank.is_moving = True
        else:
            self.player_tank.is_moving = False
        
        # Rotation
        if keys[pygame.K_a]:
            self.player_tank.rotate_left(0.016)
        elif keys[pygame.K_d]:
            self.player_tank.rotate_right(0.016)
    
    def fire_projectile(self):
        """Fire a projectile from the player tank."""
        projectile = self.player_tank.fire()
        if projectile:
            # Create a simple sprite for the projectile
            projectile.sprite = pygame.Surface((8, 8))
            projectile.sprite.fill((255, 255, 0))  # Yellow projectile
            projectile.width = 8
            projectile.height = 8
            
            # Add projectile to game objects and projectiles list
            self.game_engine.add_game_object(projectile)
            self.projectiles.append(projectile)
    
    def update(self):
        """Update the game state."""
        # Handle events
        self.handle_events()
        
        # Handle input
        self.handle_input()
        
        # Update the game engine
        self.game_engine.update()
        
        # Remove inactive projectiles from the projectiles list
        self.projectiles = [p for p in self.projectiles if p.active]
    
    def render(self):
        """Render the game."""
        # Render the game engine
        self.game_engine.render()
        
        # Render the map grid
        self.render_map_grid()
        
        # Render the instructions
        self.render_instructions()
        
        # Update the display
        pygame.display.flip()
    
    def render_map_grid(self):
        """Render the map grid."""
        # Get the screen
        screen = self.game_engine.screen
        
        # Draw grid lines
        for x in range(0, self.map_data.width * self.map_data.cell_size, self.map_data.cell_size):
            pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, self.map_data.height * self.map_data.cell_size))
        
        for y in range(0, self.map_data.height * self.map_data.cell_size, self.map_data.cell_size):
            pygame.draw.line(screen, (50, 50, 50), (0, y), (self.map_data.width * self.map_data.cell_size, y))
    
    def render_instructions(self):
        """Render the instructions."""
        # Get the screen
        screen = self.game_engine.screen
        
        # Create the instructions text
        instructions = [
            "WASD: Move/Rotate",
            "Space: Fire",
            "Esc: Quit",
            f"Rock Piles: {len([rp for rp in self.rock_piles if rp.active])}/10",
            f"Petrol Barrels: {len([pb for pb in self.petrol_barrels if pb.active])}/5",
            f"Projectiles: {len(self.projectiles)}"
        ]
        
        # Render the instructions
        y = 10
        for instruction in instructions:
            text = self.font.render(instruction, True, (255, 255, 255))
            screen.blit(text, (10, y))
            y += 20
    
    def run(self):
        """Run the game loop."""
        while self.running:
            # Update the game
            self.update()
            
            # Render the game
            self.render()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        # Quit pygame
        pygame.quit()


if __name__ == "__main__":
    # Create and run the test game
    test_game = TestGame()
    test_game.run()