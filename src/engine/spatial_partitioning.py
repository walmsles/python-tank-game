"""
Spatial Partitioning module for the Tank Game.
This module implements spatial partitioning to optimize collision detection.
"""
import math
from typing import List, Set, Tuple, Dict, Any


class SpatialGrid:
    """
    A spatial grid for efficient collision detection using spatial partitioning.
    Divides the game world into a grid of cells and tracks which objects are in each cell.
    """
    
    def __init__(self, world_width: int, world_height: int, cell_size: int = 64):
        """
        Initialize the spatial grid.
        
        Args:
            world_width: Width of the game world
            world_height: Height of the game world
            cell_size: Size of each grid cell (larger = fewer cells, less precision)
        """
        self.world_width = world_width
        self.world_height = world_height
        self.cell_size = cell_size
        
        # Calculate grid dimensions
        self.grid_width = math.ceil(world_width / cell_size)
        self.grid_height = math.ceil(world_height / cell_size)
        
        # Grid storage: each cell contains a set of object IDs
        self.grid: Dict[Tuple[int, int], Set[int]] = {}
        
        # Object tracking: maps object ID to its current grid cells
        self.object_cells: Dict[int, Set[Tuple[int, int]]] = {}
        
        # Object registry: maps object ID to the actual object
        self.objects: Dict[int, Any] = {}
        
    def _get_grid_coords(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert world coordinates to grid coordinates.
        
        Args:
            x: World X coordinate
            y: World Y coordinate
            
        Returns:
            Tuple of (grid_x, grid_y)
        """
        grid_x = max(0, min(self.grid_width - 1, int(x // self.cell_size)))
        grid_y = max(0, min(self.grid_height - 1, int(y // self.cell_size)))
        return (grid_x, grid_y)
        
    def _get_object_cells(self, obj: Any) -> Set[Tuple[int, int]]:
        """
        Get all grid cells that an object occupies.
        
        Args:
            obj: Game object with x, y, width, height attributes
            
        Returns:
            Set of grid cell coordinates the object occupies
        """
        cells = set()
        
        # Get object bounds
        left = obj.x
        right = obj.x + getattr(obj, 'width', 32)
        top = obj.y
        bottom = obj.y + getattr(obj, 'height', 32)
        
        # Find all cells the object overlaps
        start_x, start_y = self._get_grid_coords(left, top)
        end_x, end_y = self._get_grid_coords(right - 1, bottom - 1)
        
        for grid_x in range(start_x, end_x + 1):
            for grid_y in range(start_y, end_y + 1):
                cells.add((grid_x, grid_y))
                
        return cells
        
    def add_object(self, obj: Any) -> None:
        """
        Add an object to the spatial grid.
        
        Args:
            obj: Game object to add
        """
        obj_id = id(obj)
        self.objects[obj_id] = obj
        
        # Get cells the object occupies
        cells = self._get_object_cells(obj)
        self.object_cells[obj_id] = cells
        
        # Add object to each cell
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = set()
            self.grid[cell].add(obj_id)
            
    def remove_object(self, obj: Any) -> None:
        """
        Remove an object from the spatial grid.
        
        Args:
            obj: Game object to remove
        """
        obj_id = id(obj)
        
        if obj_id not in self.object_cells:
            return
            
        # Remove object from all its cells
        for cell in self.object_cells[obj_id]:
            if cell in self.grid:
                self.grid[cell].discard(obj_id)
                # Clean up empty cells
                if not self.grid[cell]:
                    del self.grid[cell]
                    
        # Clean up object tracking
        del self.object_cells[obj_id]
        if obj_id in self.objects:
            del self.objects[obj_id]
            
    def update_object(self, obj: Any) -> None:
        """
        Update an object's position in the spatial grid.
        
        Args:
            obj: Game object that has moved
        """
        obj_id = id(obj)
        
        if obj_id not in self.object_cells:
            # Object not in grid, add it
            self.add_object(obj)
            return
            
        # Get new cells the object occupies
        new_cells = self._get_object_cells(obj)
        old_cells = self.object_cells[obj_id]
        
        # If cells haven't changed, no update needed
        if new_cells == old_cells:
            return
            
        # Remove from old cells that are no longer occupied
        for cell in old_cells - new_cells:
            if cell in self.grid:
                self.grid[cell].discard(obj_id)
                if not self.grid[cell]:
                    del self.grid[cell]
                    
        # Add to new cells
        for cell in new_cells - old_cells:
            if cell not in self.grid:
                self.grid[cell] = set()
            self.grid[cell].add(obj_id)
            
        # Update object's cell tracking
        self.object_cells[obj_id] = new_cells
        
    def get_nearby_objects(self, obj: Any) -> List[Any]:
        """
        Get all objects that could potentially collide with the given object.
        
        Args:
            obj: Game object to find nearby objects for
            
        Returns:
            List of nearby objects (excluding the object itself)
        """
        obj_id = id(obj)
        nearby_ids = set()
        
        # Get cells the object occupies
        cells = self._get_object_cells(obj)
        
        # Collect all objects in those cells
        for cell in cells:
            if cell in self.grid:
                nearby_ids.update(self.grid[cell])
                
        # Remove the object itself and return actual objects
        nearby_ids.discard(obj_id)
        return [self.objects[obj_id] for obj_id in nearby_ids if obj_id in self.objects]
        
    def get_objects_in_region(self, x: float, y: float, width: float, height: float) -> List[Any]:
        """
        Get all objects in a specific rectangular region.
        
        Args:
            x: Left edge of region
            y: Top edge of region
            width: Width of region
            height: Height of region
            
        Returns:
            List of objects in the region
        """
        objects_in_region = set()
        
        # Find all cells that overlap with the region
        start_x, start_y = self._get_grid_coords(x, y)
        end_x, end_y = self._get_grid_coords(x + width - 1, y + height - 1)
        
        for grid_x in range(start_x, end_x + 1):
            for grid_y in range(start_y, end_y + 1):
                cell = (grid_x, grid_y)
                if cell in self.grid:
                    objects_in_region.update(self.grid[cell])
                    
        # Filter objects to only include those actually within the region bounds
        result = []
        for obj_id in objects_in_region:
            if obj_id in self.objects:
                obj = self.objects[obj_id]
                # Check if object actually overlaps with the region
                obj_x = getattr(obj, 'x', 0)
                obj_y = getattr(obj, 'y', 0)
                obj_width = getattr(obj, 'width', 0)
                obj_height = getattr(obj, 'height', 0)
                
                # Check for overlap between object bounds and region bounds
                if (obj_x < x + width and obj_x + obj_width > x and
                    obj_y < y + height and obj_y + obj_height > y):
                    result.append(obj)
        
        return result
        
    def clear(self) -> None:
        """Clear all objects from the spatial grid."""
        self.grid.clear()
        self.object_cells.clear()
        self.objects.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the spatial grid for performance monitoring.
        
        Returns:
            Dictionary with grid statistics
        """
        total_objects = len(self.objects)
        occupied_cells = len(self.grid)
        total_cells = self.grid_width * self.grid_height
        
        # Calculate average objects per occupied cell
        if occupied_cells > 0:
            avg_objects_per_cell = sum(len(cell_objects) for cell_objects in self.grid.values()) / occupied_cells
        else:
            avg_objects_per_cell = 0
            
        return {
            'total_objects': total_objects,
            'occupied_cells': occupied_cells,
            'total_cells': total_cells,
            'cell_utilization': occupied_cells / total_cells if total_cells > 0 else 0,
            'avg_objects_per_cell': avg_objects_per_cell,
            'cell_size': self.cell_size
        }


class OptimizedCollisionDetector:
    """
    Optimized collision detector using spatial partitioning.
    """
    
    def __init__(self, world_width: int, world_height: int, cell_size: int = 64):
        """
        Initialize the optimized collision detector.
        
        Args:
            world_width: Width of the game world
            world_height: Height of the game world
            cell_size: Size of spatial grid cells
        """
        self.spatial_grid = SpatialGrid(world_width, world_height, cell_size)
        self.collision_pairs_checked = 0  # Performance metric
        
    def update_objects(self, game_objects: List[Any]) -> None:
        """
        Update the spatial grid with current game objects.
        
        Args:
            game_objects: List of all active game objects
        """
        # Clear and rebuild the grid (could be optimized further by tracking changes)
        self.spatial_grid.clear()
        
        for obj in game_objects:
            if hasattr(obj, 'active') and obj.active:
                self.spatial_grid.add_object(obj)
                
    def check_collisions(self) -> List[Tuple[Any, Any]]:
        """
        Check for collisions using spatial partitioning.
        
        Returns:
            List of collision pairs (obj1, obj2)
        """
        collisions = []
        checked_pairs = set()
        self.collision_pairs_checked = 0
        
        # Check collisions for each object only with nearby objects
        for obj in self.spatial_grid.objects.values():
            if not (hasattr(obj, 'active') and obj.active):
                continue
                
            nearby_objects = self.spatial_grid.get_nearby_objects(obj)
            
            for other_obj in nearby_objects:
                if not (hasattr(other_obj, 'active') and other_obj.active):
                    continue
                    
                # Avoid checking the same pair twice
                pair = tuple(sorted([id(obj), id(other_obj)]))
                if pair in checked_pairs:
                    continue
                    
                checked_pairs.add(pair)
                self.collision_pairs_checked += 1
                
                # Check actual collision
                if hasattr(obj, 'collides_with') and obj.collides_with(other_obj):
                    collisions.append((obj, other_obj))
                    
        return collisions
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the collision detector.
        
        Returns:
            Dictionary with performance metrics
        """
        grid_stats = self.spatial_grid.get_stats()
        return {
            **grid_stats,
            'collision_pairs_checked': self.collision_pairs_checked
        }