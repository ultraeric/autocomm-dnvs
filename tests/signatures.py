try:
    from settings import *
except:
    from .settings import *
import unittest


class SimpleTests(BaseCase):
    def test_simple_signature(self):
        self.assertTrue(self.block0.verify_from(self.device0))
        self.assertFalse(self.block0.verify_from(self.device1))
        self.assertFalse(self.block0.verify_from(self.device2))
        self.assertTrue(self.block0.verify())

        self.assertFalse(self.block1.verify_from(self.device0))
        self.assertTrue(self.block1.verify_from(self.device1))
        self.assertFalse(self.block1.verify_from(self.device2))
        self.assertTrue(self.block1.verify())

        self.assertFalse(self.block2.verify_from(self.device0))
        self.assertFalse(self.block2.verify_from(self.device1))
        self.assertTrue(self.block2.verify_from(self.device2))
        self.assertTrue(self.block2.verify())


class AlterationSignatureTests(BaseCase):
    def test_block_alteration(self):
        self.block0.nonce = 1
        self.assertFalse(self.block0.verify())
        self.assertFalse(self.block0.verify_from(self.device0))
        self.assertFalse(self.block0.verify_from(self.device1))
        self.assertFalse(self.block0.verify_from(self.device2))

    @unittest.skipUnless(Settings.resolve_deep, 'Deep resolution not enabled. ' +
                                                'Error should be caught in hash evaluation.')
    def test_nested_state_alteration(self):
        self.states[0].nonce = 1
        self.assertFalse(self.block1.verify())
        self.assertFalse(self.block1.verify_from(self.device0))
        self.assertFalse(self.block1.verify_from(self.device1))
        self.assertFalse(self.block1.verify_from(self.device2))

    def test_structure_alteration(self):
        self.block2.parent_blocks = [self.block1]
        self.assertFalse(self.block2.verify())
        self.assertFalse(self.block2.verify_from(self.device0))
        self.assertFalse(self.block2.verify_from(self.device1))
        self.assertFalse(self.block2.verify_from(self.device2))
        self.assertTrue(self.block1.verify())
        self.assertFalse(self.block1.verify_from(self.device0))
        self.assertTrue(self.block1.verify_from(self.device1))
        self.assertFalse(self.block1.verify_from(self.device2))
