from objects.obj_utils import Signer, Serializable
from .global_state import global_state
import json


class Device(Signer, Serializable):
    def __init__(self, pub_key=None, priv_key=None):
        Signer.__init__(self, pub_key, priv_key)
        Serializable.__init__(self)
        self.is_new = global_state.register_device(self.pub_key_hex(), self)
        if self.is_new:
            print('New device registered.')

    def serializes(self) -> str:
        contents = [self.pub_key_hex()]
        return json.dumps(contents)

    @staticmethod
    def deserializes(str_repr: str):
        contents = json.loads(str_repr)
        return Device(pub_key=contents[0])

