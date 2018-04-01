class Message:
    DEVICE = 0
    BLOCK = 1

    def __init__(self, address: str='127.0.0.1', port: int=5005, data: bytes=b'', annotation: int=-1):
        self.addr = address
        self.port = port
        if annotation == -1:
            self.data = data[4:]
            self.annotation = int.from_bytes(data[:4], byteorder='big')
        else:
            self.data = annotation.to_bytes(4, byteorder='big') + data
            self.annotation = annotation
