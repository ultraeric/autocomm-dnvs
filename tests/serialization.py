from blockdag.block import Block
from blockdag.global_state import global_state
try:
    from settings import *
except:
    from .settings import *


class SimpleTests(BaseCase):
    def test_simple_reserialization(self):
        block2 = self.block2
        del global_state.blocks[block2.header]
        block2_ser = self.block2.serializes()
        block2_deser = Block.deserializes(block2_ser)
        self.assertTrue(block2_deser.serializes() == block2_ser)
        self.assertTrue(block2.device == block2_deser.device)
        self.assertTrue(block2.header == block2_deser.header)
