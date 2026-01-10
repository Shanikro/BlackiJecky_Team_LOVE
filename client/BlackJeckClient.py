
import socket
import signal
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

# Global variable to track current socket for graceful shutdown
current_sock = None


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nShutting down client...")
    if current_sock:
        try:
            current_sock.close()
        except:
            pass
    sys.exit(0)


def main():
    global current_sock
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill command
    
    print("BlackJeckClient started")
    
    try: # TODO:לחזור על הפונקציה ולראות שלא סתם עושה מלא דברים 
        while True:
            sock = None
            try:
                print("Client started, listening for offer requests...")
                server_ip, server_tcp_port, server_name = listen_for_offer()
                if server_ip is None:
                    print("No server offer received")
                    continue
                print(f"Server offer received from {server_ip}:{server_tcp_port} - {server_name}")

                #get team name from user
                try:
                    team_name = input("Enter your name: ")
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting...")
                    break

                try:
                    num_rounds = int(input("How many rounds would you like to play?  "))
                except (EOFError, KeyboardInterrupt, ValueError):
                    print("\nInvalid input or interrupted. Returning to listen for offers...")
                    continue
                    
                if num_rounds < 1:
                    print("Number of rounds must be at least 1")
                    continue
                
                # Create new socket for each game session
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                current_sock = sock  # Track for signal handler
                
                sock.connect((server_ip, server_tcp_port))
                sock.sendall(encode_request(num_rounds, team_name)) # send the request to the server

                wins = play_game(sock, server_name, team_name, num_rounds)
                
                # Print game statistics
                GameUI.print_statistics(team_name, wins, num_rounds)


            except KeyboardInterrupt:
                print("\nInterrupted. Returning to listen for offers...")
            except Exception as e:
                print(f"Error: {e}. Returning to listen for offers...")
            finally:
                # Close socket after each game session
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
                current_sock = None
                
    except KeyboardInterrupt:
        signal_handler(None, None)


def recv_exact(sock: socket.socket, size: int) -> bytes: # TODO: לבדוק מה זה עושה
    """Receive exactly 'size' bytes from the socket."""
    data = b''
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection closed unexpectedly")
        data += chunk
    return data


def play_game(sock: socket.socket, server_name: str, team_name: str, num_rounds: int):

    wins = 0

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
            try:
                while decision not in ("HITTT", "STAND", "HITT", "HIT"):
                    decision = input("Please type Hittt or Stand: ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("\nInterrupted during game. Closing connection...")
                raise  # Re-raise to be caught by outer handler

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
                        break
                
                UI.print_result(round_result, round_num)
                break # Dealer played, decide winner of round

    return wins

if __name__ == "__main__":
    main()