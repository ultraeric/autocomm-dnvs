import socket
from .message import Message


class Broadcaster:
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @staticmethod
    def broadcast(message: Message):
        Broadcaster.socket.sendto(message.data, (message.addr, message.port))
        print('Broadcasted message.')

broadcaster = Broadcaster()
