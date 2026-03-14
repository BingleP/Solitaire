# Command-Line Solitaire

A classic Klondike Solitaire game playable in your command-line interface (PowerShell, CMD, bash, etc.). This Python-based game brings the timeless card game to your terminal with color support, scoring, and configurable draw modes.

## Features

*   **Classic Klondike Solitaire**: Implements the standard rules of Klondike Solitaire.
*   **Text-Based Interface**: Play directly in your terminal.
*   **Color Display**: Utilizes `colorama` for colored card suits (Red for Hearts/Diamonds, White/Black for Spades/Clubs) and distinct color for face-down cards. Color is always on.
*   **Configurable Draw Mode**: Choose between drawing 1 or 3 cards from the stock via a command-line argument.
*   **Undo Functionality**: Made a mistake? Undo your last move.
*   **Scoring System**: Earn points for moving cards to the foundation and flipping tableau cards.
*   **Game Timer**: Tracks the duration of your game.
*   **In-Game Help**: A `help` command provides instructions on commands and pile naming.

## Requirements

*   Python 3.x
*   `colorama` library

## Installation

1.  Ensure you have Python 3 installed on your system.
2.  Clone this repository or download `solitaire.py`.
3.  Install the `colorama` library if you haven't already:
    ```bash
    pip install colorama
    ```

## How to Run

Navigate to the directory where `solitaire.py` is located and run the game using Python:

```bash
python solitaire.py [options]
```

### Command-Line Arguments

*   `--draw-mode <1|3>`: Sets the number of cards drawn from the stock at a time.
    *   `1`: Draw one card (default).
    *   `3`: Draw three cards.
    *   Example: `python solitaire.py --draw-mode 3`

*   `--help`: Shows help for command-line arguments and exits.

## Gameplay

The goal of Klondike Solitaire is to move all 52 cards to the four Foundation piles, building each suit up from Ace to King.

### Game Board

*   **Stock (S)**: Pile of face-down cards. Click `draw` to move cards to Waste.
*   **Waste (W)**: Cards drawn from Stock. The top card is playable.
*   **Foundations (F1-F4)**: Build piles from Ace to King for each suit.
*   **Tableau (T1-T7)**: Seven piles of cards. Build down in alternating colors (e.g., a Red 9 on a Black 10). The top card of each pile is face-up. Empty tableau spots can only be filled with a King.

### In-Game Commands

Enter commands at the prompt. Commands are case-insensitive.

*   `draw` (or `d`): Draws card(s) from the Stock to the Waste pile according to the current draw mode. If Stock is empty, it attempts to recycle the Waste pile.
*   `move <source> <destination>` (or `m <src> <dest>`): Moves a card.
    *   **Sources**:
        *   `W`: Top card from the Waste pile.
        *   `T<n>`: Bottom-most face-up card from Tableau pile `n` (e.g., `T1`, `T7`).
    *   **Destinations**:
        *   `F<n>`: Foundation pile `n` (e.g., `F1`, `F4`).
        *   `T<n>`: Tableau pile `n`.
    *   **Examples**:
        *   `move W T1` (Move card from Waste to Tableau 1)
        *   `move T2 F1` (Move card from Tableau 2 to Foundation 1)
        *   `move T3 T5` (Move card from Tableau 3 to Tableau 5)
*   `undo` (or `u`): Reverts the last successful move or draw.
*   `help` (or `h`): Displays the in-game help message, including command list, pile names, and scoring rules.
*   `quit` (or `q`): Exits the game.

Enjoy playing Solitaire!
