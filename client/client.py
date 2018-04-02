from network import *
from threading import Thread, Lock
from queue import Queue, PriorityQueue
from blockdag import *
import time


class Client(Thread):
    def __init__(self, port: int=5005, broadcast_port: int=5005):
        super().__init__()
        self.port = port
        self.broadcast_port = broadcast_port
        self.msg_q = Queue()
        self.q_lock = Lock()
        self.listener = Listener(self.msg_q, self.q_lock, port=port)
        self.listener.start()
        self._shutdown = False
        self.device = Device()
        self.device_message = Message(port=self.broadcast_port, data=self.device.serializes().encode('utf-8'), annotation=Message.DEVICE)
        broadcaster.broadcast(self.device_message)
        self.unprocessed = PriorityQueue()

    def run(self):
        last_timestamp = time.time()
        while not self._shutdown:
            curr_timestamp = time.time()
            # Create a new block every 100 ms
            if curr_timestamp - last_timestamp > 0.1:
                last_timestamp = curr_timestamp
                msgs = []
                with self.q_lock:
                    while not self.msg_q.empty():
                        msgs.append(self.msg_q.get())
                device_msgs = [msg for msg in msgs if msg.annotation == Message.DEVICE]
                msgs = [msg for msg in msgs if msg.annotation == Message.BLOCK]
                for device_msg in device_msgs:
                    if Device.deserializes(device_msg.data.decode('utf-8')).is_new:
                        broadcaster.broadcast(self.device_message)
                for msg in msgs:
                    print(Block.deserializes(msg.data.decode('utf-8')))
                leaves = set(global_state.get_leaves())
                state = State(nonce=(sum([block.state.nonce for block in leaves]) / len(leaves) if len(leaves) != 0 else 0) + 1)
                block = Block(self.device, state, parent_blocks=leaves)
                message = Message(port=self.broadcast_port, data=block.serializes().encode('utf-8'), annotation=Message.BLOCK)
                print(block)
                broadcaster.broadcast(message)

    def shutdown(self):
        self._shutdown = True
