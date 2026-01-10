import struct

MAGIC_COOKIE = 0xabcddcba

MSG_OFFER   = 0x2
MSG_REQUEST = 0x3
MSG_PAYLOAD = 0x4

NAME_LEN = 32
DECISION_LEN = 5

# Helpers #
def pad_name(name: str) -> bytes: # pad the name to the length of NAME_LEN
    return name.encode()[:NAME_LEN].ljust(NAME_LEN, b'\x00')

def read_name(raw: bytes) -> str: # read the name from the bytes
    return raw.split(b'\x00', 1)[0].decode()

# OFFER #
OFFER_FMT = "!IBH32s" # ! = network byte order, I = unsigned int, B = unsigned char, H = unsigned short, 32s = bytes string
OFFER_SIZE = struct.calcsize(OFFER_FMT) 

def encode_offer(tcp_port: int, server_name: str) -> bytes:
    return struct.pack(
        OFFER_FMT,
        MAGIC_COOKIE,
        MSG_OFFER,
        tcp_port,
        pad_name(server_name)
    )

def decode_offer(data: bytes):
    cookie, msg_type, port, name = struct.unpack(OFFER_FMT, data)
    if cookie != MAGIC_COOKIE or msg_type != MSG_OFFER:
        raise ValueError("Invalid OFFER packet")
    return port, read_name(name)

# REQUEST #
REQUEST_FMT = "!IBB32s"
REQUEST_SIZE = struct.calcsize(REQUEST_FMT)

def encode_request(num_rounds: int, client_name: str) -> bytes:
    return struct.pack(
        REQUEST_FMT,
        MAGIC_COOKIE,
        MSG_REQUEST,
        num_rounds,
        pad_name(client_name)
    )

def decode_request(data: bytes):
    cookie, msg_type, rounds, name = struct.unpack(REQUEST_FMT, data)
    if cookie != MAGIC_COOKIE or msg_type != MSG_REQUEST:
        raise ValueError("Invalid REQUEST packet")
    return rounds, read_name(name)

# PAYLOAD – Client → Server #
CLIENT_PAYLOAD_FMT = "!IB5s"
CLIENT_PAYLOAD_SIZE = struct.calcsize(CLIENT_PAYLOAD_FMT)

def encode_client_payload(decision: str) -> bytes:
    return struct.pack(
        CLIENT_PAYLOAD_FMT,
        MAGIC_COOKIE,
        MSG_PAYLOAD,
        decision.encode()
    )

def decode_client_payload(data: bytes) -> str:
    cookie, msg_type, decision = struct.unpack(CLIENT_PAYLOAD_FMT, data)
    if cookie != MAGIC_COOKIE or msg_type != MSG_PAYLOAD:
        raise ValueError("Invalid CLIENT PAYLOAD")
    return decision.decode().strip('\x00').upper()

# PAYLOAD – Server → Client #
SERVER_PAYLOAD_FMT = "!IBBHB" # ! = network byte order, I = unsigned int, B = unsigned char, H = unsigned short, B = unsigned char
SERVER_PAYLOAD_SIZE = struct.calcsize(SERVER_PAYLOAD_FMT)

def encode_server_payload(result: int, rank: int, suit: int) -> bytes:
    return struct.pack(
        SERVER_PAYLOAD_FMT,
        MAGIC_COOKIE,
        MSG_PAYLOAD,
        result,
        rank,
        suit
    )

def decode_server_payload(data: bytes):
    cookie, msg_type, result, rank, suit = struct.unpack(SERVER_PAYLOAD_FMT, data)
    if cookie != MAGIC_COOKIE or msg_type != MSG_PAYLOAD:
        raise ValueError("Invalid SERVER PAYLOAD")
    return result, rank, suit