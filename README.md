# 2 Player Arena Game

A fast-paced, 2-player arcade game built with Python and Pygame. Battle against an opponent in a grid-based arena using three different weapons.

## Features

- **2-Player Combat**: Local multiplayer gameplay with dual control schemes
- **Multiple Weapons**: 
  - **SMG**: Fast fire rate, low damage
  - **Shotgun**: Medium fire rate, medium damage
  - **Sniper**: Slow fire rate, high damage
- **Health System**: Each player starts with 70 HP, indicated by a health bar above their character
- **Controller Support**: Gamepad support for Player 1
- **Keyboard & Mouse Control**: Traditional keyboard and mouse controls for Player 2
- **Gridded Arena**: 1200x700 pixel play area with visual grid

## Requirements

- Python 3.x
- Pygame

## Installation

1. Ensure Python is installed on your system
2. Install Pygame:
   ```bash
   pip install pygame
   ```
3. Navigate to the project directory and run the game:
   ```bash
   python arena_game.py
   ```

## How to Play

### Player 1 (Controller)
- **Left Analog Stick**: Move character
- **Right Analog Stick**: Aim weapon
- **R2 Button**: Shoot
- **L1/R1 Buttons**: Switch weapons (cycle through SMG, Shotgun, Sniper)

### Player 2 (Keyboard & Mouse)
- **W**: Move up
- **A**: Move left
- **S**: Move down
- **D**: Move right
- **Mouse Cursor**: Aim weapon
- **Left Mouse Button**: Shoot
- **Keys 1, 2, 3**: Switch to SMG, Shotgun, or Sniper respectively

## Weapon Stats

| Weapon | Damage | Fire Rate | Projectile Speed |
|--------|--------|-----------|------------------|
| SMG | 5 | Fast (120ms) | 12 px/frame |
| Shotgun | 4 | Medium (500ms) | 10 px/frame |
| Sniper | 20 | Slow (750ms) | 18 px/frame |

## Game Mechanics

- Players spawn on opposite sides of the arena
- A white aiming line emanates from each player indicating their shooting direction
- Bullets disappear when they hit an opponent or leave the arena
- Game continues until manually closed
- The first player to reduce their opponent's HP to 0 wins (future implementation)

## Project Structure

```
arcadeGame/
├── README.md
└── arena_game.py
```

## Future Enhancements

- Win condition detection (game ends when a player reaches 0 HP)
- Score tracking and leaderboard
- Power-ups (health restoration, weapon upgrades)
- AI opponent for single-player mode
- Additional weapon types
- Arena hazards or obstacles
- Sound effects and background music
- Particle effects for impacts

## License

This project is open source and available for educational purposes.

## Notes

- A gamepad/controller is optional; Player 2's keyboard and mouse controls work standalone
- The game runs at 60 FPS for smooth gameplay
- The arena has boundaries; projectiles disappear when they leave the play area
- Character collision is not currently implemented
