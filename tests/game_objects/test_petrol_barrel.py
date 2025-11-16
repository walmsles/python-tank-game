"""
Unit tests for the PetrolBarrel class.
"""
import unittest
import math
from src.game_objects.petrol_barrel import PetrolBarrel


class TestPetrolBarrel(unittest.TestCase):
    """Test cases for the PetrolBarrel class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.barrel = PetrolBarrel(100, 100, 50)
        
    def test_initialization(self):
        """Test that PetrolBarrel initializes correctly."""
        self.assertEqual(self.barrel.x, 100)
        self.assertEqual(self.barrel.y, 100)
        self.assertEqual(self.barrel.health, 50)
        self.assertEqual(self.barrel.max_health, 50)
        self.assertTrue(self.barrel.destructible)
        self.assertTrue(self.barrel.active)
        self.assertEqual(self.barrel.tag, "petrol_barrel")
        self.assertEqual(self.barrel.explosion_radius, 64)
        self.assertEqual(self.barrel.explosion_damage, 50)
        
    def test_default_health(self):
        """Test that PetrolBarrel has correct default health."""
        default_barrel = PetrolBarrel(0, 0)
        self.assertEqual(default_barrel.health, 50)
        self.assertEqual(default_barrel.max_health, 50)
        
    def test_blocks_movement_when_active(self):
        """Test that active petrol barrel blocks movement."""
        self.assertTrue(self.barrel.blocks_movement())
        
    def test_blocks_projectiles_when_active(self):
        """Test that active petrol barrel blocks projectiles."""
        self.assertTrue(self.barrel.blocks_projectiles())
        
    def test_does_not_block_when_destroyed(self):
        """Test that destroyed petrol barrel doesn't block movement or projectiles."""
        # Destroy the barrel
        self.barrel.take_damage(50)
        self.assertFalse(self.barrel.blocks_movement())
        self.assertFalse(self.barrel.blocks_projectiles())
        
    def test_take_damage_normal(self):
        """Test taking damage without destruction."""
        result = self.barrel.take_damage(20)
        self.assertEqual(self.barrel.health, 30)
        self.assertTrue(self.barrel.active)
        self.assertFalse(result['destroyed'])
        self.assertIsNone(result['explosion'])
        
    def test_take_damage_destruction(self):
        """Test taking damage that destroys the barrel."""
        result = self.barrel.take_damage(50)
        self.assertEqual(self.barrel.health, 0)
        self.assertFalse(self.barrel.active)
        self.assertTrue(result['destroyed'])
        self.assertIsNotNone(result['explosion'])
        
    def test_take_damage_overkill(self):
        """Test taking more damage than health remaining."""
        result = self.barrel.take_damage(100)
        self.assertEqual(self.barrel.health, -50)
        self.assertFalse(self.barrel.active)
        self.assertTrue(result['destroyed'])
        self.assertIsNotNone(result['explosion'])
        
    def test_explosion_data_structure(self):
        """Test that explosion data has correct structure."""
        result = self.barrel.take_damage(50)
        explosion = result['explosion']
        
        self.assertIn('center_x', explosion)
        self.assertIn('center_y', explosion)
        self.assertIn('radius', explosion)
        self.assertIn('damage', explosion)
        
        # Check explosion center calculation (assuming barrel has width/height of 0 initially)
        expected_center_x = self.barrel.x + self.barrel.width / 2
        expected_center_y = self.barrel.y + self.barrel.height / 2
        self.assertEqual(explosion['center_x'], expected_center_x)
        self.assertEqual(explosion['center_y'], expected_center_y)
        self.assertEqual(explosion['radius'], 64)
        self.assertEqual(explosion['damage'], 50)
        
    def test_calculate_explosion_damage_at_center(self):
        """Test explosion damage calculation at explosion center."""
        # Set barrel dimensions for testing
        self.barrel.width = 32
        self.barrel.height = 32
        
        # Target at exact center should receive full damage
        damage = self.barrel.calculate_explosion_damage(
            self.barrel.x + 16, self.barrel.y + 16, 0, 0
        )
        self.assertEqual(damage, 50)
        
    def test_calculate_explosion_damage_at_edge(self):
        """Test explosion damage calculation at explosion radius edge."""
        # Set barrel dimensions for testing
        self.barrel.width = 32
        self.barrel.height = 32
        
        # Target at edge of explosion radius should receive minimal damage
        explosion_center_x = self.barrel.x + 16
        explosion_center_y = self.barrel.y + 16
        
        # Place target at exactly the explosion radius distance
        target_x = explosion_center_x + self.barrel.explosion_radius - 1
        target_y = explosion_center_y
        
        damage = self.barrel.calculate_explosion_damage(target_x, target_y, 0, 0)
        self.assertGreater(damage, 0)
        self.assertLess(damage, 50)
        
    def test_calculate_explosion_damage_outside_radius(self):
        """Test explosion damage calculation outside explosion radius."""
        # Set barrel dimensions for testing
        self.barrel.width = 32
        self.barrel.height = 32
        
        # Target outside explosion radius should receive no damage
        explosion_center_x = self.barrel.x + 16
        explosion_center_y = self.barrel.y + 16
        
        # Place target outside explosion radius
        target_x = explosion_center_x + self.barrel.explosion_radius + 10
        target_y = explosion_center_y
        
        damage = self.barrel.calculate_explosion_damage(target_x, target_y, 0, 0)
        self.assertEqual(damage, 0)
        
    def test_calculate_explosion_damage_with_target_dimensions(self):
        """Test explosion damage calculation considering target dimensions."""
        # Set barrel dimensions for testing
        self.barrel.width = 32
        self.barrel.height = 32
        
        # Target with dimensions - center should be calculated correctly
        target_width = 20
        target_height = 20
        
        damage = self.barrel.calculate_explosion_damage(
            self.barrel.x, self.barrel.y, target_width, target_height
        )
        self.assertGreater(damage, 0)
        
    def test_is_in_explosion_radius_true(self):
        """Test is_in_explosion_radius returns True for targets within radius."""
        # Set barrel dimensions for testing
        self.barrel.width = 32
        self.barrel.height = 32
        
        # Target close to barrel should be in explosion radius
        self.assertTrue(self.barrel.is_in_explosion_radius(
            self.barrel.x + 10, self.barrel.y + 10, 0, 0
        ))
        
    def test_is_in_explosion_radius_false(self):
        """Test is_in_explosion_radius returns False for targets outside radius."""
        # Set barrel dimensions for testing
        self.barrel.width = 32
        self.barrel.height = 32
        
        # Target far from barrel should not be in explosion radius
        self.assertFalse(self.barrel.is_in_explosion_radius(
            self.barrel.x + 200, self.barrel.y + 200, 0, 0
        ))
        
    def test_explosion_damage_decreases_with_distance(self):
        """Test that explosion damage decreases with distance from center."""
        # Set barrel dimensions for testing
        self.barrel.width = 32
        self.barrel.height = 32
        
        explosion_center_x = self.barrel.x + 16
        explosion_center_y = self.barrel.y + 16
        
        # Calculate damage at different distances
        damage_close = self.barrel.calculate_explosion_damage(
            explosion_center_x + 10, explosion_center_y, 0, 0
        )
        damage_far = self.barrel.calculate_explosion_damage(
            explosion_center_x + 30, explosion_center_y, 0, 0
        )
        
        # Closer target should receive more damage
        self.assertGreater(damage_close, damage_far)
        
    def test_minimum_damage_within_radius(self):
        """Test that minimum damage of 1 is applied within explosion radius."""
        # Set barrel dimensions for testing
        self.barrel.width = 32
        self.barrel.height = 32
        
        explosion_center_x = self.barrel.x + 16
        explosion_center_y = self.barrel.y + 16
        
        # Target at edge of explosion radius should receive at least 1 damage
        target_x = explosion_center_x + self.barrel.explosion_radius - 1
        target_y = explosion_center_y
        
        damage = self.barrel.calculate_explosion_damage(target_x, target_y, 0, 0)
        self.assertGreaterEqual(damage, 1)
        
    def test_render_when_active(self):
        """Test that render is called when barrel is active."""
        # This test would require a mock screen object
        # For now, we just test that render doesn't crash
        try:
            self.barrel.render(None)
        except AttributeError:
            # Expected since we're passing None as screen
            pass
            
    def test_render_when_destroyed(self):
        """Test that render is not called when barrel is destroyed."""
        self.barrel.take_damage(50)  # Destroy the barrel
        
        # This should not crash and should return early
        try:
            self.barrel.render(None)
        except AttributeError:
            self.fail("render() should return early when barrel is not active")


if __name__ == '__main__':
    unittest.main()