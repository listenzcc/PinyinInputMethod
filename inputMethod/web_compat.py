# File: web_compat.py
# Aim: Provide web compat interface of the package

import json
import threading
import urllib
from . import _cellDict_path
from .pinYin_engine import PinYinEngine


class Worker(object):
    def __init__(self):
        self.engine = PinYinEngine(_cellDict_path)

    def response(self, path):
        # Received path is like this:
        #   /pinYinCheckout?query=[pinYin]
        #     [pinYin] is the pinYin of interest

        # Checkout command
        head = 'pinYinCheckOut?query='
        if path.startswith(head):
            # Check if is empty
            if len(path) == len(head):
                return '{}'
            # Checkout
            pinYin = path[len(head):]
            return self.engine.checkout(pinYin, return_json=True)

        # Update command
        head = 'pinYinUpdate?pair='
        if path.startswith(head):
            pair = path[len(head):].split(',')
            assert(len(pair) == 2)
            pinYin = urllib.parse.unquote(pair[0])
            ciZu = urllib.parse.unquote(pair[1])
            self.engine.add_user_frame(pinYin=pinYin, ciZu=ciZu)
            response = dict(
                State='Success',
                pinYin=pinYin,
                ciZu=ciZu
            )
            return json.dumps(response)

        return None
