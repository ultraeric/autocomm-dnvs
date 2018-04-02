from abc import abstractmethod
from .settings import settings
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import random

SHA = settings.SHA
RSA_BIT_LENGTH = 2 * settings.SIG_SEC_LEVEL


class Serializable:
    def __init__(self):
        pass

    def serialize(self, filepath: str):
        str_repr = self.serializes()
        with open(filepath, 'w+') as f:
            f.write(str_repr)

    @abstractmethod
    def serializes(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def deserializes(str_repr: str):
        pass


class Headerable:
    def __init__(self, header=''):
        self._header = header
        self.finalized = False

    @property
    def header(self):
        assert self.finalized, 'Attempting to access header of non-finalized object.'
        return self._header

    @header.setter
    def header(self, header: str=''):
        self._header = header

    def generate_header(self) -> str:
        return SHA.new(SHA.new(self.header_contents().encode()).digest()).hexdigest()

    def verify_header(self):
        assert self.finalized, 'Attempting to verify non-finalized object.'
        return self.header == self.generate_header()

    def finalize(self):
        self.finalized = True
        self.header = self.header if self.header else self.generate_header()
        try:
            assert self.verify_header(), 'Instantiated header and calculated header are different.'
        except Exception:
            print('Failed to finalize Headerable')
            self.finalized = False

    @staticmethod
    def generate_nonce(max=2**64):
        return random.randint(1, max)

    @abstractmethod
    def header_contents(self) -> str:
        # IMPORTANT: To make this cryptographically secure, the header contents should include anything
        # that is a liability if faked. Anything related to uniqueness/identity should be included here.
        pass


class Signable(Headerable):
    def __init__(self, device=None, signature='', header=''):
        super().__init__(header=header)
        self.device = device
        self.signature = signature

    @abstractmethod
    def header_contents(self):
        pass

    def finalize(self):
        super().finalize()
        if self.device.is_mine():
            self.signature = self.device.sign(self)
        try:
            assert self.verify(), 'Block contains invalid signature.'
        except Exception:
            print('Failed to finalize Signable')
            self.finalized = False

    def verify(self):
        assert self.finalized, 'Attempting to verify non-finalized Block.'
        return self.device.verify(self, self.signature)

    def verify_from(self, device):
        assert self.finalized, 'Attempting to verify non-finalized Block.'
        return self.finalized and device.verify(self, self.signature)


class Signer:
    def __init__(self, pub_key=None, priv_key=None):
        self.pub_key = RSA.importKey(bytes.fromhex(pub_key)) if isinstance(pub_key, str) else pub_key
        self._priv_key = RSA.importKey(bytes.fromhex(priv_key)) if isinstance(priv_key, str) else priv_key
        if pub_key is None:
            self.init_signer()
            print('Initializing signer')

    def pub_key_hex(self):
        return self.pub_key.exportKey('DER').hex()

    def priv_key_hex(self):
        return self._priv_key.exportKey('DER').hex()

    def is_mine(self):
        return self._priv_key is not None

    def init_signer(self):
        assert self.pub_key is None and self._priv_key is None, 'Keys already exist'
        self._priv_key = RSA.generate(RSA_BIT_LENGTH)
        self.pub_key = self._priv_key.publickey()

    def sign(self, signable: Signable) -> str:
        # SHA256^2 hash
        hash = SHA.new(SHA.new(signable.generate_header().encode()).digest())
        signer = PKCS1_v1_5.new(self._priv_key)
        return signer.sign(hash).hex()

    def verify(self, signable: Signable, signature):
        # SHA256^2 hash
        signature = bytes.fromhex(signature) if isinstance(signature, str) else signature
        hash = SHA.new(SHA.new(signable.generate_header().encode()).digest())
        verifier = PKCS1_v1_5.new(self.pub_key)
        return verifier.verify(hash, signature)