"""
Game Objects package for the Tank Game.

This package contains all game object classes used in the Tank Game.
"""

from src.game_objects.game_object import GameObject
from src.game_objects.destructible_element import DestructibleElement
from src.game_objects.wall import Wall
from src.game_objects.rock_pile import RockPile

__all__ = ["GameObject", "DestructibleElement", "Wall", "RockPile"]