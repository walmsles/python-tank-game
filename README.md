# Tank Game

A Python tank game where players control a tank across a maze-like map, battling against AI-controlled enemy tanks and interacting with destructible elements.
## **Built entirely with [Kiro](https://kiro.dev)**
*An AI-powered development platform that generated all the code, tests, and documentation for this project.*
## Features

- Maze-like maps with destructible elements
- Player-controlled tank with intuitive controls
- AI-controlled enemy tanks with scaling difficulty
- Multiple levels with increasing challenges
- Scoring system and game progression

## Requirements

- Python 3.8 or higher
- Pygame 2.1.0 or higher
- NumPy 1.20.0 or higher

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tank-game.git
cd tank-game

# Install dependencies
pip install -e .
```

## Running the Game

```bash
uv run python main.py
```

## Controls

- Arrow keys or WASD: Move the tank
- Space: Fire projectile
- Escape: Pause/Exit

## Development

This game is structured with a component-based architecture:
- Game Engine: Central component managing the game loop
- Game Objects: Tanks, projectiles, walls, etc.
- Renderers: Visual representation of game objects
- Input Handler: Processing user input
- Level Manager: Managing level progression and difficulty
- Collision Detection: Handling object interactions
