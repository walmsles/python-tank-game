"""
Integration tests for projectile-destructible element interaction.
"""
import unittest
from unittest.mock import Mock, patch
import math
from src.game_objects.projectile import Projectile
from src.game_objects.rock_pile import RockPile
from src.game_objects.petrol_barrel import PetrolBarrel
from src.level_manager.map_data import MapData
from src.engine.collision_detector import CollisionDetector


class TestProjectileDestructibleInteraction(unittest.TestCase):
    """Integration tests for projectile-destructible element interaction."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a map data object
        self.map_data = MapData(20, 20)
        self.map_data.cell_size = 32
        
        # Create a rock pile
        self.rock_pile = RockPile(160, 160, health=75)
        self.rock_pile.width = 32
        self.rock_pile.height = 32
        
        # Create a petrol barrel
        self.petrol_barrel = PetrolBarrel(320, 320, health=50)
        self.petrol_barrel.width = 32
        self.petrol_barrel.height = 32
        
        # Set up the map data
        self.map_data.set_cell(5, 5, MapData.ROCK_PILE)  # Rock pile at (160, 160)
        self.map_data.set_cell(10, 10, MapData.PETROL_BARREL)  # Petrol barrel at (320, 320)
        
        # Create game objects list
        self.game_objects = [self.rock_pile, self.petrol_barrel]
        
        # Create a collision detector
        self.collision_detector = CollisionDetector(self.game_objects)
    
    def test_projectile_hits_rock_pile(self):
        """Test that projectile correctly hits and damages rock pile."""
        # Create a projectile aimed at the rock pile
        projectile = Projectile(128, 160, 90, speed=10, damage=30)
        projectile.width = 8
        projectile.height = 8
        
        # Add projectile to game objects
        self.game_objects.append(projectile)
        
        # Update the projectile for several frames
        for _ in range(10):
            # Check if projectile is still active
            if not projectile.active:
                break
            
            # Update projectile
            projectile.update(0.016, self.map_data)  # 60 FPS = ~16ms per frame
        
        # Assert that the projectile is no longer active (hit something)
        self.assertFalse(projectile.active)
        # Assert that the rock pile took damage
        self.assertEqual(self.rock_pile.health, 45)  # 75 - 30 = 45
    
    def test_projectile_destroys_rock_pile(self):
        """Test that projectile correctly destroys rock pile and updates map data."""
        # Create a projectile aimed at the rock pile with high damage
        projectile = Projectile(128, 160, 90, speed=10, damage=100)
        projectile.width = 8
        projectile.height = 8
        
        # Add projectile to game objects
        self.game_objects.append(projectile)
        
        # Update the projectile for several frames
        for _ in range(10):
            # Check if projectile is still active
            if not projectile.active:
                break
            
            # Update projectile
            projectile.update(0.016, self.map_data)  # 60 FPS = ~16ms per frame
        
        # Assert that the projectile is no longer active (hit something)
        self.assertFalse(projectile.active)
        # Assert that the rock pile was destroyed
        self.assertFalse(self.rock_pile.active)
        # Assert that the map data was updated
        self.assertEqual(self.map_data.get_cell(5, 5), MapData.EMPTY)
    
    def test_projectile_hits_petrol_barrel(self):
        """Test that projectile correctly hits and damages petrol barrel."""
        # Create a projectile aimed at the petrol barrel
        projectile = Projectile(288, 320, 90, speed=10, damage=30)
        projectile.width = 8
        projectile.height = 8
        
        # Add projectile to game objects
        self.game_objects.append(projectile)
        
        # Update the projectile for several frames
        for _ in range(10):
            # Check if projectile is still active
            if not projectile.active:
                break
            
            # Update projectile
            projectile.update(0.016, self.map_data)  # 60 FPS = ~16ms per frame
        
        # Assert that the projectile is no longer active (hit something)
        self.assertFalse(projectile.active)
        # Assert that the petrol barrel took damage
        self.assertEqual(self.petrol_barrel.health, 20)  # 50 - 30 = 20
    
    def test_projectile_destroys_petrol_barrel(self):
        """Test that projectile correctly destroys petrol barrel and updates map data."""
        # Create a projectile aimed at the petrol barrel with high damage
        projectile = Projectile(288, 320, 90, speed=10, damage=100)
        projectile.width = 8
        projectile.height = 8
        
        # Add projectile to game objects
        self.game_objects.append(projectile)
        
        # Update the projectile for several frames
        for _ in range(10):
            # Check if projectile is still active
            if not projectile.active:
                break
            
            # Update projectile
            projectile.update(0.016, self.map_data)  # 60 FPS = ~16ms per frame
        
        # Assert that the projectile is no longer active (hit something)
        self.assertFalse(projectile.active)
        # Assert that the petrol barrel was destroyed
        self.assertFalse(self.petrol_barrel.active)
        # Assert that the map data was updated
        self.assertEqual(self.map_data.get_cell(10, 10), MapData.EMPTY)
    
    def test_projectile_passes_through_destroyed_element(self):
        """Test that projectile correctly passes through space where destructible element was destroyed."""
        # Destroy the rock pile and update map data
        self.rock_pile.active = False
        self.rock_pile.update_map_data(self.map_data)
        
        # Create a projectile aimed at where the rock pile was
        projectile = Projectile(128, 160, 90, speed=10, damage=30)
        projectile.width = 8
        projectile.height = 8
        
        # Add projectile to game objects
        self.game_objects.append(projectile)
        
        # Update the projectile for several frames
        for _ in range(10):
            # Update projectile
            projectile.update(0.016, self.map_data)  # 60 FPS = ~16ms per frame
        
        # Assert that the projectile is still active (didn't hit anything)
        self.assertTrue(projectile.active)
        # Assert that the projectile moved past where the rock pile was
        self.assertGreater(projectile.x, 160)


if __name__ == '__main__':
    unittest.main()