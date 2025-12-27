# Chess Game

A beautiful and functional chess game built with Python and Pygame, featuring a polished UI with move highlighting, legal move indicators, and smooth gameplay.

## Features

- **Full Chess Rules Implementation**
  - All standard chess moves (pawns, rooks, knights, bishops, queens, kings)
  - Pawn promotion
  - En passant captures
  - Check and checkmate detection
  - Pin and check validation

- **Enhanced Visual Interface**
  - Professional color scheme with cream and brown board
  - Visual move highlighting
  - Selected piece indication
  - Valid move indicators (dots for empty squares, rings for captures)
  - Coordinate labels (a-h files, 1-8 ranks)
  - Stylish turn indicator with move counter
  - Smooth 60 FPS gameplay

- **Game Controls**
  - Click to select and move pieces
  - Undo/Redo functionality
  - Game reset option

## Requirements

- Python 3.x
- Pygame

## Installation

1. Install Python from [python.org](https://www.python.org/)

2. Install Pygame:
```bash
pip install pygame
```

3. Download chess piece images and place them in a folder named `Chess pieces/` with the following naming convention:
   - `wK.png`, `wQ.png`, `wR.png`, `wB.png`, `wN.png`, `wP.png` (white pieces)
   - `bK.png`, `bQ.png`, `bR.png`, `bB.png`, `bN.png`, `bP.png` (black pieces)

## Project Structure

```
chess-game/
│
├── ChessMain.py          # Main game file with GUI
├── Chess/
│   └── ChessEngine.py    # Game logic and move generation
└── Chess pieces/         # Folder containing piece images
    ├── wK.png
    ├── wQ.png
    ├── wR.png
    └── ...
```

## How to Run

```bash
python ChessMain.py
```

## Controls

### Mouse Controls
- **Left Click**: Select a piece and then click a highlighted square to move
- **Click Same Square**: Deselect the current piece

### Keyboard Controls
- **Left Arrow (←)**: Undo the last move
- **Right Arrow (→)**: Redo a previously undone move
- **R**: Reset the game to starting position

## Gameplay

1. White moves first
2. Click on a piece to see all its legal moves highlighted
3. Empty squares show a small dot, capture moves show a ring around the target piece
4. The turn indicator at the top shows whose turn it is and the current move number
5. Use arrow keys to review previous moves or redo moves

## Visual Indicators

- **Yellow highlight**: Currently selected piece
- **Gray overlay with dot**: Valid empty square to move to
- **Gray overlay with ring**: Valid capture move
- **Coordinate labels**: Board coordinates displayed on edges

## Game Logic Features

- **Legal Move Generation**: Only shows and allows legal moves
- **Check Detection**: Automatically detects when king is in check
- **Pin Detection**: Handles pinned pieces correctly
- **En Passant**: Special pawn capture move implemented
- **Pawn Promotion**: Pawns automatically promote to queens when reaching the opposite end


## License

This project is open source and available for educational purposes.