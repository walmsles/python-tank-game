# Design Document: Destructible Elements Fix

## Overview

This document outlines the design for fixing the bug where destructible elements (rock piles and petrol barrels) in the game map are not actually destructible when hit by projectiles. The fix will ensure proper collision detection, damage application, and map data synchronization to make destructible elements function as intended.

The current implementation has the necessary classes and methods for destructible elements, but there appears to be a disconnect between the projectile collision system and the map data. This design focuses on identifying and fixing these connection points to ensure destructible elements work correctly.

## Architecture

The fix will maintain the existing component-based architecture while ensuring proper communication between components:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Projectile    │────►│  Collision      │────►│  Destructible   │
│                 │     │  Detection      │     │  Elements       │
└─────────────────┘     └────────┬────────┘     └────────┬────────┘
                                 │                       │
                                 ▼                       ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │  Game Engine    │◄────┤   Map Data      │
                        └─────────────────┘     └─────────────────┘
```

## Components and Interfaces

### 1. Projectile-Destructible Element Collision

The current `Projectile` class has a `_check_collision` method that detects collisions with map elements, but there may be issues with how it identifies and handles destructible elements. We need to ensure:

1. The collision detection correctly identifies when a projectile hits a destructible element
2. The collision handler correctly applies damage to the destructible element
3. The map data is updated when a destructible element is destroyed

```python
# Updated Projectile._check_collision method
def _check_collision(self, new_x, new_y, map_data):
    """
    Check if the projectile would collide with an obstacle at the given position.
    
    Args:
        new_x (float): New X-coordinate to check
        new_y (float): New Y-coordinate to check
        map_data (MapData): The map data for collision detection
        
    Returns:
        tuple: (bool, hit_object) where bool is True if there would be a collision,
              and hit_object is the object that was hit (or None if no collision)
    """
    # Convert pixel coordinates to cell coordinates
    cell_size = map_data.cell_size
    cell_x = int((new_x + self.width / 2) // cell_size)
    cell_y = int((new_y + self.height / 2) // cell_size)
    
    # Check if the cell contains an obstacle
    if map_data.is_obstacle_at(cell_x, cell_y):
        # Check if it's a destructible element
        if map_data.is_destructible_at(cell_x, cell_y):
            # Return the cell coordinates for the destructible element
            return True, (cell_x, cell_y)
        else:
            # Wall collision
            return True, None
    
    # No collision
    return False, None
```

### 2. Destructible Element Damage System

The `DestructibleElement` class and its subclasses (`RockPile` and `PetrolBarrel`) have the necessary methods to take damage and be destroyed, but we need to ensure:

1. The `take_damage` method is properly called when a projectile hits a destructible element
2. The game object is properly deactivated when destroyed
3. The map data is updated when a destructible element is destroyed

```python
# Updated handle_collision method for Projectile
def handle_collision(self, hit_object, game_objects, map_data):
    """
    Handle collision with another game object or map element.
    
    Args:
        hit_object: The object that was hit or cell coordinates for map element
        game_objects: List of all game objects
        map_data: The map data
        
    Returns:
        bool: True if the projectile should be removed, False otherwise
    """
    # If hit_object is a tuple, it's a destructible element in the map
    if isinstance(hit_object, tuple):
        cell_x, cell_y = hit_object
        
        # Find the destructible element at this position
        for obj in game_objects:
            if obj.tag in ["rock_pile", "petrol_barrel"] and obj.active:
                obj_cell_x = int((obj.x + obj.width / 2) // map_data.cell_size)
                obj_cell_y = int((obj.y + obj.height / 2) // map_data.cell_size)
                
                if obj_cell_x == cell_x and obj_cell_y == cell_y:
                    # Damage the destructible element
                    result = obj.take_damage(self.damage)
                    
                    # If it's a petrol barrel and it was destroyed, handle explosion
                    if obj.tag == "petrol_barrel" and isinstance(result, dict) and result.get('destroyed'):
                        # Handle explosion if needed
                        pass
                    
                    # If the element was destroyed, update the map data
                    if (isinstance(result, bool) and result) or \
                       (isinstance(result, dict) and result.get('destroyed')):
                        map_data.set_cell(cell_x, cell_y, map_data.EMPTY)
                    
                    return True
    
    # If hit_object is a game object, damage it
    elif hit_object is not None and hit_object != self.owner:
        if hasattr(hit_object, "take_damage"):
            hit_object.take_damage(self.damage)
            return True
    
    # Default: remove the projectile
    return True
```

### 3. Map Data Synchronization

We need to ensure that when a destructible element is destroyed, the map data is updated to reflect this change:

```python
# Updated method to update map data when a destructible element is destroyed
def update_map_data_for_destroyed_element(self, game_object, map_data):
    """
    Update the map data when a destructible element is destroyed.
    
    Args:
        game_object: The destroyed game object
        map_data: The map data to update
    """
    # Convert object position to cell coordinates
    cell_x = int((game_object.x + game_object.width / 2) // map_data.cell_size)
    cell_y = int((game_object.y + game_object.height / 2) // map_data.cell_size)
    
    # Update the map data to reflect that the cell is now empty
    map_data.set_cell(cell_x, cell_y, map_data.EMPTY)
```

### 4. Collision Detection System

The `CollisionDetector` class needs to properly handle collisions between projectiles and destructible elements:

```python
# Updated _handle_projectile_destructible_collision method
def _handle_projectile_destructible_collision(self, projectile, destructible):
    """
    Handle collision between a projectile and a destructible element.
    
    Args:
        projectile: The projectile object
        destructible: The destructible element object
        
    Returns:
        dict or None: Explosion data if the destructible was a petrol barrel that exploded
    """
    # Projectile is destroyed on impact
    projectile.active = False
    
    # Damage the destructible element
    if hasattr(destructible, 'tag') and destructible.tag == 'petrol_barrel':
        # Handle petrol barrel explosion
        result = destructible.take_damage(projectile.damage if hasattr(projectile, 'damage') else 25)
        
        # Update map data if the barrel was destroyed
        if result['destroyed']:
            # Get the map data from the game engine
            map_data = self.game_engine.map_data if hasattr(self, 'game_engine') else None
            if map_data:
                cell_x = int((destructible.x + destructible.width / 2) // map_data.cell_size)
                cell_y = int((destructible.y + destructible.height / 2) // map_data.cell_size)
                map_data.set_cell(cell_x, cell_y, map_data.EMPTY)
            
            # Return explosion data
            if result['explosion']:
                return result['explosion']
    else:
        # Handle other destructible elements (like rock piles)
        destroyed = destructible.take_damage(projectile.damage if hasattr(projectile, 'damage') else 25)
        
        # Update map data if the element was destroyed
        if destroyed:
            # Get the map data from the game engine
            map_data = self.game_engine.map_data if hasattr(self, 'game_engine') else None
            if map_data:
                cell_x = int((destructible.x + destructible.width / 2) // map_data.cell_size)
                cell_y = int((destructible.y + destructible.height / 2) // map_data.cell_size)
                map_data.set_cell(cell_x, cell_y, map_data.EMPTY)
    
    return None
```

## Data Models

### MapData

The `MapData` class already has the necessary methods to check for destructible elements and update cell types. We need to ensure that these methods are properly called when destructible elements are destroyed:

```python
# Existing methods in MapData
def is_destructible_at(self, x, y):
    """
    Check if there's a destructible element at the given position.
    
    Args:
        x (int): X-coordinate of the cell
        y (int): Y-coordinate of the cell
        
    Returns:
        bool: True if there's a destructible element, False otherwise
    """
    cell_type = self.get_cell(x, y)
    return cell_type == self.ROCK_PILE or cell_type == self.PETROL_BARREL

def set_cell(self, x, y, cell_type):
    """
    Set the type of a cell in the map.
    
    Args:
        x (int): X-coordinate of the cell
        y (int): Y-coordinate of the cell
        cell_type (int): Type of the cell (EMPTY, WALL, ROCK_PILE, or PETROL_BARREL)
    """
    if 0 <= x < self.width and 0 <= y < self.height:
        self.grid[y][x] = cell_type
```

## Error Handling

The fix will include robust error handling to prevent crashes and provide meaningful feedback:

1. **Null Checks**: Ensure that objects and map data are not null before accessing them
2. **Boundary Checks**: Validate cell coordinates before accessing the map grid
3. **Type Checks**: Verify that objects are of the expected type before calling methods on them
4. **Logging**: Add logging for debugging purposes, especially for collision detection and damage application

## Testing Strategy

### Unit Tests

1. **Projectile Collision Tests**:
   - Test collision detection with different types of obstacles
   - Test collision handling for destructible elements
   - Test map data updates when destructible elements are destroyed

2. **Destructible Element Tests**:
   - Test damage application to rock piles and petrol barrels
   - Test destruction of elements when health reaches zero
   - Test visual state changes when elements are damaged

3. **Map Data Tests**:
   - Test map data updates when cells change type
   - Test synchronization between game objects and map data

### Integration Tests

1. **Projectile-Destructible Element Interaction**:
   - Test firing projectiles at rock piles and petrol barrels
   - Verify that elements take damage and are destroyed when health reaches zero
   - Verify that map data is updated when elements are destroyed

2. **Game Engine-Map Data Synchronization**:
   - Test that the game engine correctly updates the map data when destructible elements are destroyed
   - Test that collision detection uses the updated map data after elements are destroyed

### Manual Testing

1. **Gameplay Testing**:
   - Fire projectiles at rock piles and verify they are destroyed
   - Fire projectiles at petrol barrels and verify they explode
   - Verify that tanks can move through spaces where destructible elements have been destroyed

## Implementation Considerations

### Performance

The fix should not significantly impact performance:
- Collision detection is already optimized with spatial partitioning
- Map data updates are minimal and only occur when destructible elements are destroyed

### Compatibility

The fix should maintain compatibility with existing code:
- No changes to public interfaces
- No changes to game object structure
- Only internal implementation changes to fix the bug

### Debugging

Add debugging output to help identify issues:
- Log when projectiles hit destructible elements
- Log when destructible elements take damage
- Log when map data is updated

## Conclusion

This design addresses the bug where destructible elements are not actually destructible by ensuring proper collision detection, damage application, and map data synchronization. The fix maintains the existing architecture while fixing the specific issues that prevent destructible elements from working correctly.