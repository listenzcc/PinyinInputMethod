# File: web_compat.py
# Aim: Provide web compat interface of the package

from . import _cellDicts_path
from .pinYin_engine import PinYinEngine


class Worker(object):
    def __init__(self):
        self.engine = PinYinEngine(_cellDicts_path[0])

    def response(self, path):
        # Received path is like this:
        #   /pinYinCheckout?query=[pinYin]
        #     [pinYin] is the pinYin of interestf

        # Format check
        head = 'pinYinCheckOut?query='
        if not path.startswith(head):
            return None

        if len(path) == len(head):
            return '{}'

        # Checkout
        pinYin = path[len(head):]
        return self.engine.checkout(pinYin, return_json=True)