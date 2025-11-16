"""
Optimized Renderer module for the Tank Game.
This module provides optimized rendering with culling, batching, and performance improvements.
"""
import pygame
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict


class RenderBatch:
    """
    Represents a batch of similar objects that can be rendered together.
    """
    
    def __init__(self, sprite: pygame.Surface, blend_mode: int = 0):
        """
        Initialize a render batch.
        
        Args:
            sprite: The sprite texture for this batch
            blend_mode: Pygame blend mode for rendering
        """
        self.sprite = sprite
        self.blend_mode = blend_mode
        self.positions = []  # List of (x, y) positions
        self.rotations = []  # List of rotation angles (if applicable)
        self.scales = []     # List of scale factors (if applicable)
        self.colors = []     # List of color tints (if applicable)
        
    def add_instance(self, x: float, y: float, rotation: float = 0, 
                    scale: float = 1.0, color: Tuple[int, int, int] = (255, 255, 255)):
        """
        Add an instance to this batch.
        
        Args:
            x: X position
            y: Y position
            rotation: Rotation angle in degrees
            scale: Scale factor
            color: Color tint
        """
        self.positions.append((x, y))
        self.rotations.append(rotation)
        self.scales.append(scale)
        self.colors.append(color)
        
    def clear(self):
        """Clear all instances from this batch."""
        self.positions.clear()
        self.rotations.clear()
        self.scales.clear()
        self.colors.clear()
        
    def is_empty(self) -> bool:
        """Check if this batch has no instances."""
        return len(self.positions) == 0


class ViewportCuller:
    """
    Handles viewport culling to avoid rendering objects outside the visible area.
    """
    
    def __init__(self, screen_width: int, screen_height: int, margin: int = 50):
        """
        Initialize the viewport culler.
        
        Args:
            screen_width: Width of the screen/viewport
            screen_height: Height of the screen/viewport
            margin: Extra margin around viewport for culling (to handle partially visible objects)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin = margin
        
        # Viewport bounds with margin
        self.left = -margin
        self.right = screen_width + margin
        self.top = -margin
        self.bottom = screen_height + margin
        
    def is_visible(self, x: float, y: float, width: float, height: float) -> bool:
        """
        Check if an object is visible within the viewport.
        
        Args:
            x: Object X position
            y: Object Y position
            width: Object width
            height: Object height
            
        Returns:
            True if the object is visible, False otherwise
        """
        # Check if object bounds intersect with viewport bounds
        obj_right = x + width
        obj_bottom = y + height
        
        return not (obj_right < self.left or x > self.right or 
                   obj_bottom < self.top or y > self.bottom)
                   
    def update_viewport(self, screen_width: int, screen_height: int):
        """
        Update viewport dimensions.
        
        Args:
            screen_width: New screen width
            screen_height: New screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.right = screen_width + self.margin
        self.bottom = screen_height + self.margin


