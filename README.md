# 🃏 BlackiJecky_Team_LOVE

This project was created as part of the course  
**"Introduction to Data Communication"**.

The project implements a simplified **Blackjack client-server game**, using
UDP for server discovery and TCP for gameplay.

## ▶️ How to Run

Run from the **project root folder** (BlackiJecky_Team_LOVE):

### Server
```bash
python3 black_jeck/BlackJeckServer.py
```
- The server will print its IP address and start broadcasting offers via UDP.
- Press `Ctrl+C` to stop the server.

### Client
```bash
python3 black_jeck/BlackJeckClient.py
```
- The client listens for server offers on UDP port **13122**.
- Enter your name and the number of rounds to play.
- Play by typing `Hit` or `Stand`.
- Press `Ctrl+C` to stop the client.

**Note:** You can run multiple clients on the same machine.


---

## ❤️ Team LOVE

Created with love as part of the Networks course hackathon.  
Have fun – and may your protocol never bust 😉
