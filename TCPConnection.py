import socket


def recv_exact(sock: socket.socket, size: int) -> bytes:
    """Receive exactly 'size' bytes from the socket."""
    data = b''
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection closed unexpectedly")
        data += chunk
    return data
