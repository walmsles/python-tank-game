#!/usr/bin/env python3
"""
Test script for the sound system in the Tank Game.
This script tests the basic functionality of the sound manager.
"""
import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.engine.sound_manager import SoundManager


def test_sound_system():
    """Test the sound system functionality."""
    print("Testing Tank Game Sound System")
    print("=" * 40)
    
    # Initialize the sound manager
    print("1. Initializing sound manager...")
    sound_manager = SoundManager(volume=0.5)
    
    if not sound_manager.is_sound_enabled():
        print("   WARNING: Sound system could not be initialized!")
        print("   This might be due to missing audio drivers or pygame mixer issues.")
        return False
    
    print("   ✓ Sound manager initialized successfully")
    
    # Load sounds
    print("2. Loading sound effects...")
    sound_manager.load_sounds()
    print(f"   ✓ Loaded {len(sound_manager.sounds)} sound effects")
    
    # Test each sound effect
    print("3. Testing sound effects...")
    
    test_sounds = [
        ('tank_fire', 'Tank firing sound'),
        ('tank_move', 'Tank movement sound'),
        ('explosion', 'Explosion sound'),
        ('impact', 'Impact sound'),
        ('enemy_destroyed', 'Enemy destroyed sound')
    ]
    
    for sound_name, description in test_sounds:
        print(f"   Testing {description}...")
        if sound_name in sound_manager.sounds:
            channel = sound_manager.play_sound(sound_name)
            if channel:
                print(f"   ✓ {description} played successfully")
                time.sleep(1.0)  # Wait a bit between sounds
            else:
                print(f"   ✗ Failed to play {description}")
        else:
            print(f"   ✗ {description} not found in loaded sounds")
    
    # Test volume control
    print("4. Testing volume control...")
    original_volume = sound_manager.volume
    sound_manager.set_volume(0.2)
    print(f"   ✓ Volume changed from {original_volume} to {sound_manager.volume}")
    
    # Test sound toggle
    print("5. Testing sound toggle...")
    sound_manager.toggle_sound()
    enabled_after_toggle = sound_manager.is_sound_enabled()
    print(f"   ✓ Sound enabled after toggle: {enabled_after_toggle}")
    
    # Re-enable sound
    if not enabled_after_toggle:
        sound_manager.toggle_sound()
    
    # Test movement sound looping
    print("6. Testing looped movement sound...")
    channel = sound_manager.play_sound('tank_move', loops=-1)
    if channel:
        print("   ✓ Movement sound started (looping)")
        time.sleep(2.0)
        sound_manager.stop_sound('tank_move')
        print("   ✓ Movement sound stopped")
    
    # Cleanup
    print("7. Cleaning up...")
    sound_manager.cleanup()
    print("   ✓ Sound system cleaned up")
    
    print("\nSound system test completed successfully!")
    return True


def main():
    """Main function to run the sound system test."""
    try:
        success = test_sound_system()
        if success:
            print("\n🎵 All sound system tests passed!")
        else:
            print("\n❌ Sound system tests failed!")
            return 1
    except Exception as e:
        print(f"\n❌ Error during sound system test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())