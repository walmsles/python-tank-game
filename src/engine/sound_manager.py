"""
Sound Manager module for the Tank Game.
Handles all sound effects and audio management.
"""
import pygame
import os
from typing import Dict, Optional


class SoundManager:
    """
    Manages all sound effects and audio for the game.
    """
    
    def __init__(self, volume: float = 0.7):
        """
        Initialize the sound manager.
        
        Args:
            volume (float): Master volume level (0.0 to 1.0)
        """
        self.volume = volume
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.enabled = True
        self.initialized = False
        
        # Initialize pygame mixer
        self._initialize_mixer()
        
    def _initialize_mixer(self):
        """Initialize pygame mixer for sound playback."""
        try:
            # Initialize mixer with reasonable settings
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.initialized = True
            print("Sound system initialized successfully")
        except pygame.error as e:
            print(f"Warning: Could not initialize sound system: {e}")
            self.enabled = False
            self.initialized = False
    
    def create_sound_effect(self, frequency: int, duration: float, wave_type: str = 'sine') -> pygame.mixer.Sound:
        """
        Create a procedural sound effect.
        
        Args:
            frequency (int): Frequency in Hz
            duration (float): Duration in seconds
            wave_type (str): Type of wave ('sine', 'square', 'sawtooth')
            
        Returns:
            pygame.mixer.Sound: Generated sound effect
        """
        if not self.initialized:
            return None
            
        import numpy as np
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generate time array
        t = np.linspace(0, duration, frames, False)
        
        # Generate waveform based on type
        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == 'sawtooth':
            wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
        else:
            wave = np.sin(2 * np.pi * frequency * t)  # Default to sine
        
        # Apply envelope to prevent clicks
        envelope = np.ones_like(wave)
        fade_frames = int(0.01 * sample_rate)  # 10ms fade
        if fade_frames > 0:
            envelope[:fade_frames] = np.linspace(0, 1, fade_frames)
            envelope[-fade_frames:] = np.linspace(1, 0, fade_frames)
        
        wave *= envelope
        
        # Convert to 16-bit integers
        wave = (wave * 32767).astype(np.int16)
        
        # Create stereo sound
        stereo_wave = np.zeros((frames, 2), dtype=np.int16)
        stereo_wave[:, 0] = wave  # Left channel
        stereo_wave[:, 1] = wave  # Right channel
        
        # Create pygame sound
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound
    
    def create_tank_fire_sound(self) -> pygame.mixer.Sound:
        """Create a realistic tank firing sound effect."""
        if not self.initialized:
            return None
            
        import numpy as np
        
        sample_rate = 22050
        duration = 0.8  # Longer duration for more realistic sound
        frames = int(duration * sample_rate)
        
        # Generate time array
        t = np.linspace(0, duration, frames, False)
        
        # Create multiple components for a realistic tank gun sound (deeper/lower register)
        
        # 1. Sharp initial crack (lower frequency, very short)
        crack_duration = 0.05  # 50ms
        crack_frames = int(crack_duration * sample_rate)
        crack_t = t[:crack_frames]
        crack = np.sin(2 * np.pi * 800 * crack_t) * np.exp(-crack_t * 15)  # Reduced from 2000Hz to 800Hz
        
        # 2. Deep boom (very low frequency, longer)
        boom_start = 0.02  # Start slightly after crack
        boom_duration = 0.5
        boom_frames = int(boom_duration * sample_rate)
        boom_start_frame = int(boom_start * sample_rate)
        boom_t = np.linspace(0, boom_duration, boom_frames, False)
        boom = 1.0 * np.sin(2 * np.pi * 45 * boom_t) * np.exp(-boom_t * 2.5)  # Reduced from 80Hz to 45Hz, longer decay
        
        # 3. Mid-frequency punch (lower)
        punch_start = 0.01
        punch_duration = 0.25
        punch_frames = int(punch_duration * sample_rate)
        punch_start_frame = int(punch_start * sample_rate)
        punch_t = np.linspace(0, punch_duration, punch_frames, False)
        punch = 0.7 * np.sin(2 * np.pi * 200 * punch_t) * np.exp(-punch_t * 6)  # Reduced from 400Hz to 200Hz
        
        # 4. White noise burst for realism
        noise_duration = 0.15
        noise_frames = int(noise_duration * sample_rate)
        noise = 0.3 * np.random.normal(0, 1, noise_frames) * np.exp(-np.linspace(0, noise_duration, noise_frames) * 10)
        
        # Combine all components
        sound_wave = np.zeros(frames)
        
        # Add crack
        sound_wave[:len(crack)] += crack
        
        # Add boom
        if boom_start_frame + len(boom) <= frames:
            sound_wave[boom_start_frame:boom_start_frame + len(boom)] += boom
        
        # Add punch
        if punch_start_frame + len(punch) <= frames:
            sound_wave[punch_start_frame:punch_start_frame + len(punch)] += punch
        
        # Add noise
        sound_wave[:len(noise)] += noise
        
        # Apply overall envelope
        envelope = np.ones_like(sound_wave)
        fade_frames = int(0.02 * sample_rate)  # 20ms fade out
        if fade_frames > 0:
            envelope[-fade_frames:] = np.linspace(1, 0, fade_frames)
        
        sound_wave *= envelope
        
        # Normalize and prevent clipping
        max_val = np.max(np.abs(sound_wave))
        if max_val > 0:
            sound_wave = sound_wave / max_val * 0.8  # Leave some headroom
        
        # Convert to 16-bit integers
        sound_wave = (sound_wave * 32767).astype(np.int16)
        
        # Create stereo sound
        stereo_wave = np.zeros((frames, 2), dtype=np.int16)
        stereo_wave[:, 0] = sound_wave  # Left channel
        stereo_wave[:, 1] = sound_wave  # Right channel
        
        return pygame.sndarray.make_sound(stereo_wave)

    def create_tank_engine_sound(self) -> pygame.mixer.Sound:
        """Create a tank engine sound effect."""
        if not self.initialized:
            return None
            
        import numpy as np
        
        sample_rate = 22050
        duration = 0.5
        frames = int(duration * sample_rate)
        
        # Create a low-frequency rumble with some variation
        t = np.linspace(0, duration, frames, False)
        
        # Base engine rumble (low frequency)
        base_freq = 80
        rumble = np.sin(2 * np.pi * base_freq * t)
        
        # Add some higher frequency components for texture
        rumble += 0.3 * np.sin(2 * np.pi * base_freq * 2 * t)
        rumble += 0.2 * np.sin(2 * np.pi * base_freq * 3 * t)
        
        # Add some noise for realism
        noise = np.random.normal(0, 0.1, frames)
        rumble += noise
        
        # Apply envelope
        envelope = np.ones_like(rumble)
        fade_frames = int(0.05 * sample_rate)  # 50ms fade
        if fade_frames > 0:
            envelope[:fade_frames] = np.linspace(0, 1, fade_frames)
            envelope[-fade_frames:] = np.linspace(1, 0, fade_frames)
        
        rumble *= envelope * 0.3  # Keep volume moderate
        
        # Convert to 16-bit integers
        rumble = (rumble * 32767).astype(np.int16)
        
        # Create stereo sound
        stereo_rumble = np.zeros((frames, 2), dtype=np.int16)
        stereo_rumble[:, 0] = rumble
        stereo_rumble[:, 1] = rumble
        
        return pygame.sndarray.make_sound(stereo_rumble)
    
    def create_impact_sound(self) -> pygame.mixer.Sound:
        """Create a realistic projectile impact sound effect."""
        if not self.initialized:
            return None
            
        import numpy as np
        
        sample_rate = 22050
        duration = 0.4  # Moderate duration for impact
        frames = int(duration * sample_rate)
        
        # Generate time array
        t = np.linspace(0, duration, frames, False)
        
        # Create multiple components for a realistic impact sound
        
        # 1. Initial sharp crack (high frequency, very short)
        crack_duration = 0.04
        crack_frames = int(crack_duration * sample_rate)
        crack_t = t[:crack_frames]
        crack = 0.8 * np.sin(2 * np.pi * 1500 * crack_t) * np.exp(-crack_t * 25)  # Sharp, quick decay
        
        # 2. Mid-frequency thud (medium frequency, medium duration)
        thud_start = 0.01
        thud_duration = 0.2
        thud_frames = int(thud_duration * sample_rate)
        thud_start_frame = int(thud_start * sample_rate)
        thud_t = np.linspace(0, thud_duration, thud_frames, False)
        thud = 0.7 * np.sin(2 * np.pi * 180 * thud_t) * np.exp(-thud_t * 10)
        
        # 3. Low-frequency impact (lower frequency, slightly longer)
        impact_start = 0.02
        impact_duration = 0.25
        impact_frames = int(impact_duration * sample_rate)
        impact_start_frame = int(impact_start * sample_rate)
        impact_t = np.linspace(0, impact_duration, impact_frames, False)
        impact = 0.6 * np.sin(2 * np.pi * 80 * impact_t) * np.exp(-impact_t * 8)
        
        # 4. Debris/ricochet sound (noise-based)
        debris_duration = 0.15
        debris_frames = int(debris_duration * sample_rate)
        debris = 0.3 * np.random.normal(0, 1, debris_frames) * np.exp(-np.linspace(0, debris_duration, debris_frames) * 15)
        
        # Combine all components
        sound_wave = np.zeros(frames)
        
        # Add crack
        sound_wave[:len(crack)] += crack
        
        # Add thud
        if thud_start_frame + len(thud) <= frames:
            sound_wave[thud_start_frame:thud_start_frame + len(thud)] += thud
        
        # Add impact
        if impact_start_frame + len(impact) <= frames:
            sound_wave[impact_start_frame:impact_start_frame + len(impact)] += impact
        
        # Add debris
        sound_wave[:len(debris)] += debris
        
        # Apply overall envelope
        envelope = np.ones_like(sound_wave)
        fade_frames = int(0.05 * sample_rate)  # 50ms fade out
        if fade_frames > 0:
            envelope[-fade_frames:] = np.linspace(1, 0, fade_frames)
        
        sound_wave *= envelope
        
        # Normalize and prevent clipping
        max_val = np.max(np.abs(sound_wave))
        if max_val > 0:
            sound_wave = sound_wave / max_val * 0.8  # Leave some headroom
        
        # Convert to 16-bit integers
        sound_wave = (sound_wave * 32767).astype(np.int16)
        
        # Create stereo sound
        stereo_wave = np.zeros((frames, 2), dtype=np.int16)
        stereo_wave[:, 0] = sound_wave  # Left channel
        stereo_wave[:, 1] = sound_wave  # Right channel
        
        return pygame.sndarray.make_sound(stereo_wave)
        
    def create_explosion_sound(self) -> pygame.mixer.Sound:
        """Create a realistic explosion sound effect."""
        if not self.initialized:
            return None
            
        import numpy as np
        
        sample_rate = 22050
        duration = 1.2  # Longer duration for explosion
        frames = int(duration * sample_rate)
        
        # Generate time array
        t = np.linspace(0, duration, frames, False)
        
        # Create multiple components for a realistic explosion (much deeper and lower)
        
        # 1. Initial sharp crack/bang (lower frequency, very short)
        crack_duration = 0.08
        crack_frames = int(crack_duration * sample_rate)
        crack_t = t[:crack_frames]
        crack = 0.6 * np.sin(2 * np.pi * 600 * crack_t) * np.exp(-crack_t * 12)  # Reduced from 1200Hz to 600Hz
        
        # 2. Deep rumbling boom (MUCH lower frequency, longer)
        boom_start = 0.03
        boom_duration = 1.0  # Longer duration
        boom_frames = int(boom_duration * sample_rate)
        boom_start_frame = int(boom_start * sample_rate)
        boom_t = np.linspace(0, boom_duration, boom_frames, False)
        # Much lower frequency components for deeper sound
        boom = 1.8 * np.sin(2 * np.pi * 18 * boom_t) * np.exp(-boom_t * 1.5)  # Reduced from 35Hz to 18Hz
        boom += 1.4 * np.sin(2 * np.pi * 28 * boom_t) * np.exp(-boom_t * 1.8)  # Reduced from 60Hz to 28Hz
        boom += 1.0 * np.sin(2 * np.pi * 42 * boom_t) * np.exp(-boom_t * 2.2)  # Reduced from 90Hz to 42Hz
        boom += 0.8 * np.sin(2 * np.pi * 55 * boom_t) * np.exp(-boom_t * 2.5)  # Added even more low end
        
        # 3. Mid-frequency explosion body (much lower)
        body_start = 0.02
        body_duration = 0.5  # Slightly longer
        body_frames = int(body_duration * sample_rate)
        body_start_frame = int(body_start * sample_rate)
        body_t = np.linspace(0, body_duration, body_frames, False)
        body = 0.8 * np.sin(2 * np.pi * 80 * body_t) * np.exp(-body_t * 3.5)   # Reduced from 180Hz to 80Hz
        body += 0.6 * np.sin(2 * np.pi * 120 * body_t) * np.exp(-body_t * 4.0)  # Reduced from 280Hz to 120Hz
        
        # 4. Crackling/debris noise (longer duration)
        noise_duration = 0.6
        noise_frames = int(noise_duration * sample_rate)
        noise_t = np.linspace(0, noise_duration, noise_frames, False)
        # Filtered noise that sounds like debris and crackling
        noise = 0.4 * np.random.normal(0, 1, noise_frames)
        # Apply a decaying envelope to the noise
        noise *= np.exp(-noise_t * 3)
        # Add some periodic crackling
        crackling = 0.2 * np.random.choice([-1, 0, 1], noise_frames, p=[0.1, 0.8, 0.1])
        noise += crackling * np.exp(-noise_t * 4)
        
        # 5. Reverb tail (low-level rumble that fades out)
        reverb_start = 0.3
        reverb_duration = 0.9
        reverb_frames = int(reverb_duration * sample_rate)
        reverb_start_frame = int(reverb_start * sample_rate)
        reverb_t = np.linspace(0, reverb_duration, reverb_frames, False)
        reverb = 0.3 * np.sin(2 * np.pi * 25 * reverb_t) * np.exp(-reverb_t * 1.2)
        reverb += 0.2 * np.sin(2 * np.pi * 40 * reverb_t) * np.exp(-reverb_t * 1.5)
        
        # Combine all components
        sound_wave = np.zeros(frames)
        
        # Add crack
        sound_wave[:len(crack)] += crack
        
        # Add boom
        if boom_start_frame + len(boom) <= frames:
            sound_wave[boom_start_frame:boom_start_frame + len(boom)] += boom
        
        # Add body
        if body_start_frame + len(body) <= frames:
            sound_wave[body_start_frame:body_start_frame + len(body)] += body
        
        # Add noise
        sound_wave[:len(noise)] += noise
        
        # Add reverb
        if reverb_start_frame + len(reverb) <= frames:
            sound_wave[reverb_start_frame:reverb_start_frame + len(reverb)] += reverb
        
        # Apply overall envelope (gentle fade out at the end)
        envelope = np.ones_like(sound_wave)
        fade_frames = int(0.1 * sample_rate)  # 100ms fade out
        if fade_frames > 0:
            envelope[-fade_frames:] = np.linspace(1, 0, fade_frames)
        
        sound_wave *= envelope
        
        # Normalize and prevent clipping
        max_val = np.max(np.abs(sound_wave))
        if max_val > 0:
            sound_wave = sound_wave / max_val * 0.85  # Leave some headroom
        
        # Convert to 16-bit integers
        sound_wave = (sound_wave * 32767).astype(np.int16)
        
        # Create stereo sound
        stereo_wave = np.zeros((frames, 2), dtype=np.int16)
        stereo_wave[:, 0] = sound_wave  # Left channel
        stereo_wave[:, 1] = sound_wave  # Right channel
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def load_sounds(self):
        """Load or create all game sound effects with optimized startup."""
        if not self.initialized:
            return
            
        try:
            print("Creating tank fire sound...")
            self.sounds['tank_fire'] = self.create_tank_fire_sound()  # Use realistic tank firing sound
            print("Creating impact sound...")
            self.sounds['impact'] = self.create_impact_sound()  # Use realistic impact sound
            
            # Set volumes for pre-loaded sounds
            if self.sounds['tank_fire']:
                self.sounds['tank_fire'].set_volume(0.6 * self.volume)
                print("Tank fire sound created successfully")
            if self.sounds['impact']:
                self.sounds['impact'].set_volume(0.4 * self.volume)
                print("Impact sound created successfully")
            
            print(f"Loaded {len(self.sounds)} essential sound effects")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Warning: Could not create sound effects: {e}")
            self.enabled = False
    
    def _load_sound_on_demand(self, sound_name: str):
        """Load a sound effect on-demand to improve startup performance."""
        if not self.initialized or sound_name in self.sounds:
            return
            
        try:
            if sound_name == 'tank_move':
                # Create simplified tank movement sound
                self.sounds['tank_move'] = self.create_sound_effect(80, 0.5, 'sine')
                if self.sounds['tank_move']:
                    self.sounds['tank_move'].set_volume(0.3 * self.volume)
            elif sound_name == 'explosion':
                self.sounds['explosion'] = self.create_explosion_sound()  # Use realistic explosion sound
                if self.sounds['explosion']:
                    self.sounds['explosion'].set_volume(0.8 * self.volume)
            elif sound_name == 'enemy_destroyed':
                self.sounds['enemy_destroyed'] = self.create_explosion_sound()  # Use realistic explosion sound
                if self.sounds['enemy_destroyed']:
                    self.sounds['enemy_destroyed'].set_volume(0.9 * self.volume)
        except Exception as e:
            print(f"Warning: Could not create sound effect '{sound_name}': {e}")
    
    def play_sound(self, sound_name: str, loops: int = 0) -> Optional[pygame.mixer.Channel]:
        """
        Play a sound effect.
        
        Args:
            sound_name (str): Name of the sound to play
            loops (int): Number of times to loop (-1 for infinite)
            
        Returns:
            pygame.mixer.Channel: The channel playing the sound, or None
        """
        if not self.enabled or not self.initialized:
            return None
            
        # Load sound on-demand if not already loaded
        if sound_name not in self.sounds:
            self._load_sound_on_demand(sound_name)
            
        # Check if sound exists after loading
        if sound_name not in self.sounds:
            return None
            
        sound = self.sounds[sound_name]
        if sound:
            try:
                return sound.play(loops)
            except pygame.error as e:
                print(f"Warning: Could not play sound '{sound_name}': {e}")
        
        return None
    
    def stop_sound(self, sound_name: str):
        """
        Stop a specific sound effect.
        
        Args:
            sound_name (str): Name of the sound to stop
        """
        if not self.enabled or not self.initialized or sound_name not in self.sounds:
            return
            
        sound = self.sounds[sound_name]
        if sound:
            sound.stop()
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds."""
        if self.initialized:
            pygame.mixer.stop()
    
    def set_volume(self, volume: float):
        """
        Set the master volume.
        
        Args:
            volume (float): Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        
        # Update volume for all loaded sounds
        for sound_name, sound in self.sounds.items():
            if sound:
                if sound_name == 'tank_move':
                    sound.set_volume(0.3 * self.volume)
                elif sound_name == 'tank_fire':
                    sound.set_volume(0.6 * self.volume)
                elif sound_name == 'impact':
                    sound.set_volume(0.4 * self.volume)
                else:
                    sound.set_volume(0.7 * self.volume)
    
    def toggle_sound(self):
        """Toggle sound on/off."""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_all_sounds()
    
    def is_sound_enabled(self) -> bool:
        """Check if sound is enabled."""
        return self.enabled and self.initialized
    
    def cleanup(self):
        """Clean up sound resources."""
        if self.initialized:
            self.stop_all_sounds()
            pygame.mixer.quit()
            self.initialized = False