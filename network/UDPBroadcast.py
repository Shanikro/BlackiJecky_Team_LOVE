import socket
import time
from typing import Tuple
import threading
from abc import ABC, abstractmethod

class UDPBroadcast(ABC): # abstract base class for UDP broadcast

    UDP_PORT = 13122
    OFFER_INTERVAL_SEC = 1.0


    def get_broadcast_address(self) -> str:
        """Get the broadcast address for the local network."""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Calculate broadcast address (assuming /24 subnet)
            # For example, 10.125.203.87 -> 10.125.203.255
            ip_parts = local_ip.split('.')
            ip_parts[3] = '255'
            broadcast_addr = '.'.join(ip_parts)
            return broadcast_addr
        except Exception:
            # Fallback to generic broadcast
            return '<broadcast>'


    # Broadcast the offers (Server side)
    def broadcast(self, server_tcp_port: int, server_name: str, stop_event: threading.Event = None) -> None:
        # Create a socket and set the broadcast option
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # OS chooses the interface
        sock.bind(('', 0))

        offer_bytes = self.encode(server_tcp_port, server_name) # encode - subclass must implement

        try:
            while True:
                # Check if we should stop
                if stop_event and stop_event.is_set():
                    break
                    
                try:
                    broadcast_addr = self.get_broadcast_address()
                    
                    # Send to the calculated broadcast address
                    sock.sendto(offer_bytes, (broadcast_addr, self.UDP_PORT))
                    
                    # Also send to localhost in case server and client are on same machine
                    try:
                        sock.sendto(offer_bytes, ('127.0.0.1', self.UDP_PORT))
                    except Exception:
                        pass
                        
                except Exception:
                    pass
                    
                time.sleep(self.OFFER_INTERVAL_SEC)
        except KeyboardInterrupt:
            # Ctrl+C -> stop the broadcast
            pass
        finally:
            sock.close()


    # Listen for offers (Client side)
    def listen(self) -> Tuple[str, int, str]:

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow multiple clients on the same machine
        # allow port reuse (exists on macOS/Linux; usually not on Windows)
        if hasattr(socket, "SO_REUSEPORT"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # (optional but recommended) avoid "WSAECONNRESET" on Windows UDP receive
        if hasattr(socket, "SIO_UDP_CONNRESET"):
            sock.ioctl(socket.SIO_UDP_CONNRESET, False)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # enable broadcast reception
        sock.bind(("", self.UDP_PORT))

        try:
            while True:
                data, addr = sock.recvfrom(1024)
                try:
                    tcp_port, server_name = self.decode(data) # decode - subclass must implement
                    return addr[0], tcp_port, server_name
                except Exception:
                    continue  # Invalid packet, keep waiting
        finally:
            sock.close()


    @abstractmethod
    def encode(self, data: bytes) -> bytes:
        pass

    @abstractmethod
    def decode(self, data: bytes) -> Tuple[int, str]:
        pass