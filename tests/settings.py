import unittest

from blockdag.block import Block
from blockdag.device import Device
from blockdag.global_state import global_state
from blockdag.state import State


class Settings:
    resolve_deep = False


class BaseCase(unittest.TestCase):
    def setUp(self):
        global_state.clear()
        self.states = [State('', i) for i in range(20)]
        list(map(lambda s: s.finalize(), self.states))

        self.device0 = Device()
        self.device1 = Device()
        self.device2 = Device()

        self.block0 = Block(self.device0, self.states[0], [])
        self.block0.finalize()
        self.block1 = Block(self.device1, self.states[1], [self.block0])
        self.block1.finalize()
        self.block2 = Block(self.device2, self.states[2], [self.block0, self.block1])
        self.block2.finalize()
        self.blocks = [self.block0, self.block1, self.block2]

        # We only own genesis block's device
        self.block1.device._priv_key = None
        self.block2.device._priv_key = None
