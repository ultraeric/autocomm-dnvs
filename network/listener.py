from threading import Thread, Lock
from queue import Queue
from .message import Message
import socket
import struct


class Listener(Thread):
    def __init__(self, msg_q: Queue, q_lock: Lock, ip: str='', port: int=5005):
        super().__init__()
        self.msg_q = msg_q
        self.q_lock = q_lock
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))
        self._shutdown = False
        print('Listener started at IP {} on port {}'.format(ip, port))

    def shutdown(self):
        self._shutdown = True

    def run(self):
        while not self._shutdown:
            data, address = self.recv()
            with self.q_lock:
                self.msg_q.put(Message(address[0], address[1], data))

    def recv(self) -> (bytes, str):
        data, address = self.socket.recvfrom(65535)
        print('Received data.')
        return data, address

    def recv_n(self, n) -> (bytes, str):
        # Note: Only use with TCP/IP
        data = b''
        address = None
        while len(data) < n:
            packet, address = self.socket.recvfrom(n - len(data))
            if not packet:
                return None
            data += packet
        return data, address
