import random
import time
import argparse
import copy
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# --- Constants ---
SUITS = {'H': 'Hearts', 'D': 'Diamonds', 'S': 'Spades', 'C': 'Clubs'}
VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
VALUE_NAMES = {v: k for k, v in VALUES.items()}
SUIT_SYMBOLS = {'Hearts': '♥', 'Diamonds': '♦', 'Spades': '♠', 'Clubs': '♣'} # Optional: Unicode symbols
# Simpler ASCII symbols for broader compatibility:
SUIT_ASCII_SYMBOLS = {'H': 'H', 'D': 'D', 'S': 'S', 'C': 'C'}


CARD_COLORS = {'H': Fore.RED, 'D': Fore.RED, 'S': Fore.WHITE, 'C': Fore.WHITE} # White for black suits for better visibility on dark terminals

# --- Card Class ---
class Card:
    def __init__(self, suit, value_char):
        self.suit = suit # H, D, S, C
        self.value_char = value_char # A, 2-10, J, Q, K
        self.value = VALUES[value_char]
        self.is_face_up = False
        self.color = 'Red' if suit in ['H', 'D'] else 'Black'

    def __str__(self):
        if not self.is_face_up:
            # Use a distinct color for face-down cards, e.g., BLUE
            return Fore.BLUE + 'XX' + Style.RESET_ALL
        return CARD_COLORS[self.suit] + f"{self.value_char}{SUIT_ASCII_SYMBOLS[self.suit]}" + Style.RESET_ALL

    def __repr__(self):
        return f"Card('{self.suit}', '{self.value_char}', FaceUp:{self.is_face_up})"

