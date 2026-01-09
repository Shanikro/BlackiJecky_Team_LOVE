import os
import sys

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BlackJeckLogic import Card, RANK_NAMES, SUIT_SYMBOLS, SUITS, BlackjackGame

class GameUI:

    def __init__(self):
        self.player_cards = []
        self.dealer_cards = []

    def card_ui_formatter(self, card: Card):
        """Format a single card into lines."""
        # Convert rank to display string
        rank_str = RANK_NAMES.get(card.rank, str(card.rank))
        
        # Convert suit (int 0-3) to symbol
        # SUITS = ['H', 'D', 'C', 'S'] -> suit index maps to suit letter
        suit_letter = SUITS[card.suit] if isinstance(card.suit, int) and 0 <= card.suit < 4 else card.suit
        suit_symbol = SUIT_SYMBOLS.get(suit_letter, suit_letter)
        
        return [
            "┌─────────┐",
            f"│ {rank_str:<7} │",
            "│         │",
            f"│    {suit_symbol}    │",
            "│         │",
            f"│ {rank_str:>7} │",
            "└─────────┘"
        ]

    def print_cards_side_by_side(self, cards: list):
        """Print multiple cards side by side."""
        if not cards:
            return
        
        # Convert each card to lines
        card_lines = [self.card_ui_formatter(card) for card in cards]
        
        # Print line by line, combining all cards horizontally
        num_lines = len(card_lines[0])
        for line_idx in range(num_lines):
            line_parts = [card_lines[i][line_idx] for i in range(len(cards))]
            print("  ".join(line_parts))  # Join with 2 spaces between cards

    def add_player_card(self, card: Card, player_sum: int, dealer_sum: int, round_num: int):
        self.player_cards.append(card)
        print("\n" + "─"*50)
        print(f"  🎴 Round {round_num} - Your Turn 🎴")
        print("─"*50)
        print("\n  👤 YOUR CARDS:")
        self.print_cards_side_by_side(self.player_cards)
        print(f"\n  📊 Your sum: {player_sum}")
        print(f"  🎰 Dealer sum: {dealer_sum}")
        print("─"*50 + "\n")

    def add_dealer_card(self, card: Card, dealer_sum: int, player_sum: int, round_num: int):
        self.dealer_cards.append(card)
        print("\n" + "─"*50)
        print(f"  🎴 Round {round_num} - Dealer's Turn 🎴")
        print("─"*50)
        print("\n  🎰 DEALER'S CARDS:")
        self.print_cards_side_by_side(self.dealer_cards)
        print(f"\n  🎰 Dealer sum: {dealer_sum}")
        print(f"  👤 Your sum: {player_sum}")
        print("─"*50 + "\n")
    
    def print_result(self, round_result: int, player_sum: int, dealer_sum: int, round_num: int):
        
        # Determine result message and emoji
        if round_result == BlackjackGame.ROUND_RESULT.PLAYER_WINS:
            result_msg = "🎉 YOU WIN! 🎉"
            result_emoji = "🎊"
        elif round_result == BlackjackGame.ROUND_RESULT.DEALER_WINS:
            result_msg = "😞 You Lose 😞"
            result_emoji = "💔"
        elif round_result == BlackjackGame.ROUND_RESULT.TIE:
            result_msg = "🤝 It's a TIE! 🤝"
            result_emoji = "⚖️"
        else:
            result_msg = "❓ Unknown Result ❓"
            result_emoji = "❓"
        
        # Print beautiful result display
        print("\n" + "="*60)
        print(f"  {'ROUND ' + str(round_num) + ' RESULT':^54}")
        print("="*60)
        print()
        
        # Print player cards and sum
        print("  👤 YOUR HAND:")
        self.print_cards_side_by_side(self.player_cards)
        print(f"  📊 Your sum: {player_sum}")
        print()
        
        # Print dealer cards and sum
        print("  🎰 DEALER'S HAND:")
        self.print_cards_side_by_side(self.dealer_cards)
        print(f"  📊 Dealer sum: {dealer_sum}")
        print()
        
        # Print final result with style
        print("  " + "─"*56)
        print(f"  {result_msg:^54}")
        print(f"  {result_emoji:^54}")
        print("  " + "─"*56)
        print("="*60)
        print()
