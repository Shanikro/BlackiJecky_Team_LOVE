from typing import Tuple
import sys
import os

# Add parent directory to path for package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network.UDPBroadcast import UDPBroadcast
from black_jeck.BlackJeckPacketProtocol import encode_offer, decode_offer

class UDPBroadcastOffer(UDPBroadcast):
    # Implements encode/decode for offer messages.

    def encode(self, tcp_port: int, server_name: str) -> bytes:
        return encode_offer(tcp_port, server_name)
    
    def decode(self, data: bytes) -> Tuple[int, str]:
        return decode_offer(data)  # returns (tcp_port, server_name)
