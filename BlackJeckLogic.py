"""
Game Logic Module
Handles deck management, card dealing, and game rules for Blackjack.
"""

from enum import IntEnum
import random
from typing import List, Tuple, Optional

# Card suits and symbols
SUITS = ['H', 'D', 'C', 'S']
SUIT_SYMBOLS = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}

# Card ranks: 1=Ace, 2-10, 11=Jack, 12=Queen, 13=King
RANK_NAMES = {
    1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
    8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K'
}


class Card:
    
    def __init__(self, rank: int, suit: int):
        self.rank = rank
        self.suit = suit
    
    def get_value(self) -> int:
        if self.rank == 1:  # Ace
            return 11
        elif 2 <= self.rank <= 10:  # Number cards
            return self.rank
        else:  # Face cards (Jack, Queen, King)
            return 10
    
class Deck:
    def __init__(self):
        self.cards: List[Card] = [] # list of cards
        self.reset()
    
    def reset(self):
        # reset the deck
        self.cards = []
        for suit_idx in range(4):  # 4 suits
            for rank in range(1, 14):  # ranks 1-13
                self.cards.append(Card(rank, suit_idx))
        self.shuffle()
    
    def shuffle(self):
        # shuffle the deck
        random.shuffle(self.cards)
    
    def deal_card(self) -> Optional[Card]:
        # deal a card from the deck
        if len(self.cards) == 0:
            self.reset()
        return self.cards.pop() # return the top card


class Hand:
    def __init__(self):
        self.cards = [] # list of cards in the hand
        self.total_value = 0 # total value of the hand
        
    def add_card(self, card: Card):
        self.cards.append(card) # add a card to the hand
        self.total_value += card.get_value() # add the value of the card to the hand

    def is_bust(self):
        return self.total_value > 21 # return True if the hand is bust
    
    def to_string(self) -> str:
        return "\n".join([card.to_string() for card in self.cards]) # return the string representation of the hand
    
class BlackjackGame:
    # Round Result
    ROUND_RESULT = IntEnum('ROUND_RESULT', ['NOT_OVER', 'TIE', 'DEALER_WINS', 'PLAYER_WINS'])

    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.result = self.ROUND_RESULT.NOT_OVER # result of the round
    
    def player_hit(self) -> Optional[Card]:
        card = self.deck.deal_card()
        self.player_hand.add_card(card)

        if self.player_hand.is_bust():
            self.result = self.ROUND_RESULT.DEALER_WINS

        return card

    def dealer_hit(self) -> Optional[Card]:
        card = self.deck.deal_card()
        #degud print
        print("add card to dealer:", card.rank)
        self.dealer_hand.add_card(card)
        #degud print
        print("dealer hand value:", self.dealer_hand.total_value)
        
        if self.dealer_hand.is_bust():
            self.result = self.ROUND_RESULT.PLAYER_WINS

        return card
    
    def dealer_play(self) -> List[Card]:
        # Player choose 'Stand' -> Dealer plays until total_value >= 17 or busts

        # Dealer hits until total_value >= 17
        while self.dealer_hand.total_value < 17:
            card = self.deck.deal_card()
            self.dealer_hand.add_card(card)
        
        self.decide_winner()
        

    def decide_winner(self):
        player_bust = self.player_hand.is_bust()
        dealer_bust = self.dealer_hand.is_bust()
        
        # Handle bust cases first
        if player_bust:
            self.result = self.ROUND_RESULT.DEALER_WINS # player bust before dealer
        elif dealer_bust:
            self.result = self.ROUND_RESULT.PLAYER_WINS
        else:
            # Compare hand values using sign of difference
            diff = self.player_hand.total_value - self.dealer_hand.total_value
            self.result = (
                self.ROUND_RESULT.PLAYER_WINS if diff > 0 else
                self.ROUND_RESULT.DEALER_WINS if diff < 0 else
                self.ROUND_RESULT.TIE
            )