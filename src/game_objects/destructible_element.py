"""
Destructible Element module for the Tank Game.
This module defines the DestructibleElement class that represents destructible obstacles.
"""
from src.engine.game_object import GameObject


class DestructibleElement(GameObject):
    """
    Represents a destructible obstacle in the game map.
    """
    def __init__(self, x, y, health=100):
        """
        Initialize a destructible element.
        
        Args:
            x (float): X-coordinate position
            y (float): Y-coordinate position
            health (int): Initial health of the element
        """
        super().__init__(x, y)
        # Set default destructible element dimensions (32x32 pixels)
        self.width = 32
        self.height = 32
        self.health = health
        self.max_health = health
        self.destructible = True
        self.tag = "destructible"
        self.damaged_sprite = None
        
    def take_damage(self, amount):
        """
        Reduce the health of the element by the given amount.
        
        Args:
            amount (int): Amount of damage to take
            
        Returns:
            bool: True if the element was destroyed, False otherwise
        """
        old_health = self.health
        self.health -= amount
        
        print(f"DestructibleElement at ({self.x}, {self.y}) took {amount} damage. Health: {old_health} -> {self.health}")
        
        # Update sprite based on health
        if self.health <= 0:
            self.health = 0  # Ensure health doesn't go below 0
            self.active = False  # Mark as inactive/destroyed
            print(f"DestructibleElement at ({self.x}, {self.y}) destroyed!")
            return True
        elif self.health <= self.max_health / 2 and self.damaged_sprite:
            self.sprite = self.damaged_sprite
            print(f"DestructibleElement at ({self.x}, {self.y}) damaged, updating sprite")
            
        return False
        
    def set_damaged_sprite(self, sprite):
        """
        Set the sprite to use when the element is damaged.
        
        Args:
            sprite: Pygame surface to use as damaged sprite
        """
        self.damaged_sprite = sprite
        
    def update_map_data(self, map_data):
        """
        Update the map data when this destructible element is destroyed.
        
        Args:
            map_data: The map data to update
            
        Returns:
            bool: True if the map data was updated, False otherwise
        """
        if not self.active and map_data:
            # Convert object position to cell coordinates
            cell_x = int((self.x + self.width / 2) // map_data.cell_size)
            cell_y = int((self.y + self.height / 2) // map_data.cell_size)
            
            # Check if the cell is within bounds
            if 0 <= cell_x < map_data.width and 0 <= cell_y < map_data.height:
                # Update the map data to reflect that the cell is now empty
                map_data.set_cell(cell_x, cell_y, map_data.EMPTY)
                print(f"Updated map data at ({cell_x}, {cell_y}) to EMPTY")
                return True
                
        return False
        
    def render(self, screen):
        """
        Render the destructible element on the screen.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.active:
            return
            
        # Call the parent render method
        super().render(screen)
        
        # Optionally, we could add a health bar or other visual indicators here
        # For now, the visual state is handled by switching between normal and damaged sprites