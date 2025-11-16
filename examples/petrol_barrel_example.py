"""
Example demonstrating PetrolBarrel explosion functionality.
This example shows how petrol barrels explode and damage nearby objects.
"""
from src.game_objects.petrol_barrel import PetrolBarrel
from src.game_objects.wall import Wall
from src.game_objects.rock_pile import RockPile
from src.engine.collision_detector import CollisionDetector
from unittest.mock import Mock


def create_mock_projectile(damage=50):
    """Create a mock projectile for testing."""
    projectile = Mock()
    projectile.tag = 'projectile'
    projectile.damage = damage
    projectile.active = True
    projectile.x = 0
    projectile.y = 0
    projectile.width = 5
    projectile.height = 5
    return projectile


def create_mock_tank(x, y, tag='player_tank'):
    """Create a mock tank for testing."""
    tank = Mock()
    tank.tag = tag
    tank.active = True
    tank.x = x
    tank.y = y
    tank.width = 32
    tank.height = 32
    tank.health = 100
    tank.take_damage = Mock()
    return tank


def demonstrate_petrol_barrel_explosion():
    """Demonstrate petrol barrel explosion mechanics."""
    print("=== PetrolBarrel Explosion Demonstration ===\n")
    
    # Create a petrol barrel
    barrel = PetrolBarrel(100, 100, 50)
    print(f"Created PetrolBarrel at ({barrel.x}, {barrel.y})")
    print(f"Health: {barrel.health}, Explosion radius: {barrel.explosion_radius}")
    print(f"Blocks movement: {barrel.blocks_movement()}")
    print(f"Blocks projectiles: {barrel.blocks_projectiles()}\n")
    
    # Test explosion damage calculation
    print("--- Explosion Damage Calculation ---")
    barrel.width = 32  # Set dimensions for testing
    barrel.height = 32
    
    # Test damage at different distances
    center_damage = barrel.calculate_explosion_damage(116, 116, 0, 0)  # At center
    edge_damage = barrel.calculate_explosion_damage(180, 116, 0, 0)    # At edge
    outside_damage = barrel.calculate_explosion_damage(200, 200, 0, 0) # Outside radius
    
    print(f"Damage at explosion center: {center_damage}")
    print(f"Damage at explosion edge: {edge_damage}")
    print(f"Damage outside explosion radius: {outside_damage}\n")
    
    # Test barrel destruction and explosion
    print("--- Barrel Destruction and Explosion ---")
    projectile = create_mock_projectile(50)
    
    print(f"Projectile hits barrel with {projectile.damage} damage")
    result = barrel.take_damage(projectile.damage)
    
    print(f"Barrel destroyed: {result['destroyed']}")
    if result['explosion']:
        explosion = result['explosion']
        print(f"Explosion created at ({explosion['center_x']}, {explosion['center_y']})")
        print(f"Explosion radius: {explosion['radius']}, damage: {explosion['damage']}\n")
    
    # Demonstrate collision detection with explosion
    print("--- Collision Detection with Explosion ---")
    
    # Create new barrel and objects for collision test
    barrel2 = PetrolBarrel(200, 200, 50)
    barrel2.width = 32
    barrel2.height = 32
    
    # Create nearby objects
    nearby_tank = create_mock_tank(210, 210, 'player_tank')
    distant_tank = create_mock_tank(300, 300, 'enemy_tank')
    nearby_rock = RockPile(220, 220, 75)
    wall = Wall(250, 250)
    
    # Create collision detector
    game_objects = [barrel2, nearby_tank, distant_tank, nearby_rock, wall]
    collision_detector = CollisionDetector(game_objects)
    
    # Simulate projectile hitting barrel
    projectile2 = create_mock_projectile(50)
    
    print("Simulating projectile collision with petrol barrel...")
    explosion_data = collision_detector._handle_projectile_destructible_collision(projectile2, barrel2)
    
    if explosion_data:
        print("Explosion occurred! Handling explosion effects...")
        collision_detector._handle_explosion(explosion_data)
        
        # Check damage to nearby tank
        if nearby_tank.take_damage.called:
            print(f"Nearby tank took damage: {nearby_tank.take_damage.call_args}")
        else:
            print("Nearby tank was not damaged")
            
        # Check damage to distant tank
        if distant_tank.take_damage.called:
            print(f"Distant tank took damage: {distant_tank.take_damage.call_args}")
        else:
            print("Distant tank was not damaged (too far away)")
    
    print("\n--- Chain Explosion Test ---")
    
    # Create two barrels close to each other
    barrel3 = PetrolBarrel(300, 300, 50)
    barrel3.width = 32
    barrel3.height = 32
    
    barrel4 = PetrolBarrel(340, 300, 50)  # Within explosion radius of barrel3
    barrel4.width = 32
    barrel4.height = 32
    
    chain_objects = [barrel3, barrel4]
    chain_detector = CollisionDetector(chain_objects)
    
    print("Testing chain explosion with two nearby barrels...")
    
    # Destroy first barrel
    result3 = barrel3.take_damage(50)
    if result3['explosion']:
        print("First barrel exploded!")
        
        # Check if second barrel is in explosion radius
        explosion = result3['explosion']
        damage_to_barrel4 = barrel3.calculate_explosion_damage(
            barrel4.x, barrel4.y, barrel4.width, barrel4.height
        )
        
        print(f"Second barrel would take {damage_to_barrel4} damage from explosion")
        
        if damage_to_barrel4 >= barrel4.health:
            print("Second barrel would also explode, creating a chain reaction!")
        else:
            print("Second barrel would be damaged but not destroyed")
    
    print("\n=== Demonstration Complete ===")


if __name__ == "__main__":
    demonstrate_petrol_barrel_explosion()