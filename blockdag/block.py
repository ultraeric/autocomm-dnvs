import ujson as json
import time

from blockdag.device import Device
from blockdag.state import State
from objects.obj_utils import Serializable, Signable
from .global_state import global_state


class Block(Serializable, Signable):
    def __init__(self, device: Device=None, state: State=None, parent_blocks=set(), timestamp=0.,
                 nonce=0, header='', signature=''):
        assert device is not None, 'Must have a valid device creator.'
        assert all([block.finalized for block in parent_blocks]), 'All parent blocks must be finalized.'
        Serializable.__init__(self)
        Signable.__init__(self, device=device, header=header, signature=signature)
        self.device = device
        self.state = state
        self.parent_blocks = set(parent_blocks)
        self.timestamp = timestamp if timestamp else time.time()
        self.nonce = nonce if nonce else self.generate_nonce(2**16)
        self.finalize()

    @staticmethod
    def deserializes(str_repr: str):
        contents = json.loads(str_repr)
        device = global_state.devices[contents[1]]
        parent_blocks = [global_state.blocks[header] for header in contents[5]]
        state = State.deserializes(contents[3])
        block = Block(device, state, parent_blocks, contents[2], contents[6], contents[0], contents[4])
        return block

    def serializes(self) -> str:
        assert self.finalized, 'Trying to serialize an unfinished object.'
        contents = [self.header,
                    self.device.pub_key_hex(),
                    self.timestamp,
                    self.state.serializes(),
                    self.signature,
                    sorted([block.header for block in self.parent_blocks]),
                    self.nonce]
        return json.dumps(contents)

    def header_contents(self) -> str:
        # TODO: Make the header directly dependent on immutable state
        contents = [self.device.pub_key_hex(),
                    self.timestamp,
                    self.state.header,
                    sorted([block.header for block in self.parent_blocks]),
                    self.nonce]
        return json.dumps(contents)

    def finalize(self):
        super().finalize()
        try:
            global_state.register_block(self.header, self)
        except:
            self.finalized = False

    def __repr__(self):
        return 'Header: {}, Device: {}, State: {}, Timestamp: {}, Parents: {}, Nonce: {}, Signature: {}'\
            .format(self.header, self.device.pub_key_hex()[-64:], self.state.nonce, self.timestamp, str([block.header for block in self.parent_blocks]), self.nonce, self.signature[-64:])
