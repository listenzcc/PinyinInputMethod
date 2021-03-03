'''
Test the speed of worker backend.
'''
import random
from .worker import worker

chars = [chr(ord('a') + j) for j in range(26)]


def generate_random_pinYin(n=3, m=5):
    '''Generate random pinYin fragment with given size range.

    Args:
    - @n: The min length of the generated pinYin, default is 3;
    - @m: The max length of the generated pinYin, default is 5.

    Outs:
    - The generated pinYin fragment.
    '''
    r = random.randint(n, m)
    return ''.join([random.choice(chars) for _ in range(r)])


# Used for valuate the query speed
def query(py):
    return worker.query(py)


# Used for valuate the suggest speed
def suggest(cz):
    return worker.suggest(cz)
