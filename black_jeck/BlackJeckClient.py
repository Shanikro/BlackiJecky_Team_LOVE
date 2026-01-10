import socket
import sys
import os

# Add parent directory to path for package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from black_jeck.UDPBroadcastOffer import UDPBroadcastOffer
from network.TCPConnection import recv_exact
from black_jeck.BlackJeckPacketProtocol import decode_server_payload, encode_request,\
     encode_client_payload, SERVER_PAYLOAD_SIZE
from black_jeck.BlackJeckLogic import BlackjackGame, Card
from black_jeck.GameUI import GameUI

# Result codes #
RESULT_NOT_OVER = BlackjackGame.ROUND_RESULT.NOT_OVER
RESULT_WIN = BlackjackGame.ROUND_RESULT.PLAYER_WINS
RESULT_LOSS = BlackjackGame.ROUND_RESULT.DEALER_WINS
RESULT_TIE = BlackjackGame.ROUND_RESULT.TIE


def main():
    print("BlackJeck Client started")
    
    while True:
        sock = None
        try:
            # Listen for server offers
            print("Listening for server offers...")
            broadcaster = UDPBroadcastOffer()
            server_ip, server_tcp_port, server_name = broadcaster.listen()
            print(f"Server offer received from {server_ip}:{server_tcp_port} - {server_name}")

            # Get player name and number of rounds
            player_name = input("Enter your name: ")
            num_rounds = int(input("How many rounds would you like to play? "))   
            if num_rounds < 1:
                print("Number of rounds must be at least 1")
                continue
            
            # Create TCP socket and connect to server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server_ip, server_tcp_port))
            sock.sendall(encode_request(num_rounds, player_name)) # send request to server

            wins, ties, losses = play_game(sock, num_rounds) # play game
            GameUI.print_statistics(player_name, wins, ties, losses) # print statistics

        except KeyboardInterrupt: # Ctrl+C
            print("\nShutting down client...")
            break
        finally:
            if sock: # close socket
                sock.close()


def play_game(sock: socket.socket, num_rounds: int):
    wins = 0
    ties = 0
    losses = 0

    for round_num in range(1, num_rounds + 1):
        # Track round state
        player_cards = []
        dealer_cards = []
        player_sum = 0
        dealer_sum = 0

        # Receive first two player cards
        for _ in range(2):
            data = recv_exact(sock, SERVER_PAYLOAD_SIZE)
            round_result, rank, suit_idx = decode_server_payload(data)
            card = Card(rank, suit_idx)
            player_cards.append(card)
            player_sum += card.get_value()

        # Check if player busted (can be 2 Aces)
        if round_result == RESULT_LOSS:
            GameUI.print_result(round_result, round_num, player_sum, dealer_sum)
            losses += 1
            continue

        # Receive dealer first card
        data = recv_exact(sock, SERVER_PAYLOAD_SIZE)
        round_result, rank, suit_idx = decode_server_payload(data)
        card = Card(rank, suit_idx)
        dealer_cards.append(card)
        dealer_sum += card.get_value()
        
        # Display initial state
        GameUI.print_game_state(round_num, player_cards, dealer_cards, player_sum, dealer_sum)

        # Player's turn
        while True:
            decision = None
            while decision not in ("HITTT", "STAND", "HITT", "HIT"):
                decision = input("Please type Hit or Stand: ").strip().upper()

            if decision in ("HITTT", "HITT", "HIT"):
                sock.sendall(encode_client_payload("Hittt")) # send 'hit' to server
                data = recv_exact(sock, SERVER_PAYLOAD_SIZE)
                round_result, rank, suit = decode_server_payload(data)
                card = Card(rank, suit)
                player_cards.append(card)
                player_sum += card.get_value()
                
                GameUI.print_game_state(round_num, player_cards, dealer_cards, player_sum, dealer_sum)

                if round_result == RESULT_LOSS: # player busted (over 21)
                    GameUI.print_result(round_result, round_num, player_sum, dealer_sum)
                    losses += 1
                    break
            
            elif decision == "STAND":
                sock.sendall(encode_client_payload("Stand")) # send 'stand' to server
                
                # Receive dealer cards until final result
                while True:
                    data = recv_exact(sock, SERVER_PAYLOAD_SIZE)
                    round_result, rank, suit = decode_server_payload(data)
                    
                    if round_result == RESULT_NOT_OVER: # dealer not busted
                        # Add card to dealer's hand
                        card = Card(rank, suit)
                        dealer_cards.append(card)
                        dealer_sum += card.get_value()
                        GameUI.print_game_state(round_num, player_cards, dealer_cards, player_sum, dealer_sum)
                    else:
                        # Final result received
                        if round_result == RESULT_WIN:
                            wins += 1
                        elif round_result == RESULT_TIE:
                            ties += 1
                        else:
                            losses += 1
                        break
                
                GameUI.print_result(round_result, round_num, player_sum, dealer_sum)
                break

    return wins, ties, losses


if __name__ == "__main__":
    main()
