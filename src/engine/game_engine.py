"""
Game Engine module for the Tank Game.
This is the central component that manages the game loop and coordinates between other components.
Includes performance optimizations for collision detection and rendering.

This module provides a unified GameEngine class that combines the functionality of the original
GameEngine and OptimizedGameEngine classes. It includes features such as:
- Spatial partitioning for efficient collision detection
- Viewport culling for optimized rendering
- Render batching for improved performance
- Performance monitoring and profiling
- Configurable optimization settings

All performance optimizations can be enabled or disabled at runtime to suit different hardware
capabilities and performance requirements.
"""
import pygame
import time
from typing import List, Any, Optional, Dict

from src.renderers import Renderer
from src.engine.game_state_manager import GameStateManager
from src.engine.sound_manager import SoundManager
from src.engine.performance_monitor import PerformanceMonitor, PerformanceProfiler
from src.engine.collision_detector import EnhancedCollisionDetector
from src.renderers.optimized_renderer import OptimizedRenderer


class GameEngine:
    """
    The main game engine class that manages the game loop and coordinates between components.
    Includes performance optimizations for collision detection and rendering.
    
    This class provides a unified interface for game management, including:
    - Game loop management
    - Game object management
    - Rendering with optional optimizations
    - Collision detection with optional spatial partitioning
    - Performance monitoring and profiling
    - Event handling
    
    All performance optimizations can be configured through the set_performance_options method
    or toggled at runtime using keyboard shortcuts (F1-F5).
    """
    def __init__(self, width=800, height=600, title="Tank Game", target_fps=60):
        """
        Initialize the game engine.
        
        Args:
            width (int): Screen width in pixels
            height (int): Screen height in pixels
            title (str): Window title
            target_fps (int): Target frames per second
        """
        # Core properties
        self.width = width
        self.height = height
        self.title = title
        self.running = False
        self.clock = None
        self.screen = None
        self.game_objects = []
        self.current_level = 1
        
        # Timing properties
        self.target_fps = target_fps
        self.frame_time_target = 1.0 / target_fps
        self.delta_time = 0
        self.last_time = 0
        self.last_frame_time = 0
        self.last_update_time = 0
        self.last_render_time = 0
        self.last_collision_time = 0
        
        # Component references
        self.renderer = None
        self.optimized_renderer = None
        self.game_state_manager = None
        self.level_manager = None
        self.sound_manager = None
        self.performance_monitor = None
        self.enhanced_collision_detector = None
        
        # Performance optimization flags - these can be toggled at runtime
        # Spatial partitioning: Divides world into grid for faster collision detection
        self.enable_spatial_partitioning = True
        # Viewport culling: Skip rendering objects outside the visible area
        self.enable_viewport_culling = True
        # Render batching: Group similar sprites to reduce draw calls (disabled by default due to complexity)
        self.enable_render_batching = False
        # Performance monitoring: Collect FPS, frame time, and other metrics for optimization
        self.enable_performance_monitoring = True
        
    def initialize(self):
        """
        Initialize pygame and create the game window.
        Sets up renderers, collision detection, and performance monitoring.
        
        This method performs the following initialization steps:
        1. Initialize pygame and create the game window
        2. Set up the standard renderer
        3. Set up the optimized renderer if available
        4. Initialize the game state manager
        5. Initialize the sound manager
        6. Set up enhanced collision detection if spatial partitioning is enabled
        7. Initialize performance monitoring if enabled
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        
        # Initialize the standard renderer
        self.renderer = Renderer(self.screen, self.target_fps)
        
        # Initialize the optimized renderer if available
        try:
            self.optimized_renderer = OptimizedRenderer(self.screen)
        except (ImportError, AttributeError):
            print("Warning: OptimizedRenderer not available, falling back to standard renderer")
            self.optimized_renderer = None
        
        # Initialize the game state manager
        self.game_state_manager = GameStateManager(self)
        
        # Initialize the sound manager
        self.sound_manager = SoundManager()
        self.sound_manager.load_sounds()
        
        # Initialize enhanced collision detector if spatial partitioning is enabled
        if self.enable_spatial_partitioning:
            try:
                self.enhanced_collision_detector = EnhancedCollisionDetector(
                    world_width=self.width,
                    world_height=self.height
                )
            except (ImportError, AttributeError):
                print("Warning: EnhancedCollisionDetector not available")
                self.enhanced_collision_detector = None
        
        # Initialize performance monitoring if enabled
        if self.enable_performance_monitoring:
            self.performance_monitor = PerformanceMonitor()
            # Toggle performance overlay with F1 key
            pygame.key.set_repeat()
        
        return True
    
    # ============================================================================
    # CONFIGURATION METHODS
    # ============================================================================
    
    def set_performance_options(self, spatial_partitioning=None, viewport_culling=None, 
                              render_batching=None, performance_monitoring=None):
        """
        Configure performance optimization options.
        
        This method allows you to enable or disable various performance optimizations
        at runtime. Each optimization can be controlled independently.
        
        Args:
            spatial_partitioning (bool, optional): Enable/disable spatial partitioning for collision detection.
                                                  When enabled, divides the world into a grid to reduce collision checks.
                                                  Recommended for games with many objects.
            viewport_culling (bool, optional): Enable/disable viewport culling for rendering.
                                              When enabled, objects outside the visible area are not rendered.
                                              Recommended for large worlds or many objects.
            render_batching (bool, optional): Enable/disable render batching for sprites.
                                             When enabled, groups similar sprites together to reduce draw calls.
                                             Recommended for games with many similar sprites.
            performance_monitoring (bool, optional): Enable/disable performance monitoring and profiling.
                                                    When enabled, collects FPS, frame time, and other metrics.
                                                    Slight performance overhead when enabled.
                                                    
        Examples:
            # Enable all optimizations for maximum performance
            engine.set_performance_options(
                spatial_partitioning=True,
                viewport_culling=True,
                render_batching=True,
                performance_monitoring=True
            )
            
            # Disable optimizations for debugging
            engine.set_performance_options(
                spatial_partitioning=False,
                viewport_culling=False,
                render_batching=False
            )
            
            # Enable only collision optimization
            engine.set_performance_options(spatial_partitioning=True)
        """
        if spatial_partitioning is not None:
            self.enable_spatial_partitioning = spatial_partitioning
            
        if viewport_culling is not None:
            self.enable_viewport_culling = viewport_culling
            
        if render_batching is not None:
            self.enable_render_batching = render_batching
            
        if performance_monitoring is not None:
            old_value = self.enable_performance_monitoring
            self.enable_performance_monitoring = performance_monitoring
            
            # Initialize or clean up performance monitor based on new setting
            if performance_monitoring and not old_value:
                self.performance_monitor = PerformanceMonitor()
            elif not performance_monitoring and old_value and self.performance_monitor:
                self.performance_monitor.cleanup()
                self.performance_monitor = None
                
    def start_game(self):
        """
        Start the game loop.
        
        Returns:
            bool: True if the game started successfully, False otherwise
        """
        if not pygame.get_init():
            if not self.initialize():
                return False
                
        self.running = True
        self.game_loop()
        return True
        
    # ============================================================================
    # GAME LOOP METHODS
    # ============================================================================
        
    def game_loop(self):
        """
        Main game loop with performance monitoring.
        Handles timing, updates, rendering, and event processing.
        
        The game loop follows these steps:
        1. Start frame timing for performance monitoring
        2. Handle events (input, quit, etc.)
        3. Calculate delta time for frame-rate independent movement
        4. Check for game state changes (restart, etc.)
        5. Update game state (game objects, level manager, etc.)
        6. Render the current frame
        7. Update performance metrics
        8. Maintain target frame rate
        
        This loop continues until the game is exited.
        """
        while self.running:
            # Start frame timing for performance monitoring
            if self.enable_performance_monitoring and self.performance_monitor:
                self.performance_monitor.start_frame()
                
            # Handle events
            self.handle_events()
            
            if not self.running:
                break
                
            # Calculate delta time for frame-rate independent movement
            # Delta time represents the time elapsed since the last frame
            current_time = time.time()
            if hasattr(self, 'last_frame_time'):
                self.delta_time = current_time - self.last_frame_time
            else:
                # First frame: use default delta time based on target FPS
                self.delta_time = 1.0 / 60.0  # Default to 60 FPS
            self.last_frame_time = current_time
            
            # Check if game state manager requested a restart
            if self.game_state_manager and self.game_state_manager.restart_requested:
                self.restart_game()
                continue
            
            # Update game state
            self.update()
            
            # Render frame
            self.render()
            
            # Update performance metrics for monitoring and optimization
            if self.enable_performance_monitoring and self.performance_monitor:
                # Count only active objects for accurate performance metrics
                active_objects = [obj for obj in self.game_objects if getattr(obj, 'active', True)]
                collision_stats = {}
                
                # Collect collision detection performance data
                if self.enhanced_collision_detector:
                    collision_stats = self.enhanced_collision_detector.get_performance_stats()
                    
                # Collect rendering performance data
                render_stats = {}
                if self.optimized_renderer:
                    render_stats = self.optimized_renderer.get_performance_stats()
                    
                # Combine all performance statistics for comprehensive monitoring
                spatial_grid_stats = collision_stats.copy()
                spatial_grid_stats.update(render_stats)
                
                # Update the performance monitor with current frame metrics
                self.performance_monitor.update_game_metrics(
                    object_count=len(active_objects),
                    collision_checks=collision_stats.get('collision_pairs_checked', 0),
                    spatial_grid_stats=spatial_grid_stats
                )
                
                # Check performance thresholds and log warnings if needed
                if hasattr(self.performance_monitor, 'check_performance_thresholds'):
                    self.performance_monitor.check_performance_thresholds()
                else:
                    # Implement basic threshold checking if the method doesn't exist
                    fps_warning_threshold = getattr(self.performance_monitor, 'fps_warning_threshold', 30)
                    fps_critical_threshold = getattr(self.performance_monitor, 'fps_critical_threshold', 15)
                    
                    if self.performance_monitor.fps < fps_critical_threshold:
                        print(f"CRITICAL: FPS is very low ({self.performance_monitor.fps:.1f})")
                    elif self.performance_monitor.fps < fps_warning_threshold:
                        print(f"WARNING: FPS is below target ({self.performance_monitor.fps:.1f})")
                        
                # Record performance data for profiling if active
                if hasattr(self, 'is_profiling') and self.is_profiling:
                    # Check if profiling duration has elapsed
                    if time.time() - self.profiling_start_time >= self.profiling_duration:
                        self.end_performance_profiling()
            
            # Maintain target frame rate
            self.clock.tick(self.target_fps)
            
    def shutdown(self):
        """
        Clean up resources and quit pygame.
        """
        # Clean up performance monitor
        if self.enable_performance_monitoring and self.performance_monitor:
            self.performance_monitor.cleanup()
            
        # Clean up sound manager
        if self.sound_manager:
            self.sound_manager.cleanup()
            
        pygame.quit()
        
    def restart_game(self):
        """
        Restart the game by resetting game state and level manager.
        """
        # Reset game state
        if self.game_state_manager:
            self.game_state_manager.reset()
            self.game_state_manager.restart_requested = False
            
        # Reset level manager
        if self.level_manager:
            self.level_manager.reset()
            
        # Clear game objects
        self.game_objects = []
        
    def change_level(self, level_number):
        """
        Change to a new level.
        
        Args:
            level_number (int): The level number to change to
        """
        self.current_level = level_number
        # Level change logic will be implemented by the level manager
        
    def cleanup(self):
        """
        Clean up resources.
        """
        if self.enable_performance_monitoring and self.performance_monitor:
            self.performance_monitor.cleanup()
            
        # Additional cleanup can be added here
        
    def __del__(self):
        """
        Destructor to ensure cleanup.
        """
        self.cleanup()
        
    # ============================================================================
    # GAME OBJECT MANAGEMENT METHODS
    # ============================================================================
        
    def add_game_object(self, game_object):
        """
        Add a game object to the engine with optimized tracking for collision detection.
        
        This method adds a game object to the engine's list of managed objects and
        updates the collision detection system if spatial partitioning is enabled.
        
        Args:
            game_object: The game object to add
        """
        # Add the object to the game objects list
        self.game_objects.append(game_object)
        
        # Update collision detector if spatial partitioning is enabled
        if self.enhanced_collision_detector and self.enable_spatial_partitioning:
            # Get only active objects to avoid processing inactive ones
            active_objects = [obj for obj in self.game_objects if getattr(obj, 'active', True)]
            # Update the collision detector with the current set of active objects
            self.enhanced_collision_detector.set_game_objects(active_objects)
            
    def remove_game_object(self, game_object):
        """
        Remove a game object from the engine with optimized tracking for collision detection.
        
        This method removes a game object from the engine's list of managed objects and
        updates the collision detection system if spatial partitioning is enabled.
        
        Args:
            game_object: The game object to remove
        """
        # Remove the object from the game objects list if it exists
        if game_object in self.game_objects:
            self.game_objects.remove(game_object)
            
            # Update collision detector if spatial partitioning is enabled
            if self.enhanced_collision_detector and self.enable_spatial_partitioning:
                # Get only active objects to avoid processing inactive ones
                active_objects = [obj for obj in self.game_objects if getattr(obj, 'active', True)]
                # Update the collision detector with the current set of active objects
                self.enhanced_collision_detector.set_game_objects(active_objects)
                
    def get_game_objects(self, object_type=None):
        """
        Get all game objects or objects of a specific type.
        
        This method returns all game objects managed by the engine, optionally filtered by type.
        
        Args:
            object_type (type, optional): The type of objects to return. If None, returns all objects.
            
        Returns:
            list: List of game objects
        """
        if object_type is None:
            # Return all active game objects
            return [obj for obj in self.game_objects if getattr(obj, 'active', True)]
        else:
            # Return only objects of the specified type
            return [obj for obj in self.game_objects 
                   if isinstance(obj, object_type) and getattr(obj, 'active', True)]
                   
    def get_game_object_count(self, object_type=None):
        """
        Get the count of game objects, optionally filtered by type.
        
        Args:
            object_type (type, optional): The type of objects to count. If None, counts all objects.
            
        Returns:
            int: Number of game objects
        """
        return len(self.get_game_objects(object_type))
        
    def find_game_objects_by_tag(self, tag):
        """
        Find game objects with a specific tag.
        
        This method searches for game objects that have a matching tag attribute.
        Tags are a common way to categorize game objects for easy retrieval.
        
        Args:
            tag (str): The tag to search for
            
        Returns:
            list: List of game objects with the specified tag
        """
        return [obj for obj in self.game_objects 
                if hasattr(obj, 'tag') and obj.tag == tag and getattr(obj, 'active', True)]
                
    def find_game_object_by_property(self, property_name, property_value):
        """
        Find the first game object with a specific property value.
        
        This method searches for game objects that have a matching property value.
        
        Args:
            property_name (str): The name of the property to check
            property_value: The value to match
            
        Returns:
            object: The first game object with the matching property, or None if not found
        """
        for obj in self.game_objects:
            if (hasattr(obj, property_name) and 
                getattr(obj, property_name) == property_value and 
                getattr(obj, 'active', True)):
                return obj
        return None
        
    def add_game_objects(self, game_objects):
        """
        Add multiple game objects at once with optimized tracking.
        
        This method is more efficient than adding objects one by one when adding
        multiple objects, as it only updates the collision detection system once.
        
        Args:
            game_objects (list): List of game objects to add
        """
        # Add all objects to the game objects list
        self.game_objects.extend(game_objects)
        
        # Update collision detector only once after adding all objects
        if self.enhanced_collision_detector and self.enable_spatial_partitioning:
            active_objects = [obj for obj in self.game_objects if getattr(obj, 'active', True)]
            self.enhanced_collision_detector.set_game_objects(active_objects)
            
    def remove_game_objects(self, game_objects):
        """
        Remove multiple game objects at once with optimized tracking.
        
        This method is more efficient than removing objects one by one when removing
        multiple objects, as it only updates the collision detection system once.
        
        Args:
            game_objects (list): List of game objects to remove
        """
        # Remove all objects from the game objects list
        self.game_objects = [obj for obj in self.game_objects if obj not in game_objects]
        
        # Update collision detector only once after removing all objects
        if self.enhanced_collision_detector and self.enable_spatial_partitioning:
            active_objects = [obj for obj in self.game_objects if getattr(obj, 'active', True)]
            self.enhanced_collision_detector.set_game_objects(active_objects)
            
    def update(self):
        """
        Update game state with performance profiling.
        """
        if self.enable_performance_monitoring and self.performance_monitor:
            with PerformanceProfiler(self.performance_monitor, 'update'):
                self._do_update()
        else:
            self._do_update()
            
    def _do_update(self):
        """
        Internal update method that handles game object updates and collision detection.
        """
        # Get map data from level manager if available
        # This is used for collision detection with the map
        map_data = None
        if hasattr(self.level_manager, 'map_data'):
            map_data = self.level_manager.map_data
        
        # Filter active objects to avoid processing inactive ones
        # This improves performance by skipping objects that don't need updates
        active_objects = [obj for obj in self.game_objects if getattr(obj, 'active', True)]
        
        # Enhanced collision detection using spatial partitioning if enabled
        # This significantly reduces the number of collision checks needed
        if self.enhanced_collision_detector and self.enable_spatial_partitioning:
            # Measure collision detection time for performance monitoring
            start_time = time.time()
            
            # Update the collision detector with current active objects
            self.enhanced_collision_detector.set_game_objects(active_objects)
            
            # Handle collisions between objects using spatial partitioning
            # This divides the world into a grid to reduce collision checks
            self.enhanced_collision_detector.handle_collisions()
            
            # Record collision detection time for performance analysis
            self.last_collision_time = time.time() - start_time
            if self.enable_performance_monitoring and self.performance_monitor:
                self.performance_monitor.record_collision_time(self.last_collision_time)
        
        # Update all active game objects
        for game_object in active_objects:
            if hasattr(game_object, 'update'):
                # Use introspection to determine if the object's update method
                # expects map_data as a parameter (for map collision detection)
                # This provides backward compatibility with different object types
                if hasattr(game_object.__class__, 'update') and game_object.__class__.update.__code__.co_argcount > 2:
                    # If it expects map_data, pass it
                    game_object.update(self.delta_time, map_data)
                else:
                    # Otherwise, just pass delta_time
                    game_object.update(self.delta_time)
            
        # Find objects that have been deactivated during this update
        inactive_objects = [obj for obj in self.game_objects if hasattr(obj, 'active') and not obj.active]
        
        # Remove inactive objects from the game objects list
        # This prevents memory leaks and improves performance
        if len(inactive_objects) > 0:
            print(f"Removing {len(inactive_objects)} inactive game objects")
            # Update the game objects list to only include active objects
            self.game_objects = active_objects
            
            # Update collision detector with the new set of active objects
            if self.enhanced_collision_detector and self.enable_spatial_partitioning:
                self.enhanced_collision_detector.set_game_objects(active_objects)
            
        # Update the level manager (handles level transitions, enemy spawning, etc.)
        if self.level_manager:
            self.level_manager.update(self.delta_time)
            
        # Update the game state manager (handles game over, victory screens, etc.)
        if self.game_state_manager:
            self.game_state_manager.update(self.delta_time)
            
    def render(self):
        """
        Render the current frame with performance profiling.
        """
        if self.enable_performance_monitoring and self.performance_monitor:
            with PerformanceProfiler(self.performance_monitor, 'render'):
                self._do_render()
        else:
            self._do_render()
            
    def _do_render(self):
        """
        Internal render method that handles rendering game objects and UI.
        """
        # Use optimized rendering if available and enabled
        # The optimized renderer provides features like viewport culling and batching
        if self.optimized_renderer:
            # Begin the frame - this sets up the rendering context
            # and prepares for batched rendering if enabled
            self.optimized_renderer.begin_frame()
            
            # Get only active objects to avoid rendering inactive ones
            # This improves performance by skipping objects that don't need rendering
            active_objects = [obj for obj in self.game_objects if getattr(obj, 'active', True)]
            
            # Render each game object
            for obj in active_objects:
                if self.enable_render_batching and hasattr(obj, 'sprite'):
                    # Use batched rendering for objects with sprites
                    # This groups similar sprites together to reduce draw calls
                    # and significantly improves rendering performance
                    self.optimized_renderer.render_object_batched(obj)
                else:
                    # Use immediate rendering for objects without sprites
                    # or when batching is disabled
                    self.optimized_renderer.render_object_immediate(obj)
                    
            # End the frame - this finalizes any batched rendering
            # and performs any cleanup needed
            self.optimized_renderer.end_frame()
            
            # Render performance overlay if monitoring is enabled
            # This displays FPS, frame time, object count, etc.
            if self.enable_performance_monitoring and self.performance_monitor:
                self.performance_monitor.render_overlay(self.screen)
                
            # Update the display to show the rendered frame
            self.optimized_renderer.update_display()
        else:
            # Fall back to standard rendering if optimized renderer is not available
            # This provides basic functionality without optimizations
            self.renderer.clear_screen()
            self.renderer.render_game_objects(self.game_objects)
            
            # Render game state UI (score, health, game over screens, etc.)
            if self.game_state_manager:
                self.game_state_manager.render(self.renderer)
            
            # Render performance overlay if monitoring is enabled
            if self.enable_performance_monitoring and self.performance_monitor:
                self.performance_monitor.render_overlay(self.screen)
            
            # Update the display to show the rendered frame
            self.renderer.update_display()
            
    # ============================================================================
    # COLLISION DETECTION METHODS
    # ============================================================================
            
    def configure_collision_detection(self, enable_spatial_partitioning=None, grid_size=None):
        """
        Configure the collision detection system.
        
        Args:
            enable_spatial_partitioning (bool, optional): Enable/disable spatial partitioning
            grid_size (int, optional): Size of the spatial grid cells
        """
        if enable_spatial_partitioning is not None:
            self.enable_spatial_partitioning = enable_spatial_partitioning
            
            # Initialize or clean up enhanced collision detector based on new setting
            if enable_spatial_partitioning and not self.enhanced_collision_detector:
                self.enhanced_collision_detector = EnhancedCollisionDetector(
                    world_width=self.width,
                    world_height=self.height
                )
            elif not enable_spatial_partitioning and self.enhanced_collision_detector:
                self.enhanced_collision_detector = None
                
        # Configure grid size if provided and collision detector exists
        if grid_size is not None and self.enhanced_collision_detector:
            self.enhanced_collision_detector.set_grid_size(grid_size)
            
    def check_collision(self, obj1, obj2):
        """
        Check if two objects are colliding.
        
        Args:
            obj1: First game object
            obj2: Second game object
            
        Returns:
            bool: True if the objects are colliding, False otherwise
        """
        # Use enhanced collision detection if available
        if self.enhanced_collision_detector and self.enable_spatial_partitioning:
            return self.enhanced_collision_detector.check_collision(obj1, obj2)
        else:
            # Basic collision detection using rectangles
            if hasattr(obj1, 'get_rect') and hasattr(obj2, 'get_rect'):
                rect1 = obj1.get_rect()
                rect2 = obj2.get_rect()
                return rect1.colliderect(rect2)
            return False
            
    def get_collision_stats(self):
        """
        Get statistics about collision detection.
        
        Returns:
            dict: Dictionary with collision statistics
        """
        if self.enhanced_collision_detector and self.enable_spatial_partitioning:
            return self.enhanced_collision_detector.get_performance_stats()
        else:
            return {
                "spatial_partitioning": False,
                "collision_pairs_checked": 0,
                "collision_time": self.last_collision_time
            }
            
    # ============================================================================
    # RENDERING METHODS
    # ============================================================================
            
    def configure_rendering(self, enable_viewport_culling=None, enable_render_batching=None):
        """
        Configure rendering optimizations.
        
        Args:
            enable_viewport_culling (bool, optional): Enable/disable viewport culling
            enable_render_batching (bool, optional): Enable/disable render batching
        """
        if enable_viewport_culling is not None:
            self.enable_viewport_culling = enable_viewport_culling
            
        if enable_render_batching is not None:
            self.enable_render_batching = enable_render_batching
            
        # Update renderer settings if optimized renderer is available
        if self.optimized_renderer:
            self.optimized_renderer.set_culling_enabled(self.enable_viewport_culling)
            self.optimized_renderer.set_batching_enabled(self.enable_render_batching)
            
    def is_visible(self, game_object):
        """
        Check if a game object is visible in the viewport.
        
        Args:
            game_object: The game object to check
            
        Returns:
            bool: True if the object is visible, False otherwise
        """
        # Skip culling if disabled
        if not self.enable_viewport_culling:
            return True
            
        # Check if the object has position and size
        if not hasattr(game_object, 'x') or not hasattr(game_object, 'y'):
            return True
            
        if not hasattr(game_object, 'width') or not hasattr(game_object, 'height'):
            return True
            
        # Check if the object is within the viewport
        viewport_margin = 50  # Add margin to prevent pop-in
        
        x_visible = (game_object.x + game_object.width + viewport_margin >= 0 and 
                    game_object.x - viewport_margin <= self.width)
        y_visible = (game_object.y + game_object.height + viewport_margin >= 0 and 
                    game_object.y - viewport_margin <= self.height)
                    
        return x_visible and y_visible
        
    def get_render_stats(self):
        """
        Get statistics about rendering.
        
        Returns:
            dict: Dictionary with rendering statistics
        """
        if self.optimized_renderer:
            return self.optimized_renderer.get_performance_stats()
        else:
            return {
                "viewport_culling": self.enable_viewport_culling,
                "render_batching": self.enable_render_batching,
                "objects_rendered": len([obj for obj in self.game_objects if getattr(obj, 'active', True)]),
                "objects_culled": 0
            }
            
    # ============================================================================
    # PERFORMANCE MONITORING METHODS
    # ============================================================================
            
    def configure_performance_monitoring(self, enable=None, show_overlay=None, 
                                   fps_warning_threshold=None, fps_critical_threshold=None):
        """
        Configure performance monitoring settings.
        
        This method allows you to control various aspects of the performance monitoring system,
        including enabling/disabling monitoring, showing/hiding the overlay, and setting FPS thresholds.
        
        Args:
            enable (bool, optional): Enable/disable performance monitoring. When disabled, 
                                   no performance data is collected and the overlay is hidden.
            show_overlay (bool, optional): Show/hide the performance overlay on screen.
                                         The overlay displays real-time FPS, frame time, and other metrics.
            fps_warning_threshold (float, optional): FPS threshold below which warnings are logged.
                                                   Default is 30 FPS. Set to None to disable warnings.
            fps_critical_threshold (float, optional): FPS threshold below which critical warnings are logged.
                                                     Default is 15 FPS. Set to None to disable critical warnings.
                                                     
        Example:
            # Enable monitoring with custom thresholds
            engine.configure_performance_monitoring(
                enable=True,
                show_overlay=True,
                fps_warning_threshold=45,
                fps_critical_threshold=20
            )
            
            # Disable monitoring completely
            engine.configure_performance_monitoring(enable=False)
        """
        if enable is not None:
            old_value = self.enable_performance_monitoring
            self.enable_performance_monitoring = enable
            
            # Initialize or clean up performance monitor based on new setting
            if enable and not old_value:
                self.performance_monitor = PerformanceMonitor()
            elif not enable and old_value and self.performance_monitor:
                self.performance_monitor.cleanup()
                self.performance_monitor = None
                
        # Configure performance monitor if it exists
        if self.performance_monitor:
            if show_overlay is not None:
                if hasattr(self.performance_monitor, 'set_overlay_visible'):
                    self.performance_monitor.set_overlay_visible(show_overlay)
                else:
                    # If the method doesn't exist, set the attribute directly
                    self.performance_monitor.show_overlay = show_overlay
                
            if fps_warning_threshold is not None:
                if hasattr(self.performance_monitor, 'set_fps_warning_threshold'):
                    self.performance_monitor.set_fps_warning_threshold(fps_warning_threshold)
                else:
                    # Store the threshold for later use in check_performance_thresholds
                    self.performance_monitor.fps_warning_threshold = fps_warning_threshold
                
            if fps_critical_threshold is not None:
                if hasattr(self.performance_monitor, 'set_fps_critical_threshold'):
                    self.performance_monitor.set_fps_critical_threshold(fps_critical_threshold)
                else:
                    # Store the threshold for later use in check_performance_thresholds
                    self.performance_monitor.fps_critical_threshold = fps_critical_threshold
                
    def get_performance_summary(self):
        """
        Get a comprehensive performance summary.
        
        Returns:
            dict: Dictionary with performance metrics including:
                - fps: Current frames per second
                - avg_frame_time_ms: Average frame time in milliseconds
                - min_frame_time_ms: Minimum frame time in milliseconds
                - max_frame_time_ms: Maximum frame time in milliseconds
                - avg_update_time_ms: Average update time in milliseconds
                - avg_render_time_ms: Average render time in milliseconds
                - avg_collision_time_ms: Average collision detection time in milliseconds
                - cpu_usage_percent: CPU usage percentage
                - memory_usage_mb: Memory usage in megabytes
                - memory_usage_percent: Memory usage percentage
                - object_count: Number of active game objects
                - collision_checks: Number of collision checks performed
                - spatial_grid_stats: Statistics about spatial partitioning
                - spatial_partitioning_enabled: Whether spatial partitioning is enabled
                - viewport_culling_enabled: Whether viewport culling is enabled
                - render_batching_enabled: Whether render batching is enabled
                - target_fps: Target frames per second
        """
        if not self.enable_performance_monitoring or not self.performance_monitor:
            return {"performance_monitoring": "disabled"}
            
        summary = self.performance_monitor.get_performance_summary()
        
        # Add engine-specific metrics
        summary.update({
            'spatial_partitioning_enabled': self.enable_spatial_partitioning,
            'viewport_culling_enabled': self.enable_viewport_culling,
            'render_batching_enabled': self.enable_render_batching,
            'target_fps': self.target_fps
        })
        
        return summary
        
    def print_performance_summary(self):
        """
        Print a performance summary to the console.
        Useful for debugging and performance tuning.
        """
        if not self.enable_performance_monitoring or not self.performance_monitor:
            print("Performance monitoring is disabled")
            return
            
        stats = self.get_performance_summary()
        print("\n=== Performance Summary ===")
        print(f"FPS: {stats['fps']:.1f}")
        print(f"Frame Time: {stats['avg_frame_time_ms']:.2f}ms")
        print(f"Update Time: {stats['avg_update_time_ms']:.2f}ms")
        print(f"Render Time: {stats['avg_render_time_ms']:.2f}ms")
        print(f"Collision Time: {stats['avg_collision_time_ms']:.2f}ms")
        print(f"Objects: {stats['object_count']}")
        print(f"Collision Checks: {stats['collision_checks']}")
        print(f"CPU Usage: {stats['cpu_usage_percent']:.1f}%")
        print(f"Memory Usage: {stats['memory_usage_mb']:.1f}MB")
        
        # Print optimization settings
        print("\n=== Optimization Settings ===")
        print(f"Spatial Partitioning: {'Enabled' if stats['spatial_partitioning_enabled'] else 'Disabled'}")
        print(f"Viewport Culling: {'Enabled' if stats['viewport_culling_enabled'] else 'Disabled'}")
        print(f"Render Batching: {'Enabled' if stats['render_batching_enabled'] else 'Disabled'}")
        
        # Print spatial grid stats if available
        if 'spatial_grid_stats' in stats and stats['spatial_grid_stats']:
            grid_stats = stats['spatial_grid_stats']
            print("\n=== Spatial Grid Stats ===")
            for key, value in grid_stats.items():
                if isinstance(value, float):
                    print(f"{key}: {value:.2f}")
                else:
                    print(f"{key}: {value}")
                    
        print("===========================\n")
        
    def get_performance_metrics(self, metric_type=None):
        """
        Get specific performance metrics by type.
        
        Args:
            metric_type (str, optional): Type of metrics to retrieve:
                - 'timing': Frame timing metrics
                - 'system': System resource usage metrics
                - 'game': Game-specific metrics
                - 'optimization': Optimization settings
                - None: All metrics (default)
                
        Returns:
            dict: Dictionary with requested performance metrics
        """
        if not self.enable_performance_monitoring or not self.performance_monitor:
            return {"performance_monitoring": "disabled"}
            
        all_metrics = self.get_performance_summary()
        
        if metric_type is None:
            return all_metrics
            
        if metric_type == 'timing':
            return {
                'fps': all_metrics['fps'],
                'avg_frame_time_ms': all_metrics['avg_frame_time_ms'],
                'min_frame_time_ms': all_metrics['min_frame_time_ms'],
                'max_frame_time_ms': all_metrics['max_frame_time_ms'],
                'avg_update_time_ms': all_metrics['avg_update_time_ms'],
                'avg_render_time_ms': all_metrics['avg_render_time_ms'],
                'avg_collision_time_ms': all_metrics['avg_collision_time_ms']
            }
        elif metric_type == 'system':
            return {
                'cpu_usage_percent': all_metrics['cpu_usage_percent'],
                'memory_usage_mb': all_metrics['memory_usage_mb'],
                'memory_usage_percent': all_metrics.get('memory_usage_percent', 0)
            }
        elif metric_type == 'game':
            return {
                'object_count': all_metrics['object_count'],
                'collision_checks': all_metrics['collision_checks'],
                'spatial_grid_stats': all_metrics.get('spatial_grid_stats', {})
            }
        elif metric_type == 'optimization':
            return {
                'spatial_partitioning_enabled': all_metrics['spatial_partitioning_enabled'],
                'viewport_culling_enabled': all_metrics['viewport_culling_enabled'],
                'render_batching_enabled': all_metrics['render_batching_enabled'],
                'target_fps': all_metrics['target_fps']
            }
        else:
            return {'error': f"Unknown metric type: {metric_type}"}
            
    def start_performance_profiling(self, duration_seconds=10):
        """
        Start detailed performance profiling for a specified duration.
        Results will be printed to console when complete.
        
        Args:
            duration_seconds (int): Duration of profiling in seconds
            
        Returns:
            bool: True if profiling started, False otherwise
        """
        if not self.enable_performance_monitoring or not self.performance_monitor:
            print("Performance monitoring is disabled")
            return False
            
        print(f"Starting performance profiling for {duration_seconds} seconds...")
        
        # Store initial state
        self.profiling_start_time = time.time()
        self.profiling_duration = duration_seconds
        self.is_profiling = True
        
        # Store initial metrics for comparison
        self.profiling_initial_metrics = self.get_performance_summary()
        
        # Create a thread to end profiling after the specified duration
        def end_profiling():
            time.sleep(duration_seconds)
            if self.is_profiling:
                self.end_performance_profiling()
                
        import threading
        profiling_thread = threading.Thread(target=end_profiling)
        profiling_thread.daemon = True
        profiling_thread.start()
        
        return True
        
    def end_performance_profiling(self):
        """
        End performance profiling and print results.
        
        Returns:
            dict: Dictionary with profiling results
        """
        if not hasattr(self, 'is_profiling') or not self.is_profiling:
            print("No profiling session in progress")
            return {}
            
        self.is_profiling = False
        
        # Get final metrics
        final_metrics = self.get_performance_summary()
        
        # Calculate elapsed time
        elapsed_time = time.time() - self.profiling_start_time
        
        # Print profiling results
        print(f"\n=== Performance Profiling Results ({elapsed_time:.1f}s) ===")
        print(f"Average FPS: {final_metrics['fps']:.1f}")
        print(f"Frame Time: {final_metrics['avg_frame_time_ms']:.2f}ms (min: {final_metrics['min_frame_time_ms']:.2f}ms, max: {final_metrics['max_frame_time_ms']:.2f}ms)")
        update_pct = (final_metrics['avg_update_time_ms'] / final_metrics['avg_frame_time_ms'] * 100)
        render_pct = (final_metrics['avg_render_time_ms'] / final_metrics['avg_frame_time_ms'] * 100)
        collision_pct = (final_metrics['avg_collision_time_ms'] / final_metrics['avg_frame_time_ms'] * 100)
        
        print(f"Update Time: {final_metrics['avg_update_time_ms']:.2f}ms ({update_pct:.1f}% of frame)")
        print(f"Render Time: {final_metrics['avg_render_time_ms']:.2f}ms ({render_pct:.1f}% of frame)")
        print(f"Collision Time: {final_metrics['avg_collision_time_ms']:.2f}ms ({collision_pct:.1f}% of frame)")
        print(f"Objects: {final_metrics['object_count']}")
        print(f"Collision Checks: {final_metrics['collision_checks']}")
        print(f"CPU Usage: {final_metrics['cpu_usage_percent']:.1f}%")
        print(f"Memory Usage: {final_metrics['memory_usage_mb']:.1f}MB")
        
        # Compare with initial metrics
        if hasattr(self, 'profiling_initial_metrics'):
            initial = self.profiling_initial_metrics
            print("\n=== Changes During Profiling ===")
            print(f"FPS: {initial['fps']:.1f} → {final_metrics['fps']:.1f} ({final_metrics['fps'] - initial['fps']:.1f})")
            frame_time_change = final_metrics['avg_frame_time_ms'] - initial['avg_frame_time_ms']
            object_change = final_metrics['object_count'] - initial['object_count']
            memory_change = final_metrics['memory_usage_mb'] - initial['memory_usage_mb']
            
            print(f"Frame Time: {initial['avg_frame_time_ms']:.2f}ms → {final_metrics['avg_frame_time_ms']:.2f}ms ({frame_time_change:.2f}ms)")
            print(f"Objects: {initial['object_count']} → {final_metrics['object_count']} ({object_change})")
            print(f"Memory Usage: {initial['memory_usage_mb']:.1f}MB → {final_metrics['memory_usage_mb']:.1f}MB ({memory_change:.1f}MB)")
            
        print("=======================================\n")
        
        # Return profiling results
        return {
            'duration_seconds': elapsed_time,
            'initial_metrics': getattr(self, 'profiling_initial_metrics', {}),
            'final_metrics': final_metrics
        }
        
    # ============================================================================
    # EVENT HANDLING METHODS
    # ============================================================================
        
    def handle_events(self):
        """
        Handle pygame events with performance monitoring controls.
        
        This method processes pygame events and provides built-in keyboard shortcuts
        for toggling performance monitoring features. It's designed to be called once
        per frame in the main game loop.
        
        Built-in Keyboard Shortcuts:
        - F1: Toggle performance overlay (shows/hides FPS, frame time, etc.)
        - F2: Toggle spatial partitioning (enables/disables optimized collision detection)
        - F3: Toggle viewport culling (enables/disables off-screen object culling)
        - F4: Toggle render batching (enables/disables sprite batching for performance)
        - F5: Print performance summary to console
        - F6: Start/stop performance profiling (10-second detailed analysis)
        - F7: Toggle performance monitoring on/off
        - ESC: Quit the game
        
        The method also handles:
        - Game state events (restart requests from game state manager)
        - Quit events (pygame.QUIT)
        - Custom event handlers registered via register_event_handler()
        
        Note:
            Performance shortcuts only work when performance monitoring is enabled.
            Game-specific events should be handled in the process_events() method.
        """
        events = pygame.event.get()
        
        # Process events for game state manager (for restart functionality)
        if self.game_state_manager:
            restart_requested = self.game_state_manager.process_events(events)
            if restart_requested:
                print("Restart requested - restarting game!")
                self.restart_game()
                return
        
        # Handle other events
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F1 and self.enable_performance_monitoring and self.performance_monitor:
                    # Toggle performance overlay
                    if hasattr(self.performance_monitor, 'toggle_overlay'):
                        self.performance_monitor.toggle_overlay()
                    else:
                        # If the method doesn't exist, toggle the attribute directly
                        self.performance_monitor.show_overlay = not getattr(self.performance_monitor, 'show_overlay', False)
                    print(f"Performance overlay: {'ON' if getattr(self.performance_monitor, 'show_overlay', False) else 'OFF'}")
                elif event.key == pygame.K_F2:
                    # Toggle spatial partitioning
                    self.enable_spatial_partitioning = not self.enable_spatial_partitioning
                    print(f"Spatial partitioning: {'ON' if self.enable_spatial_partitioning else 'OFF'}")
                    
                    # Update collision detector if needed
                    if self.enable_spatial_partitioning and not self.enhanced_collision_detector:
                        self.enhanced_collision_detector = EnhancedCollisionDetector(
                            world_width=self.width,
                            world_height=self.height
                        )
                    elif not self.enable_spatial_partitioning and self.enhanced_collision_detector:
                        self.enhanced_collision_detector = None
                elif event.key == pygame.K_F3:
                    # Toggle viewport culling
                    self.enable_viewport_culling = not self.enable_viewport_culling
                    print(f"Viewport culling: {'ON' if self.enable_viewport_culling else 'OFF'}")
                    
                    # Update renderer settings if available
                    if self.optimized_renderer:
                        self.optimized_renderer.set_culling_enabled(self.enable_viewport_culling)
                elif event.key == pygame.K_F4:
                    # Toggle render batching
                    self.enable_render_batching = not self.enable_render_batching
                    print(f"Render batching: {'ON' if self.enable_render_batching else 'OFF'}")
                    
                    # Update renderer settings if available
                    if self.optimized_renderer:
                        self.optimized_renderer.set_batching_enabled(self.enable_render_batching)
                elif event.key == pygame.K_F5:
                    # Print performance summary
                    if self.enable_performance_monitoring and self.performance_monitor:
                        self.print_performance_summary()
                    else:
                        print("Performance monitoring is disabled")
                elif event.key == pygame.K_F6:
                    # Start/stop performance profiling
                    if self.enable_performance_monitoring and self.performance_monitor:
                        if hasattr(self, 'is_profiling') and self.is_profiling:
                            print("Stopping performance profiling...")
                            self.end_performance_profiling()
                        else:
                            self.start_performance_profiling(10)  # 10 seconds profiling
                    else:
                        print("Performance monitoring is disabled")
                elif event.key == pygame.K_F7:
                    # Toggle performance monitoring
                    self.enable_performance_monitoring = not self.enable_performance_monitoring
                    print(f"Performance monitoring: {'ON' if self.enable_performance_monitoring else 'OFF'}")
                    
                    # Initialize or clean up performance monitor based on new setting
                    if self.enable_performance_monitoring and not self.performance_monitor:
                        self.performance_monitor = PerformanceMonitor()
                    elif not self.enable_performance_monitoring and self.performance_monitor:
                        self.performance_monitor.cleanup()
                        self.performance_monitor = None
                elif event.key == pygame.K_F3:
                    # Toggle viewport culling
                    self.enable_viewport_culling = not self.enable_viewport_culling
                    print(f"Viewport culling: {'ON' if self.enable_viewport_culling else 'OFF'}")
                elif event.key == pygame.K_F4:
                    # Toggle render batching
                    self.enable_render_batching = not self.enable_render_batching
                    print(f"Render batching: {'ON' if self.enable_render_batching else 'OFF'}")
                elif event.key == pygame.K_F5:
                    # Print performance summary
                    self.print_performance_summary()
                    
        # Process events for custom handlers
        self.process_events(events)
                    
    def process_events(self, events=None):
        """
        Process pygame events for game-specific handling.
        
        Args:
            events (list, optional): List of pygame events to process. If None, get events from pygame.
        """
        if events is None:
            events = pygame.event.get()
            
        # Let the game state manager process events
        if self.game_state_manager:
            self.game_state_manager.process_events(events)
            
        # Additional event processing can be added here
        
    def register_event_handler(self, event_type, handler):
        """
        Register a custom event handler.
        
        Args:
            event_type (int): Pygame event type
            handler (callable): Function to call when the event occurs
        """
        # This is a placeholder for a more sophisticated event handling system
        # In a real implementation, you would store the handler and call it when the event occurs
        pass