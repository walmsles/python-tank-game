"""
Unit tests for the CollisionDetector class with PetrolBarrel explosions.
"""
import unittest
from unittest.mock import Mock
from src.engine.collision_detector import CollisionDetector
from src.game_objects.petrol_barrel import PetrolBarrel


class TestCollisionDetectorPetrolBarrel(unittest.TestCase):
    """Test cases for CollisionDetector with PetrolBarrel explosions."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.collision_detector = CollisionDetector()
        
    def test_is_projectile_destructible_collision_true(self):
        """Test that projectile-destructible collision is detected correctly."""
        # Create mock objects
        projectile = Mock()
        projectile.tag = 'projectile'
        
        destructible = Mock()
        destructible.destructible = True
        
        # Test both orders
        self.assertTrue(self.collision_detector._is_projectile_destructible_collision(projectile, destructible))
        self.assertTrue(self.collision_detector._is_projectile_destructible_collision(destructible, projectile))
        
    def test_is_projectile_destructible_collision_false(self):
        """Test that non-projectile-destructible collision is not detected."""
        # Create mock objects
        tank = Mock()
        tank.tag = 'player_tank'
        
        wall = Mock()
        wall.tag = 'wall'
        
        self.assertFalse(self.collision_detector._is_projectile_destructible_collision(tank, wall))
        
    def test_get_projectile_destructible_pair(self):
        """Test that projectile-destructible pair is returned in correct order."""
        # Create mock objects
        projectile = Mock()
        projectile.tag = 'projectile'
        
        destructible = Mock()
        destructible.destructible = True
        
        # Test both orders
        proj, dest = self.collision_detector._get_projectile_destructible_pair(projectile, destructible)
        self.assertEqual(proj, projectile)
        self.assertEqual(dest, destructible)
        
        proj, dest = self.collision_detector._get_projectile_destructible_pair(destructible, projectile)
        self.assertEqual(proj, projectile)
        self.assertEqual(dest, destructible)
        
    def test_handle_projectile_destructible_collision_rock_pile(self):
        """Test handling collision between projectile and rock pile (no explosion)."""
        # Create mock objects
        projectile = Mock()
        projectile.tag = 'projectile'
        projectile.damage = 25
        projectile.active = True
        
        rock_pile = Mock()
        rock_pile.tag = 'rock_pile'
        rock_pile.take_damage = Mock()
        
        # Handle collision
        result = self.collision_detector._handle_projectile_destructible_collision(projectile, rock_pile)
        
        # Verify projectile is destroyed
        self.assertFalse(projectile.active)
        
        # Verify rock pile takes damage
        rock_pile.take_damage.assert_called_once_with(25)
        
        # Verify no explosion
        self.assertIsNone(result)
        
    def test_handle_projectile_destructible_collision_petrol_barrel_no_explosion(self):
        """Test handling collision between projectile and petrol barrel without explosion."""
        # Create mock objects
        projectile = Mock()
        projectile.tag = 'projectile'
        projectile.damage = 25
        projectile.active = True
        
        barrel = Mock()
        barrel.tag = 'petrol_barrel'
        barrel.take_damage = Mock(return_value={'destroyed': False, 'explosion': None})
        
        # Handle collision
        result = self.collision_detector._handle_projectile_destructible_collision(projectile, barrel)
        
        # Verify projectile is destroyed
        self.assertFalse(projectile.active)
        
        # Verify barrel takes damage
        barrel.take_damage.assert_called_once_with(25)
        
        # Verify no explosion
        self.assertIsNone(result)
        
    def test_handle_projectile_destructible_collision_petrol_barrel_with_explosion(self):
        """Test handling collision between projectile and petrol barrel with explosion."""
        # Create mock objects
        projectile = Mock()
        projectile.tag = 'projectile'
        projectile.damage = 50
        projectile.active = True
        
        explosion_data = {
            'center_x': 100,
            'center_y': 100,
            'radius': 64,
            'damage': 50
        }
        
        barrel = Mock()
        barrel.tag = 'petrol_barrel'
        barrel.take_damage = Mock(return_value={'destroyed': True, 'explosion': explosion_data})
        
        # Handle collision
        result = self.collision_detector._handle_projectile_destructible_collision(projectile, barrel)
        
        # Verify projectile is destroyed
        self.assertFalse(projectile.active)
        
        # Verify barrel takes damage
        barrel.take_damage.assert_called_once_with(50)
        
        # Verify explosion data is returned
        self.assertEqual(result, explosion_data)
        
    def test_handle_explosion_damages_nearby_tank(self):
        """Test that explosion damages nearby tanks."""
        # Create explosion data
        explosion_data = {
            'center_x': 100,
            'center_y': 100,
            'radius': 64,
            'damage': 50
        }
        
        # Create mock tank near explosion
        tank = Mock()
        tank.tag = 'player_tank'
        tank.active = True
        tank.x = 90
        tank.y = 90
        tank.width = 20
        tank.height = 20
        tank.take_damage = Mock()
        
        # Set up collision detector with the tank
        self.collision_detector.game_objects = [tank]
        
        # Handle explosion
        self.collision_detector._handle_explosion(explosion_data)
        
        # Verify tank takes damage
        tank.take_damage.assert_called_once()
        
    def test_handle_explosion_does_not_damage_distant_tank(self):
        """Test that explosion does not damage tanks outside radius."""
        # Create explosion data
        explosion_data = {
            'center_x': 100,
            'center_y': 100,
            'radius': 64,
            'damage': 50
        }
        
        # Create mock tank far from explosion
        tank = Mock()
        tank.tag = 'player_tank'
        tank.active = True
        tank.x = 200
        tank.y = 200
        tank.width = 20
        tank.height = 20
        tank.take_damage = Mock()
        
        # Set up collision detector with the tank
        self.collision_detector.game_objects = [tank]
        
        # Handle explosion
        self.collision_detector._handle_explosion(explosion_data)
        
        # Verify tank does not take damage
        tank.take_damage.assert_not_called()
        
    def test_handle_explosion_chain_reaction(self):
        """Test that explosion can trigger chain reactions with other petrol barrels."""
        # Create explosion data
        explosion_data = {
            'center_x': 100,
            'center_y': 100,
            'radius': 64,
            'damage': 50
        }
        
        # Create mock petrol barrel near explosion
        chain_explosion_data = {
            'center_x': 120,
            'center_y': 120,
            'radius': 64,
            'damage': 50
        }
        
        barrel = Mock()
        barrel.tag = 'petrol_barrel'
        barrel.active = True
        barrel.x = 110
        barrel.y = 110
        barrel.width = 20
        barrel.height = 20
        barrel.destructible = True
        barrel.take_damage = Mock(return_value={'destroyed': True, 'explosion': chain_explosion_data})
        
        # Set up collision detector with the barrel
        self.collision_detector.game_objects = [barrel]
        
        # Mock the _handle_explosion method to track recursive calls
        original_handle_explosion = self.collision_detector._handle_explosion
        explosion_calls = []
        
        def mock_handle_explosion(data):
            explosion_calls.append(data)
            if len(explosion_calls) == 1:  # Only handle the first explosion to avoid infinite recursion in test
                original_handle_explosion(data)
        
        self.collision_detector._handle_explosion = mock_handle_explosion
        
        # Handle explosion
        self.collision_detector._handle_explosion(explosion_data)
        
        # Verify barrel takes damage
        barrel.take_damage.assert_called_once()
        
        # Verify chain explosion was triggered
        self.assertEqual(len(explosion_calls), 2)  # Original + chain explosion
        self.assertEqual(explosion_calls[0], explosion_data)
        self.assertEqual(explosion_calls[1], chain_explosion_data)
        
    def test_handle_explosion_damages_other_destructibles(self):
        """Test that explosion damages other destructible elements."""
        # Create explosion data
        explosion_data = {
            'center_x': 100,
            'center_y': 100,
            'radius': 64,
            'damage': 50
        }
        
        # Create mock destructible element near explosion
        rock_pile = Mock()
        rock_pile.tag = 'rock_pile'
        rock_pile.active = True
        rock_pile.x = 90
        rock_pile.y = 90
        rock_pile.width = 20
        rock_pile.height = 20
        rock_pile.destructible = True
        rock_pile.take_damage = Mock()
        
        # Set up collision detector with the rock pile
        self.collision_detector.game_objects = [rock_pile]
        
        # Handle explosion
        self.collision_detector._handle_explosion(explosion_data)
        
        # Verify rock pile takes damage
        rock_pile.take_damage.assert_called_once()
        
    def test_handle_explosion_ignores_inactive_objects(self):
        """Test that explosion ignores inactive objects."""
        # Create explosion data
        explosion_data = {
            'center_x': 100,
            'center_y': 100,
            'radius': 64,
            'damage': 50
        }
        
        # Create mock inactive tank
        tank = Mock()
        tank.tag = 'player_tank'
        tank.active = False
        tank.x = 90
        tank.y = 90
        tank.width = 20
        tank.height = 20
        tank.take_damage = Mock()
        
        # Set up collision detector with the tank
        self.collision_detector.game_objects = [tank]
        
        # Handle explosion
        self.collision_detector._handle_explosion(explosion_data)
        
        # Verify tank does not take damage
        tank.take_damage.assert_not_called()


if __name__ == '__main__':
    unittest.main()