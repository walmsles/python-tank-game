"""
Performance Monitor module for the Tank Game.
This module tracks and displays performance metrics like FPS, frame times, and system usage.
"""
import time
import pygame
from collections import deque
from typing import Dict, Any, Optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
import threading


class PerformanceMonitor:
    """
    Monitors and tracks game performance metrics.
    """
    
    def __init__(self, max_samples: int = 60):
        """
        Initialize the performance monitor.
        
        Args:
            max_samples: Maximum number of samples to keep for averaging
        """
        self.max_samples = max_samples
        
        # Frame timing
        self.frame_times = deque(maxlen=max_samples)
        self.last_frame_time = time.time()
        self.fps = 0.0
        self.avg_frame_time = 0.0
        self.min_frame_time = float('inf')
        self.max_frame_time = 0.0
        
        # Update timing
        self.update_times = deque(maxlen=max_samples)
        self.render_times = deque(maxlen=max_samples)
        self.collision_times = deque(maxlen=max_samples)
        
        # System metrics
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.memory_usage_mb = 0.0
        
        # Game-specific metrics
        self.object_count = 0
        self.collision_checks = 0
        self.spatial_grid_stats = {}
        
        # Display settings
        self.show_overlay = False
        self.font = None
        self.overlay_alpha = 180
        
        # Background thread for system monitoring
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_system_metrics, daemon=True)
        self._monitor_thread.start()
        
    def _monitor_system_metrics(self):
        """Background thread to monitor system metrics."""
        if not PSUTIL_AVAILABLE:
            return
            
        try:
            process = psutil.Process()
        except:
            return
        
        while self._monitoring:
            try:
                # CPU usage (averaged over 0.1 seconds)
                self.cpu_usage = process.cpu_percent(interval=0.1)
                
                # Memory usage
                memory_info = process.memory_info()
                self.memory_usage_mb = memory_info.rss / 1024 / 1024  # Convert to MB
                self.memory_usage = process.memory_percent()
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process might have ended or access denied
                break
            except Exception:
                # Other errors, continue monitoring
                pass
                
            time.sleep(0.5)  # Update system metrics every 0.5 seconds
            
    def start_frame(self):
        """Mark the start of a new frame."""
        current_time = time.time()
        
        if self.last_frame_time > 0:
            frame_time = current_time - self.last_frame_time
            self.frame_times.append(frame_time)
            
            # Update frame time statistics
            if len(self.frame_times) > 0:
                self.avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                self.fps = 1.0 / self.avg_frame_time if self.avg_frame_time > 0 else 0
                self.min_frame_time = min(self.frame_times)
                self.max_frame_time = max(self.frame_times)
                
        self.last_frame_time = current_time
        
    def record_update_time(self, update_time: float):
        """
        Record the time taken for game update logic.
        
        Args:
            update_time: Time in seconds for update phase
        """
        self.update_times.append(update_time)
        
    def record_render_time(self, render_time: float):
        """
        Record the time taken for rendering.
        
        Args:
            render_time: Time in seconds for render phase
        """
        self.render_times.append(render_time)
        
    def record_collision_time(self, collision_time: float):
        """
        Record the time taken for collision detection.
        
        Args:
            collision_time: Time in seconds for collision detection
        """
        self.collision_times.append(collision_time)
        
    def update_game_metrics(self, object_count: int, collision_checks: int, 
                          spatial_grid_stats: Optional[Dict[str, Any]] = None):
        """
        Update game-specific performance metrics.
        
        Args:
            object_count: Number of active game objects
            collision_checks: Number of collision pairs checked
            spatial_grid_stats: Statistics from spatial partitioning system
        """
        self.object_count = object_count
        self.collision_checks = collision_checks
        if spatial_grid_stats:
            self.spatial_grid_stats = spatial_grid_stats
            
    def toggle_overlay(self):
        """Toggle the performance overlay display."""
        self.show_overlay = not self.show_overlay
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        avg_update_time = sum(self.update_times) / len(self.update_times) if self.update_times else 0
        avg_render_time = sum(self.render_times) / len(self.render_times) if self.render_times else 0
        avg_collision_time = sum(self.collision_times) / len(self.collision_times) if self.collision_times else 0
        
        return {
            'fps': self.fps,
            'avg_frame_time_ms': self.avg_frame_time * 1000,
            'min_frame_time_ms': self.min_frame_time * 1000 if self.min_frame_time != float('inf') else 0,
            'max_frame_time_ms': self.max_frame_time * 1000,
            'avg_update_time_ms': avg_update_time * 1000,
            'avg_render_time_ms': avg_render_time * 1000,
            'avg_collision_time_ms': avg_collision_time * 1000,
            'cpu_usage_percent': self.cpu_usage,
            'memory_usage_mb': self.memory_usage_mb,
            'memory_usage_percent': self.memory_usage,
            'object_count': self.object_count,
            'collision_checks': self.collision_checks,
            'spatial_grid_stats': self.spatial_grid_stats
        }
        
    def render_overlay(self, screen: pygame.Surface):
        """
        Render the performance overlay on screen.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.show_overlay:
            return
            
        # Initialize font if needed
        if self.font is None:
            try:
                self.font = pygame.font.Font(None, 24)
            except pygame.error:
                return
                
        # Get performance metrics
        metrics = self.get_performance_summary()
        
        # Create overlay surface
        overlay_width = 300
        overlay_height = 280
        overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha))
        
        # Render text lines
        y_offset = 10
        line_height = 20
        text_color = (255, 255, 255)
        
        lines = [
            f"FPS: {metrics['fps']:.1f}",
            f"Frame Time: {metrics['avg_frame_time_ms']:.2f}ms",
            f"Min/Max: {metrics['min_frame_time_ms']:.2f}/{metrics['max_frame_time_ms']:.2f}ms",
            "",
            f"Update: {metrics['avg_update_time_ms']:.2f}ms",
            f"Render: {metrics['avg_render_time_ms']:.2f}ms",
            f"Collision: {metrics['avg_collision_time_ms']:.2f}ms",
            "",
            f"CPU: {metrics['cpu_usage_percent']:.1f}%",
            f"Memory: {metrics['memory_usage_mb']:.1f}MB ({metrics['memory_usage_percent']:.1f}%)",
            "",
            f"Objects: {metrics['object_count']}",
            f"Collision Checks: {metrics['collision_checks']}",
        ]
        
        # Add spatial grid stats if available
        if metrics['spatial_grid_stats']:
            stats = metrics['spatial_grid_stats']
            lines.extend([
                "",
                f"Grid Cells: {stats.get('occupied_cells', 0)}/{stats.get('total_cells', 0)}",
                f"Cell Utilization: {stats.get('cell_utilization', 0):.1%}",
                f"Avg Objects/Cell: {stats.get('avg_objects_per_cell', 0):.1f}"
            ])
        
        for line in lines:
            if line:  # Skip empty lines for spacing
                text_surface = self.font.render(line, True, text_color)
                overlay.blit(text_surface, (10, y_offset))
            y_offset += line_height
            
        # Render FPS graph (simple bar chart)
        if len(self.frame_times) > 1:
            graph_y = overlay_height - 60
            graph_height = 40
            graph_width = overlay_width - 20
            
            # Draw graph background
            pygame.draw.rect(overlay, (40, 40, 40), (10, graph_y, graph_width, graph_height))
            
            # Draw FPS bars
            max_fps = 120  # Scale for 120 FPS max
            bar_width = max(1, graph_width // len(self.frame_times))
            
            for i, frame_time in enumerate(self.frame_times):
                fps = 1.0 / frame_time if frame_time > 0 else 0
                bar_height = int((fps / max_fps) * graph_height)
                bar_height = min(bar_height, graph_height)
                
                # Color based on FPS (green = good, yellow = ok, red = bad)
                if fps >= 50:
                    color = (0, 255, 0)
                elif fps >= 30:
                    color = (255, 255, 0)
                else:
                    color = (255, 0, 0)
                    
                x = 10 + i * bar_width
                y = graph_y + graph_height - bar_height
                pygame.draw.rect(overlay, color, (x, y, bar_width - 1, bar_height))
                
        # Render the overlay
        screen.blit(overlay, (screen.get_width() - overlay_width - 10, 10))
        
    def log_performance_warning(self, metric: str, value: float, threshold: float):
        """
        Log a performance warning when metrics exceed thresholds.
        
        Args:
            metric: Name of the metric
            value: Current value
            threshold: Warning threshold
        """
        if value > threshold:
            print(f"Performance Warning: {metric} = {value:.2f} (threshold: {threshold:.2f})")
            
    def check_performance_thresholds(self):
        """Check performance metrics against warning thresholds."""
        metrics = self.get_performance_summary()
        
        # Check FPS threshold
        if metrics['fps'] < 30:
            self.log_performance_warning("FPS", metrics['fps'], 30)
            
        # Check frame time threshold (33ms = 30 FPS)
        if metrics['avg_frame_time_ms'] > 33:
            self.log_performance_warning("Frame Time (ms)", metrics['avg_frame_time_ms'], 33)
            
        # Check memory usage threshold
        if metrics['memory_usage_mb'] > 500:  # 500MB threshold
            self.log_performance_warning("Memory Usage (MB)", metrics['memory_usage_mb'], 500)
            
        # Check CPU usage threshold
        if metrics['cpu_usage_percent'] > 80:
            self.log_performance_warning("CPU Usage (%)", metrics['cpu_usage_percent'], 80)
            
    def cleanup(self):
        """Clean up resources and stop monitoring."""
        self._monitoring = False
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)


class PerformanceProfiler:
    """
    Context manager for profiling specific code sections.
    """
    
    def __init__(self, monitor: PerformanceMonitor, metric_name: str):
        """
        Initialize the profiler.
        
        Args:
            monitor: Performance monitor instance
            metric_name: Name of the metric being profiled
        """
        self.monitor = monitor
        self.metric_name = metric_name
        self.start_time = 0
        
    def __enter__(self):
        """Start profiling."""
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End profiling and record the time."""
        elapsed_time = time.time() - self.start_time
        
        if self.metric_name == 'update':
            self.monitor.record_update_time(elapsed_time)
        elif self.metric_name == 'render':
            self.monitor.record_render_time(elapsed_time)
        elif self.metric_name == 'collision':
            self.monitor.record_collision_time(elapsed_time)