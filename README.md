# Super Mario Bros - Gesture Control Edition

A modern Mario-style platformer game with gesture controls using MediaPipe and computer vision.

## 🎮 How to Play

### Starting the Game
Run the launcher to access the professional menu system:
```bash
python launcher.py
```

### Menu Navigation
- **Arrow Keys / WASD**: Navigate menu options
- **SPACE / ENTER**: Select option
- **ESC**: Go back (in submenus)

### Game Controls
- **Right Hand Extended**: Move Mario right
- **Left Hand Extended**: Move Mario left  
- **Both Hands Raised**: Make Mario jump
- **Keyboard Fallback**: Arrow keys, WASD, or SPACE for jump

## 🎯 Menu Features

### Main Menu
- **PLAY**: Start the game
- **SETTINGS**: Adjust game preferences
- **CREDITS**: View game information
- **QUIT**: Exit the application

### Settings
- **MUSIC**: Toggle background music on/off
- **SFX**: Toggle sound effects on/off  
- **DIFFICULTY**: Choose between Easy, Normal, and Hard

### Visual Features
- Animated particle effects
- Scrolling background
- Bouncing title animation
- Glowing menu selections
- Mario character animation

## 📁 File Structure

- `launcher.py` - Main entry point with menu system
- `menu.py` - Professional menu interface
- `18.py` - Your original game (unchanged)
- `game_wrapper.py` - Integration helper
- Image files: `mario.png`, `mario2.png`, `obstacle.png`, `im1.png`
- Audio: `background_music.mp3`

## 🚀 Quick Start

1. Make sure you have a webcam connected
2. Install required packages: `pygame`, `opencv-python`, `mediapipe`
3. Run: `python launcher.py`
4. Use the menu to start playing!

## 🎨 Menu Design

The menu features a professional Mario-themed design with:
- Classic Mario red and blue color scheme
- Smooth animations and transitions
- Particle effects for atmosphere
- Responsive selection highlighting
- Integrated game settings

Enjoy your enhanced Mario gaming experience! 🍄
