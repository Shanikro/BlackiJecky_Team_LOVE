
import socket
import signal
import sys
import threading
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BlackJeckLogic import BlackjackGame, SUITS
from UDPBroadcast import broadcast_offers
from BlackJeckPacketProtocol import decode_request, encode_server_payload, decode_client_payload, REQUEST_SIZE, CLIENT_PAYLOAD_SIZE


def recv_exact(conn: socket.socket, size: int) -> bytes: # TODO: לבדוק מה זה עושה
    """Receive exactly 'size' bytes from the connection."""
    data = b''
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection closed unexpectedly")
        data += chunk
    return data

# Constants
SERVER_NAME = "Team_LOVE"
DEFAULT_IP = "127.0.0.1"

def get_local_ip() -> str:
    """Get the local IP address of this machine."""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return DEFAULT_IP

def main():
    server_ip = get_local_ip()
    print(f"Server started, listening on IP address {server_ip}")

    # Create TCP socket and bind to any available port
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(("", 0))          # 0 = OS chooses port
    tcp_sock.listen(5) # listen for up to 5 connections in the queue
    tcp_port = tcp_sock.getsockname()[1] # get the tcp port
    
    # Create stop event for graceful shutdown
    stop_event = threading.Event()
    
    # Start broadcasting the offer in a separate thread
    broadcast_thread = threading.Thread(
        target=broadcast_offers,
        args=(tcp_port, SERVER_NAME, stop_event),
        daemon=True
    )
    broadcast_thread.start()
    
    # Handle graceful shutdown on Ctrl+C
    def signal_handler(sig, frame):
        print("\nShutting down server...")
        stop_event.set()  # Stop broadcasting
        tcp_sock.close()   # Close TCP socket
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill command

    # Wait for connections
    try:
        while True:
            conn, addr = tcp_sock.accept()
            print(f"New client connected from {addr}")

            try:
                rounds, name = decode_request(recv_exact(conn, REQUEST_SIZE))
                if rounds < 1:
                    print("Invalid number of rounds")
                    conn.close()
                    continue
                play_game(conn, rounds, name)
            except Exception as e:
                print(f"Error handling client {addr}: {e}")
            finally:
                conn.close()
    except KeyboardInterrupt: # Ctrl+C or kill command
        print("\nShutting down server...")
        signal_handler(None, None)

def play_game(conn: socket.socket, rounds: int, player_name: str):

    print(f"Starting {rounds} rounds with player {player_name}")

    for round_num in range(1, rounds + 1):
        print(f"{'='*50}")
        print(f"Round {round_num}/{rounds} - {player_name}")
        
        game = BlackjackGame()

        first_card_player = game.player_hit()
        conn.sendall(encode_server_payload(game.result, first_card_player.rank, first_card_player.suit))

        second_card_player = game.player_hit()
        conn.sendall(encode_server_payload(game.result, second_card_player.rank, second_card_player.suit))

        if game.result == game.ROUND_RESULT.DEALER_WINS:
            decide_winner(game.result, player_name)
            continue # Dealer wins, no need to continue the round

        first_card_dealer = game.dealer_hit()
        conn.sendall(encode_server_payload(game.result, first_card_dealer.rank, first_card_dealer.suit))

        second_card_dealer = game.dealer_hit()

        # Player turn
        while True:
            decision = decode_client_payload(recv_exact(conn, CLIENT_PAYLOAD_SIZE))

            if decision == "HITTT":
                card = game.player_hit()
                conn.sendall(encode_server_payload(game.result, card.rank, card.suit))

                if game.player_hand.is_bust():
                    decide_winner(game.result, player_name)
                    break 

            elif decision == "STAND":
                # expose the second card of the dealer
                conn.sendall(encode_server_payload(game.result, second_card_dealer.rank, second_card_dealer.suit))

                while game.dealer_hand.total_value < 17:
                    card = game.dealer_hit()
                    #degud print
                    print("Dealer hits, new card:", card.rank)
                    print("Dealer hand value now:", game.dealer_hand.total_value)
                    conn.sendall(encode_server_payload(game.result, card.rank, card.suit))

                #debug print
                print("Final dealer hand value:", game.dealer_hand.total_value)
                game.decide_winner()
                conn.sendall(encode_server_payload(game.result, 0, 0)) # send final result with dummy card
                decide_winner(game.result, player_name)

                break # Dealer plays, decide winner

def decide_winner(result: int, player_name: str):
    if result == BlackjackGame.ROUND_RESULT.DEALER_WINS:
        print("Dealer wins round")
    elif result == BlackjackGame.ROUND_RESULT.PLAYER_WINS:
        print(f"Player {player_name} wins round")
    else:
        print("Tie")

if __name__ == "__main__":
    main()

