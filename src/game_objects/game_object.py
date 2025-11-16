"""
GameObject base class for the Tank Game.

This module defines the base GameObject class that all game entities will inherit from.
It provides common functionality like position tracking, updating, and rendering.
"""

class GameObject:
    """
    Base class for all game objects.
    
    This class provides common functionality for all game objects including
    position tracking, updating, and rendering.
    """
    
    def __init__(self, x=0, y=0):
        """
        Initialize a new GameObject.
        
        Args:
            x (float): Initial x-coordinate position
            y (float): Initial y-coordinate position
        """
        self.x = x
        self.y = y
        self.sprite = None
    
    def update(self, delta_time):
        """
        Update the game object's state.
        
        This method should be overridden by subclasses to implement
        specific update behavior.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
        """
        pass
    
    def render(self, screen):
        """
        Render the game object to the screen.
        
        This method should be overridden by subclasses to implement
        specific rendering behavior.
        
        Args:
            screen: The screen surface to render to
        """
        if self.sprite:
            screen.blit(self.sprite, (self.x, self.y))
    
    def set_position(self, x, y):
        """
        Set the position of the game object.
        
        Args:
            x (float): New x-coordinate position
            y (float): New y-coordinate position
        """
        self.x = x
        self.y = y
    
    def get_position(self):
        """
        Get the current position of the game object.
        
        Returns:
            tuple: A tuple containing the (x, y) coordinates
        """
        return (self.x, self.y)