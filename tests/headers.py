try:
    from settings import *
except:
    from .settings import *


class SimpleTests(BaseCase):
    def test_simple_hash(self):
        self.blocks.sort(key=lambda b: b.timestamp)
        list(map(lambda b: self.assertTrue(b), self.blocks))


class AlterationHeaderTests(BaseCase):
    def test_state_alteration(self):
        self.blocks = self.blocks.sort(key=lambda block: block.timestamp)
        self.block1.nonce = 1
        self.assertFalse(self.block1.verify_header())

    def test_structure_alteration(self):
        self.block2.parent_blocks = [self.block1, self.block0]
        self.assertTrue(self.block2.verify_header())

        self.block2.parent_blocks = [self.block1]
        self.assertFalse(self.block2.verify_header())