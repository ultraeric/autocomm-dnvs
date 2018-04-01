from objects.obj_utils import Serializable
from threading import RLock
from queue import PriorityQueue


class GlobalState:
    blocks = {}
    devices = {}
    block_q = PriorityQueue()
    leaf_blocks = {}

    block_lock = RLock()
    device_lock = RLock()

    @staticmethod
    def clear():
        with GlobalState.block_lock:
            GlobalState.blocks = {}
        with GlobalState.device_lock:
            GlobalState.devices = {}

    @staticmethod
    def register_device(key, device):
        with GlobalState.device_lock:
            if key in GlobalState.devices.keys():
                return False
            GlobalState.devices[key] = device
            return True

    @staticmethod
    def remove_device(key):
        with GlobalState.device_lock:
            if key in GlobalState.devices.keys():
                del GlobalState.devices[key]

    @staticmethod
    def register_block(key, block):
        with GlobalState.block_lock:
            GlobalState.blocks[key] = block
            GlobalState.block_q.put((block.timestamp, block))
            device_key = block.device.pub_key_hex()
            curr_leaf = GlobalState.leaf_blocks[device_key] if device_key in GlobalState.leaf_blocks else None
            if not curr_leaf:
                GlobalState.leaf_blocks[block.device.pub_key_hex()] = block
            elif block.timestamp > curr_leaf.timestamp:
                GlobalState.leaf_blocks[block.device.pub_key_hex()] = block
    @staticmethod
    def remove_block(key):
        with GlobalState.block_lock:
            if key in GlobalState.blocks.keys():
                del GlobalState.blocks[key]

    @staticmethod
    def clear_stale(end_t):
        with GlobalState.block_lock:
            while not GlobalState.block_q.empty() and GlobalState.block_q.queue[0].timestamp < end_t:
                block = GlobalState.block_q.get()[1]
                GlobalState.remove_block(block.header)
                if block == GlobalState.leaf_blocks[block.device.pub_key_hex()]:
                    del GlobalState.leaf_blocks[block.device.pub_key_hex()]

    @staticmethod
    def get_leaves():
        with GlobalState.block_lock:
            return set(GlobalState.leaf_blocks.values())

global_state = GlobalState()
