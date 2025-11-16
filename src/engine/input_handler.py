"""
Input Handler module for the Tank Game.
This module processes keyboard/mouse events and translates them to game actions.
"""
import pygame


class InputHandler:
    """
    Handles input from the user.
    """
    def __init__(self):
        """Initialize the input handler."""
        self.key_states = {}
        self.previous_key_states = {}
        
    def process_events(self):
        """
        Process keyboard/mouse events.
        Should be called once per frame.
        """
        # Store previous key states
        self.previous_key_states = self.key_states.copy()
        
        # Update key states
        keys = pygame.key.get_pressed()
        self.key_states = {
            'up': keys[pygame.K_UP] or keys[pygame.K_w],
            'down': keys[pygame.K_DOWN] or keys[pygame.K_s],
            'left': keys[pygame.K_LEFT] or keys[pygame.K_a],
            'right': keys[pygame.K_RIGHT] or keys[pygame.K_d],
            'fire': keys[pygame.K_SPACE],
            'escape': keys[pygame.K_ESCAPE],
            'enter': keys[pygame.K_RETURN]
        }
        
    def is_key_pressed(self, key):
        """
        Check if a key is currently pressed.
        
        Args:
            key (str): Key name to check
            
        Returns:
            bool: True if the key is pressed, False otherwise
        """
        return self.key_states.get(key, False)
        
    def is_key_just_pressed(self, key):
        """
        Check if a key was just pressed this frame.
        
        Args:
            key (str): Key name to check
            
        Returns:
            bool: True if the key was just pressed, False otherwise
        """
        return self.key_states.get(key, False) and not self.previous_key_states.get(key, False)