class OptimizedRenderer:
    """
    Optimized renderer with batching, culling, and performance improvements.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the optimized renderer.
        
        Args:
            screen: Pygame surface to render to
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Viewport culling
        self.culler = ViewportCuller(self.screen_width, self.screen_height)
        
        # Render batches organized by sprite/texture
        self.batches: Dict[str, RenderBatch] = {}
        
        # Sprite cache to avoid repeated loading/creation
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        
        # Layer system for rendering order
        self.layers: Dict[int, List[Any]] = defaultdict(list)
        
        # Performance tracking
        self.objects_rendered = 0
        self.objects_culled = 0
        self.batches_rendered = 0
        
        # Dirty rectangle tracking for partial screen updates
        self.dirty_rects = []
        self.use_dirty_rects = False  # Can be enabled for further optimization
        
    def clear_screen(self, color: Tuple[int, int, int] = (0, 0, 0)):
        """
        Clear the screen with the specified color.
        
        Args:
            color: RGB color tuple
        """
        self.screen.fill(color)
        self.dirty_rects.clear()
        
    def begin_frame(self):
        """Begin a new rendering frame."""
        # Clear all batches
        for batch in self.batches.values():
            batch.clear()
            
        # Clear layers
        self.layers.clear()
        
        # Reset performance counters
        self.objects_rendered = 0
        self.objects_culled = 0
        self.batches_rendered = 0
        
    def add_to_layer(self, layer: int, obj: Any):
        """
        Add an object to a specific rendering layer.
        
        Args:
            layer: Layer number (lower numbers render first)
            obj: Object to render
        """
        self.layers[layer].append(obj)
        
    def get_or_create_batch(self, sprite_key: str, sprite: pygame.Surface, 
                          blend_mode: int = 0) -> RenderBatch:
        """
        Get or create a render batch for the given sprite.
        
        Args:
            sprite_key: Unique key for the sprite
            sprite: Sprite surface
            blend_mode: Pygame blend mode
            
        Returns:
            RenderBatch for the sprite
        """
        if sprite_key not in self.batches:
            self.batches[sprite_key] = RenderBatch(sprite, blend_mode)
        return self.batches[sprite_key]
        
    def render_object_batched(self, obj: Any, layer: int = 0, sprite_key: Optional[str] = None):
        """
        Add an object to be rendered using batching.
        
        Args:
            obj: Game object to render
            layer: Rendering layer
            sprite_key: Optional sprite key for batching
        """
        # Check if object is visible
        obj_width = getattr(obj, 'width', 32)
        obj_height = getattr(obj, 'height', 32)
        
        if not self.culler.is_visible(obj.x, obj.y, obj_width, obj_height):
            self.objects_culled += 1
            return
            
        # Use sprite key or generate one
        if sprite_key is None:
            sprite_key = f"{type(obj).__name__}_{getattr(obj, 'tag', 'default')}"
            
        # Get sprite from object
        sprite = getattr(obj, 'sprite', None)
        if sprite is None:
            return
            
        # Add to appropriate batch
        batch = self.get_or_create_batch(sprite_key, sprite)
        
        # Get object properties
        rotation = getattr(obj, 'direction', 0)
        scale = getattr(obj, 'scale', 1.0)
        color = getattr(obj, 'color', (255, 255, 255))
        
        batch.add_instance(obj.x, obj.y, rotation, scale, color)
        self.objects_rendered += 1
        
    def render_object_immediate(self, obj: Any):
        """
        Render an object immediately without batching.
        
        Args:
            obj: Game object to render
        """
        # Check if object is visible
        obj_width = getattr(obj, 'width', 32)
        obj_height = getattr(obj, 'height', 32)
        
        if not self.culler.is_visible(obj.x, obj.y, obj_width, obj_height):
            self.objects_culled += 1
            return
            
        # Render the object directly
        if hasattr(obj, 'render'):
            obj.render(self.screen)
            self.objects_rendered += 1
            
            # Track dirty rectangle if enabled
            if self.use_dirty_rects:
                self.dirty_rects.append(pygame.Rect(obj.x, obj.y, obj_width, obj_height))
                
    def render_sprite_at(self, sprite: pygame.Surface, x: float, y: float, 
                        rotation: float = 0, scale: float = 1.0, 
                        color: Tuple[int, int, int] = (255, 255, 255),
                        blend_mode: int = 0):
        """
        Render a sprite at the specified position with transformations.
        
        Args:
            sprite: Sprite to render
            x: X position
            y: Y position
            rotation: Rotation angle in degrees
            scale: Scale factor
            color: Color tint
            blend_mode: Pygame blend mode
        """
        # Check visibility
        sprite_width = sprite.get_width() * scale
        sprite_height = sprite.get_height() * scale
        
        if not self.culler.is_visible(x, y, sprite_width, sprite_height):
            return
            
        # Apply transformations
        transformed_sprite = sprite
        
        # Apply scaling
        if scale != 1.0:
            new_width = int(sprite.get_width() * scale)
            new_height = int(sprite.get_height() * scale)
            if new_width > 0 and new_height > 0:
                transformed_sprite = pygame.transform.scale(transformed_sprite, (new_width, new_height))
                
        # Apply rotation
        if rotation != 0:
            transformed_sprite = pygame.transform.rotate(transformed_sprite, -rotation)
            
        # Apply color tint
        if color != (255, 255, 255):
            transformed_sprite = transformed_sprite.copy()
            transformed_sprite.fill(color, special_flags=pygame.BLEND_MULT)
            
        # Calculate centered position after transformations
        final_x = x - transformed_sprite.get_width() // 2 + sprite.get_width() // 2
        final_y = y - transformed_sprite.get_height() // 2 + sprite.get_height() // 2
        
        # Render the sprite
        if blend_mode != 0:
            self.screen.blit(transformed_sprite, (final_x, final_y), special_flags=blend_mode)
        else:
            self.screen.blit(transformed_sprite, (final_x, final_y))
            
    def render_all_batches(self):
        """Render all accumulated batches."""
        for sprite_key, batch in self.batches.items():
            if batch.is_empty():
                continue
                
            self.batches_rendered += 1
            
            # Render all instances in the batch
            for i in range(len(batch.positions)):
                x, y = batch.positions[i]
                rotation = batch.rotations[i] if i < len(batch.rotations) else 0
                scale = batch.scales[i] if i < len(batch.scales) else 1.0
                color = batch.colors[i] if i < len(batch.colors) else (255, 255, 255)
                
                self.render_sprite_at(batch.sprite, x, y, rotation, scale, color, batch.blend_mode)
                
    def render_layers(self):
        """Render all objects organized by layers."""
        # Sort layers by key (lower numbers first)
        for layer_num in sorted(self.layers.keys()):
            objects = self.layers[layer_num]
            
            # Render objects in this layer
            for obj in objects:
                self.render_object_immediate(obj)
                
    def end_frame(self):
        """End the current rendering frame."""
        # Render all batches
        self.render_all_batches()
        
        # Render layered objects
        self.render_layers()
        
    def update_display(self):
        """Update the display."""
        if self.use_dirty_rects and self.dirty_rects:
            # Update only dirty rectangles
            pygame.display.update(self.dirty_rects)
        else:
            # Update entire display
            pygame.display.flip()
            
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get rendering performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'objects_rendered': self.objects_rendered,
            'objects_culled': self.objects_culled,
            'batches_rendered': self.batches_rendered,
            'total_batches': len(self.batches),
            'active_layers': len(self.layers),
            'dirty_rects': len(self.dirty_rects) if self.use_dirty_rects else 0
        }
        
    def enable_dirty_rect_optimization(self, enabled: bool = True):
        """
        Enable or disable dirty rectangle optimization.
        
        Args:
            enabled: Whether to enable dirty rectangle tracking
        """
        self.use_dirty_rects = enabled
        
    def resize_viewport(self, width: int, height: int):
        """
        Resize the viewport for culling calculations.
        
        Args:
            width: New viewport width
            height: New viewport height
        """
        self.screen_width = width
        self.screen_height = height
        self.culler.update_viewport(width, height)
        
    def cache_sprite(self, key: str, sprite: pygame.Surface):
        """
        Cache a sprite for reuse.
        
        Args:
            key: Unique key for the sprite
            sprite: Sprite surface to cache
        """
        self.sprite_cache[key] = sprite
        
    def get_cached_sprite(self, key: str) -> Optional[pygame.Surface]:
        """
        Get a cached sprite.
        
        Args:
            key: Sprite key
            
        Returns:
            Cached sprite surface or None if not found
        """
        return self.sprite_cache.get(key)
        
    def clear_sprite_cache(self):
        """Clear the sprite cache."""
        self.sprite_cache.clear()


class RenderQueue:
    """
    A render queue for organizing rendering commands by priority and type.
    """
    
    def __init__(self):
        """Initialize the render queue."""
        self.commands = []
        
    def add_command(self, priority: int, render_func, *args, **kwargs):
        """
        Add a rendering command to the queue.
        
        Args:
            priority: Rendering priority (lower numbers render first)
            render_func: Function to call for rendering
            *args: Arguments for the render function
            **kwargs: Keyword arguments for the render function
        """
        self.commands.append((priority, render_func, args, kwargs))
        
    def execute_all(self):
        """Execute all rendering commands in priority order."""
        # Sort by priority
        self.commands.sort(key=lambda x: x[0])
        
        # Execute commands
        for priority, render_func, args, kwargs in self.commands:
            render_func(*args, **kwargs)
            
        # Clear the queue
        self.commands.clear()
        
    def clear(self):
        """Clear all commands from the queue."""
        self.commands.clear()