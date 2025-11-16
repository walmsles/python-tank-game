"""
Main entry point for the Tank Game.
"""
import pygame
import sys
import os
import math
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.engine.game_engine import GameEngine
from src.game_objects.player_tank import PlayerTank
from src.level_manager.level_manager import LevelManager
from src.renderers.enhanced_map_renderer import EnhancedMapRenderer
from src.renderers.enhanced_tank_renderer import EnhancedTankRenderer
from src.renderers.enhanced_projectile_renderer import EnhancedProjectileRenderer
from src.renderers.visual_effects_manager import VisualEffectsManager
from src.engine.input_handler import InputHandler


def main():
    """Main function to start the tank game."""
    try:
        # Create and initialize the game engine
        game_engine = GameEngine(width=800, height=600, title="Tank Game", target_fps=60)
        game_engine.initialize()
        
        # Create enhanced renderers
        map_renderer = EnhancedMapRenderer(game_engine.renderer)
        tank_renderer = EnhancedTankRenderer(game_engine.renderer)
        projectile_renderer = EnhancedProjectileRenderer(game_engine.renderer)
        
        # Create visual effects manager
        visual_effects = VisualEffectsManager()
        
        # Create an input handler
        input_handler = InputHandler()
        
        # Create a player tank
        player_tank = PlayerTank(400, 300, health=100, speed=5)
        game_engine.add_game_object(player_tank)
        
        # Set sound manager for the player tank
        if game_engine.sound_manager:
            player_tank.set_sound_manager(game_engine.sound_manager)
        
        # Create a level manager
        level_manager = LevelManager(game_engine, max_level=10)
        game_engine.level_manager = level_manager
        
        # Initialize the level manager with the player tank
        level_manager.initialize(player_tank)
        
        # List to store active projectiles
        projectiles = []
        
        # Custom update function to handle input and game logic
        def custom_update():
            # Process input events (for tank movement)
            input_handler.process_events()
            
            # Skip game logic if game is over or victory screen is showing
            if (game_engine.game_state_manager.show_game_over_screen or 
                game_engine.game_state_manager.show_victory_screen):
                return
            
            # Update the player tank and check for projectile firing
            if player_tank.active:
                new_projectile = player_tank.update(game_engine.delta_time, level_manager.map_data, input_handler)
                if new_projectile:
                    new_projectile.age = 0.0  # Initialize age for visual effects
                    projectiles.append(new_projectile)
                    game_engine.add_game_object(new_projectile)
                    
                    # Add muzzle flash effect
                    import math
                    muzzle_x = player_tank.x + player_tank.width // 2 + math.sin(math.radians(player_tank.direction)) * (player_tank.height // 2 + 5)
                    muzzle_y = player_tank.y + player_tank.height // 2 - math.cos(math.radians(player_tank.direction)) * (player_tank.height // 2 + 5)
                    visual_effects.add_muzzle_flash(muzzle_x, muzzle_y, player_tank.direction)
            
            # Update enemy tanks
            game_objects = [player_tank] + level_manager.enemy_tanks + projectiles
            for enemy_tank in level_manager.enemy_tanks[:]:
                if enemy_tank.active:
                    new_projectile = enemy_tank.update(game_engine.delta_time, level_manager.map_data, game_objects)
                    if new_projectile:
                        new_projectile.age = 0.0  # Initialize age for visual effects
                        projectiles.append(new_projectile)
                        game_engine.add_game_object(new_projectile)
                        
                        # Add muzzle flash effect for enemy tanks
                        import math
                        muzzle_x = enemy_tank.x + enemy_tank.width // 2 + math.sin(math.radians(enemy_tank.direction)) * (enemy_tank.height // 2 + 5)
                        muzzle_y = enemy_tank.y + enemy_tank.height // 2 - math.cos(math.radians(enemy_tank.direction)) * (enemy_tank.height // 2 + 5)
                        visual_effects.add_muzzle_flash(muzzle_x, muzzle_y, enemy_tank.direction)
            
            # Update projectiles and handle collisions
            for projectile in projectiles[:]:  # Create a copy of the list to safely remove items
                # Update projectile age for visual effects
                if hasattr(projectile, 'age'):
                    projectile.age += game_engine.delta_time
                
                # Store the old position for collision detection
                old_x, old_y = projectile.x, projectile.y
                
                # Store the projectile's current position and calculate the next position
                current_x, current_y = projectile.x, projectile.y
                # Use the imported math module
                import math
                rad = math.radians(projectile.direction)
                dx = math.sin(rad) * projectile.speed * game_engine.delta_time * 60
                dy = -math.cos(rad) * projectile.speed * game_engine.delta_time * 60
                next_x, next_y = current_x + dx, current_y + dy
                
                # Check for collisions before updating
                collision, hit_object = projectile._check_collision(next_x, next_y, level_manager.map_data)
                
                if collision:
                    print(f"Collision detected! Hit object: {hit_object}")
                    
                    # If there was a collision with a destructible element (hit_object is a tuple of cell coordinates)
                    if hit_object is not None and isinstance(hit_object, tuple):
                        cell_x, cell_y = hit_object
                        cell_type = level_manager.map_data.get_cell(cell_x, cell_y)
                        print(f"Collision with cell type {cell_type} at ({cell_x}, {cell_y})")
                        
                        # Find the destructible element at this position
                        found_destructible = False
                        for obj in game_engine.game_objects:
                            if hasattr(obj, 'tag') and obj.tag in ["destructible", "rock_pile", "petrol_barrel"] and obj.active:
                                obj_cell_x = int((obj.x + obj.width / 2) // level_manager.map_data.cell_size)
                                obj_cell_y = int((obj.y + obj.height / 2) // level_manager.map_data.cell_size)
                                
                                if obj_cell_x == cell_x and obj_cell_y == cell_y:
                                    print(f"Found destructible element {obj.tag} at ({obj_cell_x}, {obj_cell_y})")
                                    found_destructible = True
                                    
                                    # Damage the destructible element
                                    if obj.tag == "petrol_barrel":
                                        result = obj.take_damage(projectile.damage * 2)  # Double damage to petrol barrels
                                        print(f"Petrol barrel damaged! Result: {result}")
                                        if isinstance(result, dict) and result.get('destroyed'):
                                            print(f"Petrol barrel destroyed!")
                                            # Update map data
                                            level_manager.map_data.set_cell(cell_x, cell_y, level_manager.map_data.EMPTY)
                                            # Add explosion effect
                                            explosion_x = cell_x * level_manager.map_data.cell_size + level_manager.map_data.cell_size // 2
                                            explosion_y = cell_y * level_manager.map_data.cell_size + level_manager.map_data.cell_size // 2
                                            visual_effects.add_explosion(explosion_x, explosion_y, size=100)  # Larger explosion
                                            
                                            # Handle explosion damage to nearby objects
                                            explosion_radius = 96  # Larger radius (3 cells)
                                            
                                            # Check all game objects for explosion damage
                                            for target_obj in game_engine.game_objects:
                                                if target_obj.active and target_obj != obj:
                                                    # Calculate distance from explosion center to target
                                                    target_center_x = target_obj.x + target_obj.width / 2
                                                    target_center_y = target_obj.y + target_obj.height / 2
                                                    dx = target_center_x - explosion_x
                                                    dy = target_center_y - explosion_y
                                                    distance = math.sqrt(dx * dx + dy * dy)
                                                    
                                                    # If target is within explosion radius, damage it
                                                    if distance < explosion_radius:
                                                        # Calculate damage based on distance (closer = more damage)
                                                        damage_ratio = 1.0 - (distance / explosion_radius)
                                                        damage = int(50 * damage_ratio)  # Base explosion damage of 50
                                                        
                                                        # Apply damage if target can take damage
                                                        if hasattr(target_obj, 'take_damage') and damage > 0:
                                                            print(f"Explosion damaged {target_obj.tag if hasattr(target_obj, 'tag') else 'object'} for {damage} damage")
                                                            
                                                            # Handle different object types
                                                            if hasattr(target_obj, 'tag') and target_obj.tag == 'petrol_barrel':
                                                                # Chain reaction for other petrol barrels
                                                                barrel_result = target_obj.take_damage(damage)
                                                                if barrel_result.get('destroyed'):
                                                                    # Update map data for destroyed barrel
                                                                    barrel_cell_x = int((target_obj.x + target_obj.width / 2) // level_manager.map_data.cell_size)
                                                                    barrel_cell_y = int((target_obj.y + target_obj.height / 2) // level_manager.map_data.cell_size)
                                                                    level_manager.map_data.set_cell(barrel_cell_x, barrel_cell_y, level_manager.map_data.EMPTY)
                                                            else:
                                                                # Normal damage for other objects
                                                                target_obj.take_damage(damage)
                                            
                                            # Play explosion sound
                                            if game_engine.sound_manager:
                                                game_engine.sound_manager.play_sound('explosion')
                                    else:
                                        # Increase damage to rock piles for faster destruction
                                        rock_pile_damage = projectile.damage * 1.5
                                        print(f"Damaging rock pile with {rock_pile_damage} damage")
                                        destroyed = obj.take_damage(rock_pile_damage)
                                        print(f"Rock pile damaged! Destroyed: {destroyed}")
                                        
                                        # Add visual effects for rock pile damage
                                        impact_x = obj.x + obj.width // 2
                                        impact_y = obj.y + obj.height // 2
                                        
                                        # Calculate damage percentage
                                        damage_percentage = 1.0 - (obj.health / obj.max_health)
                                        
                                        # Scale effects based on damage percentage
                                        num_debris = int(10 + 15 * damage_percentage)  # More debris as damage increases
                                        debris_size_max = int(3 + 3 * damage_percentage)  # Larger debris as damage increases
                                        dust_size = int(20 + 20 * damage_percentage)  # Larger dust cloud as damage increases
                                        impact_size = int(15 + 10 * damage_percentage)  # Larger impact as damage increases
                                        
                                        # Add debris effect
                                        for i in range(num_debris):
                                            debris_x = impact_x + random.uniform(-20, 20)
                                            debris_y = impact_y + random.uniform(-20, 20)
                                            debris_size = random.randint(1, debris_size_max)
                                            
                                            # Vary debris color based on damage
                                            if damage_percentage < 0.5:
                                                debris_color = (100, 90, 80)  # Gray/brown
                                            else:
                                                # More reddish as damage increases
                                                red_tint = min(255, int(100 + 100 * damage_percentage))
                                                debris_color = (red_tint, 90, 80)
                                                
                                            # Calculate random velocity for debris
                                            velocity_scale = 50 + 50 * damage_percentage  # Faster debris as damage increases
                                            vx = random.uniform(-velocity_scale, velocity_scale)
                                            vy = random.uniform(-velocity_scale, 20)
                                            visual_effects.add_particle(debris_x, debris_y, debris_size, debris_color, 
                                                                      duration=0.5, velocity=(vx, vy), gravity=True)
                                        
                                        # Add dust cloud
                                        visual_effects.add_dust_cloud(impact_x, impact_y, size=dust_size, duration=0.7)
                                        
                                        # Add impact effect
                                        visual_effects.add_impact(impact_x, impact_y, size=impact_size)
                                        
                                        # Add small smoke effect for heavily damaged rock piles
                                        if damage_percentage > 0.5:
                                            visual_effects.add_smoke(impact_x, impact_y, intensity=damage_percentage, duration=1.0)
                                        
                                        if destroyed:
                                            print(f"Rock pile destroyed!")
                                            # Add explosion effect for destroyed rock pile - brown/orange color for rock
                                            visual_effects.add_explosion(impact_x, impact_y, size=40, 
                                                                      color=(180, 100, 50), duration=0.8)
                                            
                                            # Add more debris for destruction - lots of flying rocks
                                            for i in range(30):
                                                # Spread debris in all directions
                                                angle = random.uniform(0, 2 * math.pi)
                                                distance = random.uniform(5, 40)
                                                debris_x = impact_x + math.cos(angle) * distance
                                                debris_y = impact_y + math.sin(angle) * distance
                                                
                                                # Vary debris size and color
                                                debris_size = random.randint(2, 6)
                                                
                                                # Different colors for variety
                                                if random.random() < 0.3:
                                                    debris_color = (150, 120, 90)  # Lighter brown
                                                elif random.random() < 0.6:
                                                    debris_color = (120, 100, 80)  # Medium brown
                                                else:
                                                    debris_color = (90, 80, 70)    # Darker brown
                                                
                                                # Calculate random velocity for debris with more force
                                                speed = random.uniform(80, 150)
                                                vx = math.cos(angle) * speed
                                                vy = math.sin(angle) * speed - random.uniform(20, 50)  # Add upward boost
                                                
                                                visual_effects.add_particle(debris_x, debris_y, debris_size, debris_color, 
                                                                          duration=random.uniform(0.8, 1.5), 
                                                                          velocity=(vx, vy), gravity=True)
                                            
                                            # Add dust cloud
                                            visual_effects.add_dust_cloud(impact_x, impact_y, size=50, duration=1.2)
                                            
                                            # Add smoke effect
                                            visual_effects.add_smoke(impact_x, impact_y, intensity=1.0, duration=1.5)
                                            
                                            # Update map data
                                            level_manager.map_data.set_cell(cell_x, cell_y, level_manager.map_data.EMPTY)
                                            
                                            # Play rock destruction sound
                                            if game_engine.sound_manager:
                                                game_engine.sound_manager.play_sound('impact')
                                    
                                    break
                        
                        if not found_destructible:
                            print(f"No destructible element found at ({cell_x}, {cell_y})")
                    
                    # Deactivate the projectile
                    projectile.active = False
                else:
                    # No collision, update the projectile position
                    projectile.x = next_x
                    projectile.y = next_y
                
                # Update lifetime
                projectile.time_alive += game_engine.delta_time
                if projectile.time_alive >= projectile.lifetime:
                    projectile.active = False
                
                # Check if the projectile is no longer active
                if not projectile.active:
                    
                    # Projectile hit something or expired - add impact effect
                    impact_x = projectile.x + projectile.width // 2
                    impact_y = projectile.y + projectile.height // 2
                    visual_effects.add_impact(impact_x, impact_y)
                    
                    # Play impact sound
                    if game_engine.sound_manager:
                        game_engine.sound_manager.play_sound('impact')
                    
                    # Clean up projectile effects
                    projectile_renderer.cleanup_projectile_effects(projectile)
                    
                    projectiles.remove(projectile)
                    game_engine.remove_game_object(projectile)
                    continue
                    
                # Check for collisions with tanks
                for tank in [player_tank] + level_manager.enemy_tanks:
                    if tank.active and projectile.active and tank != projectile.owner and projectile.collides_with(tank):
                        # Add impact effect
                        impact_x = projectile.x + projectile.width // 2
                        impact_y = projectile.y + projectile.height // 2
                        visual_effects.add_impact(impact_x, impact_y)
                        
                        # Play impact sound
                        if game_engine.sound_manager:
                            game_engine.sound_manager.play_sound('impact')
                        
                        # Damage the tank
                        tank.take_damage(projectile.damage)
                        
                        # Add explosion effect if tank is destroyed
                        if not tank.active:
                            explosion_x = tank.x + tank.width // 2
                            explosion_y = tank.y + tank.height // 2
                            visual_effects.add_explosion(explosion_x, explosion_y, size=60)
                            
                            # Play explosion sound
                            if game_engine.sound_manager:
                                if tank.tag == "player":
                                    game_engine.sound_manager.play_sound('explosion')
                                else:
                                    game_engine.sound_manager.play_sound('enemy_destroyed')
                        
                        # Clean up projectile effects
                        projectile_renderer.cleanup_projectile_effects(projectile)
                        
                        # Remove the projectile
                        projectile.active = False
                        projectiles.remove(projectile)
                        game_engine.remove_game_object(projectile)
                        break
            
            # Update the level manager
            level_manager.update(game_engine.delta_time)
            
            # Update visual effects
            visual_effects.update(game_engine.delta_time)
        
        # Custom render function to display the map, tanks, and projectiles
        def custom_render():
            game_engine.renderer.clear_screen()
            
            # Only render game objects if not showing game over/victory screens
            if not (game_engine.game_state_manager.show_game_over_screen or 
                   game_engine.game_state_manager.show_victory_screen):
                
                # Render the map with enhanced visuals
                if level_manager.map_data:
                    map_renderer.render_map(game_engine.screen, level_manager.map_data)
                    # Render background atmospheric effects
                    map_renderer.render_background_effects(game_engine.screen, level_manager.map_data)
                
                # Render the tanks with enhanced visuals
                if player_tank.active:
                    tank_renderer.render_tank(game_engine.screen, player_tank)
                    # Add smoke effect for heavily damaged player tank
                    if hasattr(player_tank, 'health') and hasattr(player_tank, 'max_health'):
                        damage_ratio = 1 - (player_tank.health / player_tank.max_health)
                        if damage_ratio > 0.6:  # Heavy damage
                            smoke_x = player_tank.x + player_tank.width // 2
                            smoke_y = player_tank.y + player_tank.height // 4
                            visual_effects.add_smoke(smoke_x, smoke_y, intensity=damage_ratio, duration=0.5)
                            
                for enemy_tank in level_manager.enemy_tanks:
                    if enemy_tank.active:
                        tank_renderer.render_tank(game_engine.screen, enemy_tank)
                        # Add smoke effect for heavily damaged enemy tanks
                        if hasattr(enemy_tank, 'health') and hasattr(enemy_tank, 'max_health'):
                            damage_ratio = 1 - (enemy_tank.health / enemy_tank.max_health)
                            if damage_ratio > 0.6:  # Heavy damage
                                smoke_x = enemy_tank.x + enemy_tank.width // 2
                                smoke_y = enemy_tank.y + enemy_tank.height // 4
                                visual_effects.add_smoke(smoke_x, smoke_y, intensity=damage_ratio, duration=0.5)
                
                # Render the projectiles with enhanced effects
                for projectile in projectiles:
                    if projectile.active:
                        projectile_renderer.render_projectile(game_engine.screen, projectile)
                
                # Render visual effects (explosions, impacts, etc.)
                visual_effects.render(game_engine.screen)
                
                # Render level transition if active
                if hasattr(level_manager, 'transition'):
                    level_manager.render_transition(game_engine.screen)
            
            # Render game state UI (score, health, game over screens, etc.)
            if game_engine.game_state_manager:
                game_engine.game_state_manager.render(game_engine.renderer)
            
            # Update the display
            game_engine.renderer.update_display()
        
        # Custom restart function
        def restart_game():
            nonlocal projectiles
            
            # Clear projectiles
            for projectile in projectiles:
                game_engine.remove_game_object(projectile)
            projectiles = []
            
            # Clear visual effects
            visual_effects.clear_all_effects()
            
            # Reset player tank
            player_tank.health = 100
            player_tank.max_health = 100
            player_tank.active = True
            player_tank.x = 400
            player_tank.y = 300
            
            # Reset level manager
            level_manager.reset()
            
            # Reset game state manager
            game_engine.game_state_manager.reset()
        
        # Override the game engine's restart method
        original_restart = game_engine.restart_game
        def enhanced_restart():
            restart_game()
            game_engine.game_state_manager.restart_requested = False
        
        game_engine.restart_game = enhanced_restart
        
        # Custom event handler that includes restart functionality
        def custom_handle_events():
            # Get events first
            events = pygame.event.get()
            
            # Process events for game state manager (for restart functionality)
            if game_engine.game_state_manager:
                restart_requested = game_engine.game_state_manager.process_events(events)
                if restart_requested:
                    print("Restart requested - restarting game!")
                    game_engine.restart_game()
                    return
            
            # Handle other events (quit, performance toggles, etc.)
            for event in events:
                if event.type == pygame.QUIT:
                    game_engine.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_engine.running = False
                    elif event.key == pygame.K_F1 and game_engine.enable_performance_monitoring:
                        game_engine.performance_monitor.toggle_overlay()
                    elif event.key == pygame.K_F2:
                        game_engine.enable_spatial_partitioning = not game_engine.enable_spatial_partitioning
                        print(f"Spatial partitioning: {'ON' if game_engine.enable_spatial_partitioning else 'OFF'}")
                    elif event.key == pygame.K_F3:
                        game_engine.enable_viewport_culling = not game_engine.enable_viewport_culling
                        print(f"Viewport culling: {'ON' if game_engine.enable_viewport_culling else 'OFF'}")
                    elif event.key == pygame.K_F5:
                        game_engine.performance_monitor.print_performance_summary()
                    elif event.key == pygame.K_r:
                        # Debug: Print when R is pressed
                        print(f"R key pressed! Game over: {game_engine.game_state_manager.show_game_over_screen}, Victory: {game_engine.game_state_manager.show_victory_screen}")
        
        # Replace the game engine's methods with our custom ones
        game_engine.handle_events = custom_handle_events
        game_engine.update = lambda: (custom_update(), game_engine.game_state_manager.update(game_engine.delta_time))
        game_engine.render = custom_render
        
        # Enable performance optimizations
        game_engine.set_performance_options(
            spatial_partitioning=True,
            viewport_culling=True,
            render_batching=False,  # Keep disabled for compatibility
            performance_monitoring=True
        )
        
        # Start the game loop
        print("Starting Tank Game...")
        print("Controls:")
        print("  Arrow Keys: Move tank")
        print("  Space: Fire")
        print("  R: Restart (when game over)")
        print("  F1: Toggle performance overlay")
        print("  F2: Toggle spatial partitioning")
        print("  F3: Toggle viewport culling")
        print("  F5: Print performance summary")
        print("  ESC/Close Window: Quit")
        
        game_engine.start_game()
        
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    main()