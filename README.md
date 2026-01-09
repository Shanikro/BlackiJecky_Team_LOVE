# 🃏 BlackiJecky_Team_LOVE

This project was created as part of the course  
**“Introduction to Data Communication”**.

The project implements a simplified **Blackjack client-server game**, using
UDP for server discovery and TCP for gameplay.

---

## ▶️ How to Run

### Server
1. Navigate to the server directory: `cd server`
2. Run the server: `python server_main.py`
3. The server will print its IP address and start broadcasting offer messages via UDP once every second.
4. The server waits for incoming TCP connections from clients.
5. Press Ctrl+C to stop the server.

### Client
1. Navigate to the client directory: `cd client`
2. Run the client: `python client_main.py`
3. The client listens for server offer messages on UDP port **13122**.
4. When an offer is received, you'll be prompted to enter the number of rounds to play (1-255).
5. Play the game by choosing 'h' for Hit or 's' for Stand.
6. After all rounds, the client will display statistics and return to listening for new offers.
7. Press Ctrl+C to stop the client.

**Note:** Both client and server are expected to run continuously until terminated manually. You can run multiple clients on the same machine - they will all listen on the same UDP port thanks to SO_REUSEPORT.

---

## 🎮 Game Flow

1. The server shuffles a standard 52-card deck.
2. The client receives two face-up cards.
3. The dealer (server) receives two cards:
   - One card is revealed to the client.
   - The second card is hidden until the dealer’s turn.
4. The client repeatedly chooses:
   - **Hit** – receive another card.
   - **Stand** – stop receiving cards.
5. If the client’s total exceeds 21, the client busts and loses the round.
6. If the client does not bust, the dealer reveals the hidden card and draws cards
   until the dealer’s total is at least 17 or the dealer busts.
7. The winner is determined according to Blackjack rules.
8. The server sends the round result (win / loss / tie) to the client.
9. After all rounds are completed, the client prints final statistics and win rate,
   closes the TCP connection, and returns to listening for offers.

---

## ❤️ Team LOVE

Created with love as part of the Networks course hackathon.  
Have fun – and may your protocol never bust 😉
