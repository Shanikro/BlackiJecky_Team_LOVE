import socket
import signal
import sys
import os
import threading

# Add parent directory to path for package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from black_jeck.BlackJeckLogic import BlackjackGame
from black_jeck.UDPBroadcastOffer import UDPBroadcastOffer
from network.TCPConnection import recv_exact
from black_jeck.BlackJeckPacketProtocol import decode_request, encode_server_payload, decode_client_payload,\
     REQUEST_SIZE, CLIENT_PAYLOAD_SIZE

SERVER_NAME = "Team_LOVE"
DEFAULT_IP = "127.0.0.1"

# global variables for graceful shutdown
tcp_sock = None
stop_event = None


def signal_handler(sig, frame):
    """Handle graceful shutdown on Ctrl+C or kill command."""
    print("\nShutting down server...")
    if stop_event:
        stop_event.set()
    if tcp_sock:
        tcp_sock.close()
    sys.exit(0)


def get_local_ip() -> str:
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
    global tcp_sock, stop_event
    
    server_ip = get_local_ip()
    print(f"Server started, listening on IP address {server_ip}") # print server IP

    # Create TCP socket and bind to any available port
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create TCP socket
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow reuse of address
    tcp_sock.bind(("", 0)) # bind to any available port
    tcp_sock.listen(5) # listen for connections (5 connections at a time)
    tcp_port = tcp_sock.getsockname()[1] # get the port number
    
    # Create stop event and start broadcast thread
    stop_event = threading.Event() # create stop event
    broadcaster = UDPBroadcastOffer()
    broadcast_thread = threading.Thread( # create broadcast thread
        target=broadcaster.broadcast,
        args=(tcp_port, SERVER_NAME, stop_event),
        daemon=True # daemon thread (dies when main thread dies)
    )
    broadcast_thread.start() # start broadcast thread
    
    signal.signal(signal.SIGINT, signal_handler) # register signal handler for graceful shutdown

    # wait for connections
    try:
        while True:
            conn, addr = tcp_sock.accept() # accept connection from client
            print(f"New client connected from {addr}") # print client address (IP and port)

            try:
                rounds, name = decode_request(recv_exact(conn, REQUEST_SIZE)) # decode request from client
                if rounds < 1:
                    print("Invalid number of rounds")
                    conn.close()
                    continue

                play_game(conn, rounds, name) # play game with client

            except Exception as e: # handle exception
                print(f"Error handling client {addr}: {e}")
            finally: # close connection
                conn.close()
    except KeyboardInterrupt: # Ctrl+C or kill command
        print("\nShutting down server...")
        signal_handler(None, None) # call signal handler

def play_game(conn: socket.socket, rounds: int, player_name: str):

    print(f"Starting {rounds} rounds with player {player_name}")

    for round_num in range(1, rounds + 1):
        print(f"{'='*50}")
        print(f"Round {round_num}/{rounds} - {player_name}")
        
        game = BlackjackGame() # create new round game

        first_card_player = game.player_hit()
        conn.sendall(encode_server_payload(game.result, first_card_player.rank, first_card_player.suit))

        second_card_player = game.player_hit()
        conn.sendall(encode_server_payload(game.result, second_card_player.rank, second_card_player.suit))

        if game.result == game.ROUND_RESULT.DEALER_WINS: # player busts
            server_print_winner(game.result, player_name)
            continue # Dealer wins, no need to continue the round

        first_card_dealer = game.dealer_hit()
        conn.sendall(encode_server_payload(game.result, first_card_dealer.rank, first_card_dealer.suit))

        second_card_dealer = game.dealer_hit() # second card of dealer hidden

        # Player turn
        while True:
            decision = decode_client_payload(recv_exact(conn, CLIENT_PAYLOAD_SIZE)) # decode decision from client

            if decision == "HITTT":
                card = game.player_hit()
                conn.sendall(encode_server_payload(game.result, card.rank, card.suit)) # send card to client

                if game.result == game.ROUND_RESULT.DEALER_WINS: # player busts
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

