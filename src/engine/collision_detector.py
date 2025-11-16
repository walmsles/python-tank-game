"""
Collision Detector module for the Tank Game.
This module handles collision detection between game objects.
"""


class CollisionDetector:
    """
    Handles collision detection between game objects.
    """
    def __init__(self, game_objects=None, map_data=None):
        """
        Initialize the collision detector.
        
        Args:
            game_objects (list): List of game objects to check collisions for
            map_data (MapData): The map data for collision detection
        """
        self.game_objects = game_objects or []
        self.map_data = map_data
        
    def set_game_objects(self, game_objects):
        """
        Set the list of game objects to check collisions for.
        
        Args:
            game_objects (list): List of game objects
        """
        self.game_objects = game_objects
        
    def check_collisions(self):
        """
        Check for collisions between all game objects.
        
        Returns:
            list: List of collision pairs (obj1, obj2)
        """
        collisions = []
        
        # Check each pair of objects
        for i, obj1 in enumerate(self.game_objects):
            for obj2 in self.game_objects[i+1:]:
                if obj1.collides_with(obj2):
                    collisions.append((obj1, obj2))
                    
        return collisions
        
    def handle_collisions(self):
        """
        Check for collisions and handle them appropriately.
        Handles different collision types based on object tags.
        """
        collisions = self.check_collisions()
        
        # Handle specific collision types
        for obj1, obj2 in collisions:
            self._handle_collision_pair(obj1, obj2)
            
    def _handle_collision_pair(self, obj1, obj2):
        """
        Handle collision between two specific objects.
        
        Args:
            obj1: First game object
            obj2: Second game object
        """
        # Handle projectile-wall collisions
        if self._is_projectile_wall_collision(obj1, obj2):
            projectile, wall = self._get_projectile_wall_pair(obj1, obj2)
            self._handle_projectile_wall_collision(projectile, wall)
            
        # Handle projectile-destructible collisions
        elif self._is_projectile_destructible_collision(obj1, obj2):
            projectile, destructible = self._get_projectile_destructible_pair(obj1, obj2)
            explosion_data = self._handle_projectile_destructible_collision(projectile, destructible)
            if explosion_data:
                self._handle_explosion(explosion_data)
            
        # Handle tank-wall collisions
        elif self._is_tank_wall_collision(obj1, obj2):
            tank, wall = self._get_tank_wall_pair(obj1, obj2)
            self._handle_tank_wall_collision(tank, wall)
            
    def _is_projectile_wall_collision(self, obj1, obj2):
        """
        Check if collision is between a projectile and a wall.
        
        Args:
            obj1: First game object
            obj2: Second game object
            
        Returns:
            bool: True if one is projectile and other is wall
        """
        return ((hasattr(obj1, 'tag') and obj1.tag == 'projectile' and 
                 hasattr(obj2, 'tag') and obj2.tag == 'wall') or
                (hasattr(obj1, 'tag') and obj1.tag == 'wall' and 
                 hasattr(obj2, 'tag') and obj2.tag == 'projectile'))
                 
    def _is_projectile_destructible_collision(self, obj1, obj2):
        """
        Check if collision is between a projectile and a destructible element.
        
        Args:
            obj1: First game object
            obj2: Second game object
            
        Returns:
            bool: True if one is projectile and other is destructible
        """
        return ((hasattr(obj1, 'tag') and obj1.tag == 'projectile' and 
                 hasattr(obj2, 'destructible') and obj2.destructible) or
                (hasattr(obj1, 'destructible') and obj1.destructible and 
                 hasattr(obj2, 'tag') and obj2.tag == 'projectile'))
                 
    def _is_tank_wall_collision(self, obj1, obj2):
        """
        Check if collision is between a tank and a wall.
        
        Args:
            obj1: First game object
            obj2: Second game object
            
        Returns:
            bool: True if one is tank and other is wall
        """
        return ((hasattr(obj1, 'tag') and obj1.tag in ['player_tank', 'enemy_tank'] and 
                 hasattr(obj2, 'tag') and obj2.tag == 'wall') or
                (hasattr(obj1, 'tag') and obj1.tag == 'wall' and 
                 hasattr(obj2, 'tag') and obj2.tag in ['player_tank', 'enemy_tank']))
                 
    def _get_projectile_wall_pair(self, obj1, obj2):
        """
        Get the projectile and wall from a collision pair.
        
        Args:
            obj1: First game object
            obj2: Second game object
            
        Returns:
            tuple: (projectile, wall)
        """
        if hasattr(obj1, 'tag') and obj1.tag == 'projectile':
            return obj1, obj2
        else:
            return obj2, obj1
            
    def _get_projectile_destructible_pair(self, obj1, obj2):
        """
        Get the projectile and destructible element from a collision pair.
        
        Args:
            obj1: First game object
            obj2: Second game object
            
        Returns:
            tuple: (projectile, destructible)
        """
        if hasattr(obj1, 'tag') and obj1.tag == 'projectile':
            return obj1, obj2
        else:
            return obj2, obj1
            
    def _get_tank_wall_pair(self, obj1, obj2):
        """
        Get the tank and wall from a collision pair.
        
        Args:
            obj1: First game object
            obj2: Second game object
            
        Returns:
            tuple: (tank, wall)
        """
        if hasattr(obj1, 'tag') and obj1.tag in ['player_tank', 'enemy_tank']:
            return obj1, obj2
        else:
            return obj2, obj1
            
    def _handle_projectile_wall_collision(self, projectile, wall):
        """
        Handle collision between a projectile and a wall.
        Walls block projectiles, so the projectile should be destroyed.
        
        Args:
            projectile: The projectile object
            wall: The wall object
        """
        # Walls are indestructible, so only the projectile is affected
        projectile.active = False
        
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
            if result['destroyed'] and result['explosion']:
                return result['explosion']
        else:
            # Handle other destructible elements (like rock piles)
            destroyed = destructible.take_damage(projectile.damage if hasattr(projectile, 'damage') else 25)
            
        # If the element was destroyed, update the map data
        if ((hasattr(destructible, 'tag') and destructible.tag == 'petrol_barrel' and 
             isinstance(result, dict) and result.get('destroyed')) or 
            (not hasattr(destructible, 'tag') or destructible.tag != 'petrol_barrel') and destroyed):
            
            if hasattr(destructible, 'update_map_data'):
                # Use the map_data from this collision detector if available
                if self.map_data:
                    destructible.update_map_data(self.map_data)
                else:
                    # Find map_data from the game objects
                    for obj in self.game_objects:
                        if hasattr(obj, 'map_data'):
                            destructible.update_map_data(obj.map_data)
                            break
            
        return None
        
    def _handle_tank_wall_collision(self, tank, wall):
        """
        Handle collision between a tank and a wall.
        Walls block tank movement.
        
        Args:
            tank: The tank object
            wall: The wall object
        """
        # Walls block movement - this would typically be handled
        # by preventing the tank from moving into the wall position
        # The specific implementation depends on how tank movement is handled
        pass
        
    def _handle_explosion(self, explosion_data):
        """
        Handle explosion effects, damaging nearby objects.
        
        Args:
            explosion_data (dict): Explosion data containing center, radius, and damage
        """
        explosion_center_x = explosion_data['center_x']
        explosion_center_y = explosion_data['center_y']
        explosion_radius = explosion_data['radius']
        base_damage = explosion_data['damage']
        
        # Find all objects within explosion radius and damage them
        for obj in self.game_objects:
            if not obj.active:
                continue
                
            # Calculate distance from explosion center to object center
            obj_center_x = obj.x + (obj.width / 2 if hasattr(obj, 'width') else 0)
            obj_center_y = obj.y + (obj.height / 2 if hasattr(obj, 'height') else 0)
            
            dx = obj_center_x - explosion_center_x
            dy = obj_center_y - explosion_center_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            # If object is within explosion radius, damage it
            if distance < explosion_radius:
                # Calculate damage based on distance (closer = more damage)
                damage_ratio = 1.0 - (distance / explosion_radius)
                damage = int(base_damage * damage_ratio)
                damage = max(damage, 1)  # Minimum 1 damage if within radius
                
                # Apply damage to tanks
                if hasattr(obj, 'tag') and obj.tag in ['player_tank', 'enemy_tank']:
                    if hasattr(obj, 'take_damage'):
                        obj.take_damage(damage)
                        print(f"Explosion damaged {obj.tag} at ({obj.x}, {obj.y}) for {damage} damage")
                        
                # Apply damage to other destructible elements
                elif hasattr(obj, 'destructible') and obj.destructible:
                    if hasattr(obj, 'take_damage'):
                        # Handle chain explosions for petrol barrels
                        if hasattr(obj, 'tag') and obj.tag == 'petrol_barrel':
                            result = obj.take_damage(damage)
                            if result['destroyed'] and result['explosion']:
                                # Chain explosion - handle recursively
                                self._handle_explosion(result['explosion'])
                        else:
                            obj.take_damage(damage)
                        print(f"Explosion damaged {obj.tag if hasattr(obj, 'tag') else 'destructible'} at ({obj.x}, {obj.y}) for {damage} damage")


