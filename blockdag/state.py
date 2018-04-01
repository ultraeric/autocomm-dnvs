from objects.obj_utils import Headerable, Serializable
import ujson as json


class State(Headerable, Serializable):
    def __init__(self, header='', nonce=0):
        Headerable.__init__(self, header)
        Serializable.__init__(self)
        self.nonce = nonce if nonce else self.generate_nonce(2**16)
        self.finalize()

    def header_contents(self) -> str:
        contents = [self.nonce]
        return json.dumps(contents)

    @staticmethod
    def deserializes(str_repr: str):
        contents = json.loads(str_repr)
        state = State(contents[0], contents[1])
        return state

    def serializes(self) -> str:
        assert self.finalized, 'Trying to serialize an unfinished object.'
        contents = [self.header,
                    self.nonce]
        return json.dumps(contents)
