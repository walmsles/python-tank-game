"""
Game State Manager module for the Tank Game.
This module defines the GameStateManager class that manages the game state.
"""
import pygame


class GameStateManager:
    """
    Manages the game state, including score, game over conditions, and restart functionality.
    """
    def __init__(self, game_engine):
        """
        Initialize the game state manager.
        
        Args:
            game_engine (GameEngine): The game engine instance
        """
        self.game_engine = game_engine
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.victory = False
        self.show_game_over_screen = False
        self.show_victory_screen = False
        self.restart_requested = False
        
    def update(self, delta_time):
        """
        Update the game state.
        
        Args:
            delta_time (float): Time elapsed since the last update in seconds
        """
        # Check for player death
        player_tank = self._get_player_tank()
        if player_tank and not player_tank.active:
            self.game_over = True
            self.show_game_over_screen = True
            
        # Check for victory (handled by level manager)
        level_manager = self._get_level_manager()
        if level_manager and level_manager.is_game_complete():
            self.victory = True
            self.show_victory_screen = True
            
        # Update score from level manager
        if level_manager:
            self.score = level_manager.get_score()
            self.current_level = level_manager.get_current_level()
            self.max_level = level_manager.get_max_level()
            
        # Update high score if needed
        if self.score > self.high_score:
            self.high_score = self.score
            
    def render(self, renderer):
        """
        Render the game state UI elements.
        
        Args:
            renderer (Renderer): The renderer to use
        """
        # Get the screen dimensions
        screen_width = renderer.screen.get_width()
        screen_height = renderer.screen.get_height()
        
        # Render score
        level_manager = self._get_level_manager()
        if level_manager:
            score_text = f"Score: {level_manager.get_score()}"
            renderer.render_text(score_text, None, 24, (255, 255, 255), 10, 10)
            
            # Render current level
            level_text = f"Level: {level_manager.get_current_level()}/{level_manager.get_max_level()}"
            renderer.render_text(level_text, None, 24, (255, 255, 255), 10, 40)
        
        # Render game over screen
        if self.show_game_over_screen:
            # Semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
            renderer.screen.blit(overlay, (0, 0))
            
            # Game over text
            renderer.render_text("GAME OVER", None, 48, (255, 0, 0), screen_width // 2, screen_height // 2 - 50, centered=True)
            
            # Final score
            if level_manager:
                final_score_text = f"Final Score: {level_manager.get_score()}"
                renderer.render_text(final_score_text, None, 36, (255, 255, 255), screen_width // 2, screen_height // 2, centered=True)
                
                # High score
                high_score_text = f"High Score: {self.high_score}"
                renderer.render_text(high_score_text, None, 24, (255, 255, 255), screen_width // 2, screen_height // 2 + 40, centered=True)
            
            # Restart instructions
            renderer.render_text("Press R to Restart", None, 24, (255, 255, 255), screen_width // 2, screen_height // 2 + 100, centered=True)
            
        # Render victory screen
        if self.show_victory_screen:
            # Semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
            renderer.screen.blit(overlay, (0, 0))
            
            # Victory text
            renderer.render_text("VICTORY!", None, 48, (0, 255, 0), screen_width // 2, screen_height // 2 - 50, centered=True)
            
            # Final score
            if level_manager:
                final_score_text = f"Final Score: {level_manager.get_score()}"
                renderer.render_text(final_score_text, None, 36, (255, 255, 255), screen_width // 2, screen_height // 2, centered=True)
                
                # High score
                high_score_text = f"High Score: {self.high_score}"
                renderer.render_text(high_score_text, None, 24, (255, 255, 255), screen_width // 2, screen_height // 2 + 40, centered=True)
            
            # Restart instructions
            renderer.render_text("Press R to Play Again", None, 24, (255, 255, 255), screen_width // 2, screen_height // 2 + 100, centered=True)
            
    def process_events(self, events):
        """
        Process events for the game state manager.
        
        Args:
            events (list): List of pygame events to process
            
        Returns:
            bool: True if the game should restart, False otherwise
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.show_game_over_screen or self.show_victory_screen):
                    self.restart_requested = True
                    return True
                    
        return False
        
    def reset(self):
        """
        Reset the game state.
        """
        self.game_over = False
        self.victory = False
        self.show_game_over_screen = False
        self.show_victory_screen = False
        self.restart_requested = False
        
    def _get_player_tank(self):
        """
        Get the player tank from the game objects.
        
        Returns:
            PlayerTank: The player tank, or None if not found
        """
        for game_object in self.game_engine.game_objects:
            if hasattr(game_object, 'tag') and game_object.tag == "player":
                return game_object
                
        return None
        
    def _get_level_manager(self):
        """
        Get the level manager from the game engine.
        
        Returns:
            LevelManager: The level manager, or None if not found
        """
        if hasattr(self.game_engine, 'level_manager'):
            return self.game_engine.level_manager
            
        return None