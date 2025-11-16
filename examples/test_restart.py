#!/usr/bin/env python3
"""
Test script to check restart functionality
"""
import pygame
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.engine.game_state_manager import GameStateManager
from src.engine.game_engine import GameEngine

def test_restart():
    """Test the restart functionality"""
    pygame.init()
    
    # Create a minimal game engine
    game_engine = GameEngine()
    game_engine.initialize()
    
    # Create game state manager
    game_state_manager = GameStateManager(game_engine)
    
    # Simulate game over state
    game_state_manager.show_game_over_screen = True
    
    print("Game over screen active:", game_state_manager.show_game_over_screen)
    print("Testing R key press...")
    
    # Create a fake R key press event
    r_key_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
    events = [r_key_event]
    
    # Process the event
    result = game_state_manager.process_events(events)
    
    print("Restart requested:", game_state_manager.restart_requested)
    print("Process events returned:", result)
    
    pygame.quit()

if __name__ == "__main__":
    test_restart()