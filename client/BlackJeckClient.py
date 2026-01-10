import socket
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UDPBroadcast import listen_for_offer
from BlackJeckPacketProtocol import decode_server_payload, encode_request, encode_client_payload, SERVER_PAYLOAD_SIZE
from BlackJeckLogic import BlackjackGame, Card, SUITS
from GameUI import GameUI

RESULT_NOT_OVER = BlackjackGame.ROUND_RESULT.NOT_OVER
RESULT_WIN = BlackjackGame.ROUND_RESULT.PLAYER_WINS
RESULT_LOSS = BlackjackGame.ROUND_RESULT.DEALER_WINS
RESULT_TIE = BlackjackGame.ROUND_RESULT.TIE

def main():
    print("BlackJeckClient started")
    
    while True:
        sock = None
        try:
            print("Client started, listening for offer requests...")
            server_ip, server_tcp_port, server_name = listen_for_offer()
            if server_ip is None:
                print("No server offer received")
                continue
            print(f"Server offer received from {server_ip}:{server_tcp_port} - {server_name}")

            team_name = input("Enter your name: ")
            num_rounds = int(input("How many rounds would you like to play? "))
                
            if num_rounds < 1:
                print("Number of rounds must be at least 1")
                continue
            
            # Create new socket and connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server_ip, server_tcp_port))
            sock.sendall(encode_request(num_rounds, team_name))

            wins, ties = play_game(sock, server_name, team_name, num_rounds)
            GameUI.print_statistics(team_name, wins, ties, num_rounds)

        except KeyboardInterrupt:
            print("\nShutting down client...")
            break
        finally:
            if sock:
                sock.close()


"""
Receive exactly 'size' bytes from the socket.
"""
def recv_exact(sock: socket.socket, size: int) -> bytes:
    data = b'' # empty byte string
    while len(data) < size:
        chunk = sock.recv(size - len(data)) # receive data from the socket
        if not chunk:
            raise ConnectionError("Connection closed unexpectedly")
        data += chunk
    return data


def play_game(sock: socket.socket, server_name: str, team_name: str, num_rounds: int):

    wins = 0
    ties = 0

    for round_num in range(1, num_rounds + 1):
        # initialize the UI (init also the player and dealer sums)
        UI = GameUI()

        # receive the first two cards from the server
        for _ in range(2):
            data = recv_exact(sock, SERVER_PAYLOAD_SIZE)
            round_result, rank, suit_idx = decode_server_payload(data)
            UI.add_player_card(Card(rank, suit_idx), round_num)

        # Check if the player has bust
        if round_result == RESULT_LOSS:
            UI.print_result(round_result, round_num)
            continue

        # receive the dealer first card
        data = recv_exact(sock, SERVER_PAYLOAD_SIZE)
        round_result, rank, suit_idx = decode_server_payload(data)
        UI.add_dealer_card(Card(rank, suit_idx), round_num)

        # play the game
        while True:
            decision = None
            while decision not in ("HITTT", "STAND", "HITT", "HIT"):
                decision = input("Please type Hittt or Stand: ").strip().upper()

            if decision in ("HITTT", "HITT", "HIT"):
                sock.sendall(encode_client_payload("Hittt"))
                data = recv_exact(sock, SERVER_PAYLOAD_SIZE)
                round_result, rank, suit_idx = decode_server_payload(data)
                UI.add_player_card(Card(rank, suit_idx), round_num)

                # Check if the player has bust
                if round_result == RESULT_LOSS:
                    UI.print_result(round_result, round_num)
                    break
            
            elif decision == "STAND":
                sock.sendall(encode_client_payload("Stand"))
                while True:
                    data = recv_exact(sock, SERVER_PAYLOAD_SIZE)
                    round_result, rank, suit_idx = decode_server_payload(data)
                    
                    # Only add card if round is still ongoing
                    if round_result == RESULT_NOT_OVER:
                        UI.add_dealer_card(Card(rank, suit_idx), round_num)
                    else:
                        # Final result received, don't add card (already added)
                        if round_result == RESULT_WIN:
                            wins += 1
                        elif round_result == RESULT_TIE:
                            ties += 1
                        break
                
                UI.print_result(round_result, round_num)
                break # Dealer played, decide winner of round

    return wins, ties

if __name__ == "__main__":
    main()