# Import the optimized collision detector
try:
    from .spatial_partitioning import OptimizedCollisionDetector
    
    class EnhancedCollisionDetector(CollisionDetector):
        """
        Enhanced collision detector that uses spatial partitioning for better performance.
        """
        
        def __init__(self, game_objects=None, world_width=800, world_height=600):
            """
            Initialize the enhanced collision detector.
            
            Args:
                game_objects: List of game objects
                world_width: Width of the game world
                world_height: Height of the game world
            """
            super().__init__(game_objects)
            self.optimized_detector = OptimizedCollisionDetector(world_width, world_height)
            self.use_spatial_partitioning = True
            
        def check_collisions(self):
            """
            Check for collisions using spatial partitioning when possible.
            
            Returns:
                list: List of collision pairs (obj1, obj2)
            """
            if self.use_spatial_partitioning and len(self.game_objects) > 10:
                # Use optimized collision detection for larger numbers of objects
                self.optimized_detector.update_objects(self.game_objects)
                return self.optimized_detector.check_collisions()
            else:
                # Fall back to original method for small numbers of objects
                return super().check_collisions()
                
        def get_performance_stats(self):
            """
            Get performance statistics from the collision detector.
            
            Returns:
                dict: Performance statistics
            """
            if hasattr(self.optimized_detector, 'get_performance_stats'):
                return self.optimized_detector.get_performance_stats()
            else:
                return {
                    'collision_pairs_checked': len(self.game_objects) * (len(self.game_objects) - 1) // 2,
                    'spatial_partitioning_enabled': False
                }
                
except ImportError:
    # Fallback if spatial partitioning is not available
    class EnhancedCollisionDetector(CollisionDetector):
        """Fallback enhanced collision detector without spatial partitioning."""
        
        def get_performance_stats(self):
            return {
                'collision_pairs_checked': len(self.game_objects) * (len(self.game_objects) - 1) // 2,
                'spatial_partitioning_enabled': False
            }