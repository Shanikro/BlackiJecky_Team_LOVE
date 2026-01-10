# udp_broadcast.py
import socket
import time
from typing import Optional, Tuple
import threading

from BlackJeckPacketProtocol import decode_offer, encode_offer


UDP_PORT = 13122
OFFER_INTERVAL_SEC = 1.0


def get_broadcast_address() -> str:
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


def broadcast_offers(server_tcp_port: int, server_name: str, stop_event: threading.Event = None) -> None:
    """
    Broadcast UDP offers. Can be stopped by setting stop_event.
    
    Args:
        server_tcp_port: TCP port to advertise
        server_name: Name of the server
        stop_event: Optional threading.Event to signal stop
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # OS chooses the interface
    sock.bind(('', 0))

    offer_bytes = encode_offer(server_tcp_port, server_name)

    try:
        while True:
            # Check if we should stop
            if stop_event and stop_event.is_set():
                break
                
            try:
                broadcast_addr = get_broadcast_address()
                
                # Send to the calculated broadcast address
                sock.sendto(offer_bytes, (broadcast_addr, UDP_PORT))
                
                # Also send to localhost in case server and client are on same machine
                try:
                    sock.sendto(offer_bytes, ('127.0.0.1', UDP_PORT))
                except Exception:
                    pass
                    
            except Exception:
                pass
                
            time.sleep(OFFER_INTERVAL_SEC)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    finally:
        sock.close()


def listen_for_offer(timeout_sec: float = 0.0) -> Optional[Tuple[str, int, str]]:
    """
    Client side:
    Listens on UDP_PORT for OFFER.
    Returns (server_ip, server_tcp_port, server_name) on success.
    If timeout_sec > 0, returns None on timeout.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Allow multiple clients on the same machine (as per instructions)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Enable broadcast reception
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except (AttributeError, OSError):
        pass

    sock.bind(("", UDP_PORT))

    if timeout_sec and timeout_sec > 0:
        sock.settimeout(timeout_sec)

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            server_ip = addr[0]

            try:
                tcp_port, server_name = decode_offer(data)
                return server_ip, tcp_port, server_name
            except Exception:
                # packet is not valid (cookie/type/length) -> ignore
                continue

    except socket.timeout:
        return None
    finally:
        sock.close()