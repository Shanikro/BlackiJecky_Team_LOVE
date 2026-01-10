from typing import List
from BlackJeckLogic import Card, RANK_NAMES, SUITS, BlackjackGame


class GameUI:

    SUIT_SYMBOLS = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}

    @staticmethod
    def _format_card(card: Card) -> List[str]:
        rank_str = RANK_NAMES.get(card.rank, str(card.rank))
        suit_letter = SUITS[card.suit] if isinstance(card.suit, int) and 0 <= card.suit < 4 else card.suit
        suit_symbol = GameUI.SUIT_SYMBOLS.get(suit_letter, suit_letter)
        
        return [
            "┌─────────┐",
            f"│ {rank_str:<7} │",
            "│         │",
            f"│    {suit_symbol}    │",
            "│         │",
            f"│ {rank_str:>7} │",
            "└─────────┘"
        ]

    @staticmethod
    def _print_cards_row(cards: List[Card]):
        """Print multiple cards side by side."""
        if not cards:
            return
        
        card_lines = [GameUI._format_card(card) for card in cards]
        num_lines = len(card_lines[0])
        
        for line_idx in range(num_lines):
            line_parts = [card_lines[i][line_idx] for i in range(len(cards))]
            print("  ".join(line_parts))

    @staticmethod
    def print_game_state(round_num: int, player_cards: List[Card], dealer_cards: List[Card], 
                         player_sum: int, dealer_sum: int):

        # Only print if player has at least 2 cards and dealer has at least 1 card
        if len(player_cards) < 2 or len(dealer_cards) < 1:
            return
        
        print("\n" + "─"*50)
        print(f"  🎴 Round {round_num} 🎴")
        print("─"*50)
        
        print("\n  👤 YOUR CARDS:")
        GameUI._print_cards_row(player_cards)
        print(f"  📊 Your sum: {player_sum}")
        
        print("\n  🎰 DEALER'S CARDS:")
        GameUI._print_cards_row(dealer_cards)
        print(f"  🎰 Dealer sum: {dealer_sum}")
        
        print("─"*50 + "\n")
    
    @staticmethod
    def print_result(round_result: int, round_num: int, player_sum: int, dealer_sum: int):

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
        
        print("\n" + "="*50)
        print(f"  {'ROUND ' + str(round_num) + ' RESULT':^44}")
        print("="*50)
        print(f"  👤 Your sum: {player_sum}  |  🎰 Dealer sum: {dealer_sum}")
        print("─"*50)
        print(f"  {result_msg:^44}")
        print(f"  {result_emoji:^44}")
        print("="*50 + "\n")
    
    @staticmethod
    def print_statistics(player_name: str, wins: int, ties: int, losses: int):

        total_rounds = wins + ties + losses
        win_rate = (wins / total_rounds * 100) if total_rounds > 0 else 0
        
        print("\n" + "🎰" + "═"*56 + "🎰")
        print("           📊 GAME STATISTICS 📊")
        print("═"*60)
        print(f"  👤 Player: {player_name}")
        print(f"  🎮 Total Rounds: {total_rounds}")
        print("─"*60)
        print(f"  🏆 Wins:   {wins}")
        print(f"  🤝 Ties:   {ties}")
        print(f"  💔 Losses: {losses}")
        print(f"  📈 Win Rate: {win_rate:.1f}%")
        print("─"*60)
        if win_rate >= 50:
            print("  🎉 Great job! You beat the house! 🎉")
        elif win_rate > 0 or ties > 0:
            print("  💪 Better luck next time! 💪")
        else:
            print("  😢 The house always wins... 😢")
        print("🎰" + "═"*56 + "🎰\n")