# --- Game Class ---
class Game:
    def __init__(self, draw_mode=1):
        self.draw_mode = draw_mode
        self.deck = self._create_deck()
        self.stock = []
        self.waste = []
        self.tableau: list[list[Card]] = [[] for _ in range(7)]
        self.foundation: list[list[Card]] = [[] for _ in range(4)]
        self.history = []
        self.score = 0
        self.start_time = time.time()
        self._setup_board()
        self.save_state() # Save initial state for undo

    def _create_deck(self):
        deck = [Card(s, v_char) for s in SUITS.keys() for v_char in VALUES.keys()]
        random.shuffle(deck)
        return deck

    def _setup_board(self):
        # Deal to tableau
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.pop()
                if j == i: # Top card of the pile
                    card.is_face_up = True
                self.tableau[i].append(card)
        # Remaining cards to stock
        self.stock = self.deck
        self.deck = [] # Deck is now empty, cards are in stock or tableau

    def display_board(self):
        print("\n" + "="*40)
        # Score and Time
        elapsed_time = int(time.time() - self.start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        print(f"Score: {self.score}  Time: {minutes:02d}:{seconds:02d}  Draw Mode: {self.draw_mode}")
        print("-"*40)

        # Stock and Waste
        stock_display = Fore.GREEN + "[XXX]" + Style.RESET_ALL if self.stock else Fore.RED + "[---]" + Style.RESET_ALL
        
        waste_str_parts = []
        if not self.waste:
            waste_str_parts.append(Fore.RED + "[---]" + Style.RESET_ALL)
        else:
            # Display up to draw_mode cards from waste, or fewer if less are available
            # The playable card is self.waste[-1]
            # Show a few cards from the end of the waste pile to hint at what's there
            display_count = min(len(self.waste), self.draw_mode if self.draw_mode == 3 else 1)
            for card in self.waste[-display_count:]:
                 waste_str_parts.append(str(card))

        print(f"Stock (S): {stock_display}   Waste (W): {' '.join(waste_str_parts)}")

        # Foundations
        f_display = []
        for i, pile in enumerate(self.foundation):
            top_card = str(pile[-1]) if pile else "[ ]"
            f_display.append(f"F{i+1}: {top_card}")
        print("Foundations: " + "  ".join(f_display))
        print("-"*40)

        # Tableau
        print("Tableau:")
        CARD_DISPLAY_WIDTH = 4  # Define standard width for card display cell
        max_len = max(len(p) for p in self.tableau) if self.tableau and any(self.tableau) else 0
        
        for i in range(max_len): # For each row in the tableau
            row_str_parts = []
            for j in range(7): # For each tableau pile (column)
                if i < len(self.tableau[j]):
                    card = self.tableau[j][i]
                    card_str_val = str(card) # String representation of card, includes ANSI

                    # Calculate visible length (excluding ANSI codes)
                    visible_len = 0
                    if card.is_face_up:
                        visible_len = len(card.value_char) + len(SUIT_ASCII_SYMBOLS[card.suit])
                    else: # Face-down 'XX'
                        visible_len = 2
                    
                    num_spaces = CARD_DISPLAY_WIDTH - visible_len
                    padding = " " * num_spaces if num_spaces > 0 else ""
                    row_str_parts.append(f"{card_str_val}{padding}")
                else:
                    # Empty slot in this row for this pile
                    row_str_parts.append(" " * CARD_DISPLAY_WIDTH)
            print("  ".join(row_str_parts)) # Join columns with two spaces
        
        # Tableau pile numbers (T1, T2, ...)
        pile_numbers_str_parts = []
        for j in range(7):
            label = f"T{j+1}"
            # Visible length of "T1" is 2, "T2" is 2, etc.
            visible_label_len = len(label) 
            num_spaces = CARD_DISPLAY_WIDTH - visible_label_len
            padding = " " * num_spaces if num_spaces > 0 else ""
            pile_numbers_str_parts.append(f"{label}{padding}")
        print("  ".join(pile_numbers_str_parts)) # Join labels with two spaces
        print("="*40 + "\n")

    def save_state(self):
        # Deep copy is essential for lists of objects
        state = {
            'stock': [copy.copy(card) for card in self.stock], # Cards themselves are simple, shallow copy is fine for Card objects
            'waste': [copy.copy(card) for card in self.waste],
            'tableau': [[copy.copy(card) for card in pile] for pile in self.tableau],
            'foundation': [[copy.copy(card) for card in pile] for pile in self.foundation],
            'score': self.score,
            # time is not undone
        }
        self.history.append(state)

    def undo_move(self):
        if len(self.history) > 1: # Keep at least the initial state
            self.history.pop() # Remove current state
            last_state = self.history[-1] # Get previous state
            self.stock = last_state['stock']
            self.waste = last_state['waste']
            self.tableau = last_state['tableau']
            self.foundation = last_state['foundation']
            self.score = last_state['score']
            print(Fore.YELLOW + "Last move undone.")
            return True
        print(Fore.RED + "Cannot undo further.")
        return False

    def draw_from_stock(self):
        if not self.stock:
            if not self.waste:
                print(Fore.RED + "Stock and Waste are empty. Cannot draw.")
                return False
            # Recycle waste to stock
            self.stock = self.waste[::-1] # Reverse waste to become stock
            self.waste = []
            print(Fore.YELLOW + "Waste pile recycled into Stock.")
            # No penalty for now for simplicity, could add score -= 100 here
            return self.draw_from_stock() # Try drawing again

        num_to_draw = self.draw_mode
        drawn_cards = []
        for _ in range(num_to_draw):
            if self.stock:
                card = self.stock.pop()
                card.is_face_up = True
                self.waste.append(card)
                drawn_cards.append(card)
            else:
                break
        if drawn_cards:
            print(f"Drew {len(drawn_cards)} card(s) to Waste.")
            return True
        return False
        
    def _get_pile_from_str(self, pile_str):
        pile_str = pile_str.upper()
        if not pile_str: return None, -1
        
        type_char = pile_str[0]
        idx = -1

        if type_char == 'W':
            return self.waste, -1 # Index not really used for waste source
        if type_char == 'T':
            if len(pile_str) > 1 and pile_str[1:].isdigit():
                idx = int(pile_str[1:]) - 1
                if 0 <= idx < 7:
                    return self.tableau[idx], idx
        if type_char == 'F':
            if len(pile_str) > 1 and pile_str[1:].isdigit():
                idx = int(pile_str[1:]) - 1
                if 0 <= idx < 4:
                    return self.foundation[idx], idx
        return None, -1

    def _can_place_on_tableau(self, card_to_move: Card, dest_pile_top_card: Card | None):
        if not dest_pile_top_card: # Empty tableau pile
            return card_to_move.value == VALUES['K'] # Only Kings on empty
        return card_to_move.color != dest_pile_top_card.color and \
               card_to_move.value == dest_pile_top_card.value - 1

    def _can_place_on_foundation(self, card_to_move: Card, dest_pile_top_card: Card | None, foundation_idx: int):
        # Determine foundation suit based on first card or expected Ace
        foundation_suit = None
        if dest_pile_top_card:
            foundation_suit = dest_pile_top_card.suit
        elif not self.foundation[foundation_idx]: # Empty foundation
            return card_to_move.value == VALUES['A'] # Must be an Ace

        if foundation_suit and card_to_move.suit != foundation_suit:
            return False # Must match suit
        
        if not dest_pile_top_card: # Should be caught by Ace check, but for safety
             return card_to_move.value == VALUES['A']
        
        return card_to_move.suit == dest_pile_top_card.suit and \
               card_to_move.value == dest_pile_top_card.value + 1


    def _flip_top_tableau_card(self, pile_idx):
        if self.tableau[pile_idx] and not self.tableau[pile_idx][-1].is_face_up:
            self.tableau[pile_idx][-1].is_face_up = True
            self.score += 5
            print(Fore.GREEN + f"Flipped card in Tableau T{pile_idx+1}. (+5 score)")


    def move_card(self, src_str, dest_str):
        src_pile_obj, src_idx = self._get_pile_from_str(src_str)
        dest_pile_obj, dest_idx = self._get_pile_from_str(dest_str)

        if src_pile_obj is None:
            print(Fore.RED + f"Invalid source pile: {src_str}")
            return False
        if dest_pile_obj is None:
            print(Fore.RED + f"Invalid destination pile: {dest_str}")
            return False
        if src_pile_obj is dest_pile_obj and src_idx == dest_idx : # e.g. T1 to T1
            print(Fore.RED + "Source and destination piles cannot be the same.")
            return False


        card_to_move = None
        original_pile_list_for_pop = None # This is for tableau to ensure we pop from the correct list

        # --- Source Logic ---
        if src_str.upper().startswith('W'): # Moving from Waste
            if not self.waste:
                print(Fore.RED + "Waste pile is empty.")
                return False
            card_to_move = self.waste[-1]
            original_pile_list_for_pop = self.waste
        elif src_str.upper().startswith('T'): # Moving from Tableau
            if not self.tableau[src_idx] or not self.tableau[src_idx][-1].is_face_up:
                print(Fore.RED + f"Tableau pile T{src_idx+1} is empty or top card is face down.")
                return False
            card_to_move = self.tableau[src_idx][-1] # Only single bottom-most face-up card for now
            original_pile_list_for_pop = self.tableau[src_idx]
        else:
            print(Fore.RED + "Cannot move from Foundation piles in this version.")
            return False # Disallow F -> T or F -> F for simplicity

        if not card_to_move: # Should not happen if logic above is correct
            print(Fore.RED + "No card selected to move.")
            return False

        # --- Destination Logic & Validation ---
        moved = False
        if dest_str.upper().startswith('F'): # Moving to Foundation
            dest_top_card = self.foundation[dest_idx][-1] if self.foundation[dest_idx] else None
            if self._can_place_on_foundation(card_to_move, dest_top_card, dest_idx):
                moved_card = original_pile_list_for_pop.pop()
                self.foundation[dest_idx].append(moved_card)
                self.score += 10
                print(Fore.GREEN + f"Moved {moved_card} to Foundation F{dest_idx+1}. (+10 score)")
                moved = True
            else:
                print(Fore.RED + f"Cannot move {card_to_move} to Foundation F{dest_idx+1}. Invalid move.")
        
        elif dest_str.upper().startswith('T'): # Moving to Tableau
            dest_top_card = self.tableau[dest_idx][-1] if self.tableau[dest_idx] else None
            if self._can_place_on_tableau(card_to_move, dest_top_card):
                moved_card = original_pile_list_for_pop.pop()
                self.tableau[dest_idx].append(moved_card)
                if src_str.upper().startswith('W'): # Points for waste to tableau
                    self.score += 5
                    print(Fore.GREEN + f"Moved {moved_card} from Waste to Tableau T{dest_idx+1}. (+5 score)")
                else: # Tableau to Tableau move
                     print(Fore.GREEN + f"Moved {moved_card} from T{src_idx+1} to Tableau T{dest_idx+1}.")
                moved = True
            else:
                print(Fore.RED + f"Cannot move {card_to_move} to Tableau T{dest_idx+1}. Invalid move.")

        if moved:
            if src_str.upper().startswith('T'): # If card moved from Tableau, try to flip new top
                self._flip_top_tableau_card(src_idx)
            return True
        return False

    def check_win_condition(self):
        return sum(len(p) for p in self.foundation) == 52

    def display_help(self):
        draw_mode_status = f"Set by --draw-mode {self.draw_mode} at launch."
        help_text = f"""
{Style.BRIGHT}{Fore.CYAN}Solitaire Game Help{Style.RESET_ALL}

{Fore.YELLOW}Goal:{Style.RESET_ALL} Move all cards to the Foundation piles (F1-F4),
      building each suit up from Ace to King.

{Fore.YELLOW}Command-Line Options:{Style.RESET_ALL}
  {Fore.GREEN}--draw-mode <1|3>{Style.RESET_ALL} : Set card draw mode (1 or 3). Current: {draw_mode_status}

{Fore.YELLOW}In-Game Commands:{Style.RESET_ALL}
  {Fore.GREEN}draw{Style.RESET_ALL} (or {Fore.GREEN}d{Style.RESET_ALL})        : Draw card(s) from Stock to Waste.
  {Fore.GREEN}move <src> <dest>{Style.RESET_ALL} (or {Fore.GREEN}m <src> <dest>{Style.RESET_ALL}): Move a card.
    {Fore.CYAN}Piles:{Style.RESET_ALL}
      {Fore.MAGENTA}S{Style.RESET_ALL}  : Stock (not a direct move source)
      {Fore.MAGENTA}W{Style.RESET_ALL}  : Waste (top card is moved)
      {Fore.MAGENTA}T<n>{Style.RESET_ALL}: Tableau pile (e.g., {Fore.MAGENTA}T1{Style.RESET_ALL}, {Fore.MAGENTA}T2{Style.RESET_ALL}, ..., {Fore.MAGENTA}T7{Style.RESET_ALL}). Moves bottom-most face-up card.
      {Fore.MAGENTA}F<n>{Style.RESET_ALL}: Foundation pile (e.g., {Fore.MAGENTA}F1{Style.RESET_ALL}, {Fore.MAGENTA}F2{Style.RESET_ALL}, ..., {Fore.MAGENTA}F4{Style.RESET_ALL}).
    {Fore.CYAN}Examples:{Style.RESET_ALL}
      {Fore.GREEN}move W T1{Style.RESET_ALL}  - Move card from Waste to Tableau 1.
      {Fore.GREEN}move T2 F1{Style.RESET_ALL}  - Move card from Tableau 2 to Foundation 1.
      {Fore.GREEN}move T3 T5{Style.RESET_ALL}  - Move card from Tableau 3 to Tableau 5.
  {Fore.GREEN}undo{Style.RESET_ALL} (or {Fore.GREEN}u{Style.RESET_ALL})        : Revert the last move.
  {Fore.GREEN}help{Style.RESET_ALL} (or {Fore.GREEN}h{Style.RESET_ALL})        : Display this help message.
  {Fore.GREEN}quit{Style.RESET_ALL} (or {Fore.GREEN}q{Style.RESET_ALL})        : Exit the game.

{Fore.YELLOW}Scoring:{Style.RESET_ALL}
  +10 points: Card to Foundation.
  +5  points: Card from Waste to Tableau.
  +5  points: Flipping a Tableau card face-up.

{Fore.YELLOW}Display:{Style.RESET_ALL}
  Cards are shown as ValueSuit (e.g., {CARD_COLORS['H']}AH{Style.RESET_ALL}, {CARD_COLORS['S']}KS{Style.RESET_ALL}).
  Face-down cards are {Fore.BLUE}XX{Style.RESET_ALL}. Empty foundation slots are [ ].
  Stock: {Fore.GREEN}[XXX]{Style.RESET_ALL} (cards available), {Fore.RED}[---]{Style.RESET_ALL} (empty).
  Waste: Shows playable card(s). {Fore.RED}[---]{Style.RESET_ALL} if empty.
        (Color display is always on for cards)
"""
        print(help_text)


    def game_loop(self):
        print(Fore.CYAN + Style.BRIGHT + "Welcome to Solitaire!")
        self.display_help() # Show help on start for first time users

        while True:
            self.display_board()
            if self.check_win_condition():
                print(Fore.GREEN + Style.BRIGHT + f"Congratulations! You've won with a score of {self.score}!")
                break

            try:
                user_input = input(Fore.CYAN + "Enter command (or 'help'): " + Style.RESET_ALL).strip().lower().split()
            except EOFError: # Handle Ctrl+D or premature end of input stream
                print(Fore.YELLOW + "\nExiting game.")
                break
            except KeyboardInterrupt: # Handle Ctrl+C
                print(Fore.YELLOW + "\nExiting game.")
                break


            if not user_input:
                continue

            command = user_input[0]
            args = user_input[1:]

            action_taken = False
            if command in ["q", "quit"]:
                print(Fore.YELLOW + "Exiting game.")
                break
            elif command in ["h", "help"]:
                self.display_help()
            elif command in ["d", "draw"]:
                if self.draw_from_stock():
                    action_taken = True
            elif command in ["u", "undo"]:
                self.undo_move() # Undo itself is an action, no need to save state after it
                                # Display will refresh board, no explicit action_taken = True
            elif command in ["m", "move"]:
                if len(args) == 2:
                    if self.move_card(args[0], args[1]):
                        action_taken = True
                else:
                    print(Fore.RED + "Invalid move command. Usage: move <source> <destination>")
            else:
                print(Fore.RED + f"Unknown command: {command}. Type 'help' for options.")

            if action_taken:
                self.save_state() # Save state after a successful action (draw, move)

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play Solitaire in the command line.")
    parser.add_argument(
        '--draw-mode', 
        type=int, 
        choices=[1, 3], 
        default=1, 
        help='Number of cards to draw from stock (1 or 3). Default is 1.'
    )
    args = parser.parse_args()

    game = Game(draw_mode=args.draw_mode)
    game.game_loop()
