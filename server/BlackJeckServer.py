
import socket
import signal
import sys
import threading
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BlackJeckLogic import BlackjackGame, SUITS
from UDPBroadcastOffer import broadcast_offers
from BlackJeckPacketProtocol import decode_request, encode_server_payload, decode_client_payload, REQUEST_SIZE, CLIENT_PAYLOAD_SIZE


def recv_exact(conn: socket.socket, size: int) -> bytes:
    data = b'' # empty byte string
    while len(data) < size:
        chunk = conn.recv(size - len(data)) # receive data from the socket
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
            server_print_winner(game.result, player_name)
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

                if game.result == game.ROUND_RESULT.DEALER_WINS:
                    server_print_winner(game.result, player_name)
                    break

            elif decision == "STAND":
                # expose the second card of the dealer (still NOT_OVER)
                conn.sendall(encode_server_payload(game.result, second_card_dealer.rank, second_card_dealer.suit))

                # Dealer draws until reaching 17+
                while game.dealer_hand.total_value < 17:
                    card = game.dealer_hit()
                    # Always send NOT_OVER for cards (result will be sent after loop)
                    conn.sendall(encode_server_payload(game.ROUND_RESULT.NOT_OVER, card.rank, card.suit))
                
                # After loop: dealer has 17+ or busted, decide winner
                game.decide_winner()
                # Send final result packet (use last card in hand)
                last_card = game.dealer_hand.cards[-1]
                conn.sendall(encode_server_payload(game.result, last_card.rank, last_card.suit))

                server_print_winner(game.result, player_name)

                break # Dealer played, decide winner of round

def server_print_winner(result: int, player_name: str):
    if result == BlackjackGame.ROUND_RESULT.DEALER_WINS:
        print("Dealer wins round")
    elif result == BlackjackGame.ROUND_RESULT.PLAYER_WINS:
        print(f"Player {player_name} wins round")
    else:
        print("Tie")

if __name__ == "__main__":
    main()

