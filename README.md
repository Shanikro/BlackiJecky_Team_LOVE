# 🃏 BlackiJecky_Team_LOVE

This project was created as part of the course  
**“Introduction to Data Communication”**.

The project implements a simplified **Blackjack client-server game**, using
UDP for server discovery and TCP for gameplay.

---

## ▶️ How to Run

### Server
1. Run the server application.
2. The server starts broadcasting offer messages via UDP once every second.
3. The server waits for incoming TCP connections from clients.

### Client
1. Run the client application.
2. The client listens for server offer messages on UDP port **13122**.
3. Upon receiving an offer, the client connects to the server via TCP.
4. The client is prompted to enter the number of rounds to play.

Both client and server are expected to run continuously until terminated manually.

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
